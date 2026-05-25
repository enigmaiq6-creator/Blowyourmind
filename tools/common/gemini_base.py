import os
import httpx
from typing import Any, Callable, Optional

from dotenv import load_dotenv
from google.genai import Client, errors
from pydantic import PrivateAttr
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger

load_dotenv()


class GeminiUsage(BaseModelTool):
    model: str
    prompt_tokens: Optional[int] = None
    thoughts_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class GeminiBase(BaseModelTool):
    _client: Client = PrivateAttr()
    _location: str = PrivateAttr()

    @property
    def client(self) -> Client:
        return self._client

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")
        self._location = location
        api_key = os.getenv("GEMINI_API_KEY")

        if project_id:
            Messenger.info(f"✨ Using Vertex AI (Enterprise) for Gemini in project: {project_id}...")
            self._client = Client(
                vertexai=True,
                project=project_id,
                location=location,
                http_options={"timeout": 300}
            )
        else:
            Messenger.info("🔧 Using Google AI Studio (API Key) for Gemini...")
            if not api_key:
                raise RuntimeError("❌ GEMINI_API_KEY or GCP_PROJECT_ID is required")
            self._client = Client(api_key=api_key, http_options={"timeout": 300})

    @retry(
        wait=wait_fixed(60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type((errors.ServerError, errors.ClientError, httpx.RequestError, httpx.RemoteProtocolError, httpx.HTTPError, httpx.TimeoutException, TimeoutError)),
        before_sleep=lambda retry_state: Messenger.info(
            f"⏳ Gemini bloqueado (Saturación o Error de Red). Reintentando en 60s... "
            f"(Intento {retry_state.attempt_number}/5)"
        ),
        reraise=True,
    )
    def _execute_with_retry(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Executes a Gemini API call with a 60s retry on ServerError or ClientError (429).
        Timeout is set to 90s per request to prevent infinite hangs.
        """
        return func(*args, **kwargs)

    def _extract_usage(self, response: Any, model_name: str) -> GeminiUsage:
        usage_meta = getattr(response, "usage_metadata", None)
        usage = GeminiUsage(model=model_name)

        if usage_meta:
            usage.prompt_tokens = getattr(usage_meta, "prompt_token_count", None)
            usage.thoughts_tokens = getattr(usage_meta, "thoughts_token_count", None)
            usage.output_tokens = getattr(usage_meta, "candidates_token_count", None)
            usage.total_tokens = getattr(usage_meta, "total_token_count", None)

        if usage.total_tokens is not None:
            Messenger.usage(
                model=usage.model,
                prompt=usage.prompt_tokens or 0,
                thoughts=usage.thoughts_tokens or 0,
                output=usage.output_tokens or 0,
                total=usage.total_tokens
            )
        return usage
