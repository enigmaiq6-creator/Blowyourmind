import os
import httpx
from typing import Any, Callable, Optional

from dotenv import load_dotenv
from google.genai import Client, errors, types
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
    _api_key: Optional[str] = PrivateAttr(default=None)
    _project_id: Optional[str] = PrivateAttr(default=None)
    _using_vertex: bool = PrivateAttr(default=False)

    @property
    def client(self) -> Client:
        return self._client

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")
        self._location = location
        self._api_key = os.getenv("GEMINI_API_KEY")
        self._project_id = project_id
        self._using_vertex = False

        if self._api_key:
            Messenger.info("🔧 Using Google AI Studio (API Key) for Gemini...")
            self._client = Client(api_key=self._api_key, http_options=types.HttpOptions(timeout=300000))
        elif self._project_id:
            Messenger.info(f"✨ Using Vertex AI (Enterprise) for Gemini in project: {self._project_id}...")
            self._client = Client(
                vertexai=True,
                project=self._project_id,
                location=location,
                http_options=types.HttpOptions(timeout=300000)
            )
            self._using_vertex = True
        else:
            raise RuntimeError("❌ GEMINI_API_KEY or GCP_PROJECT_ID is required")

    @retry(
        wait=wait_fixed(90),
        stop=stop_after_attempt(8),
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
        If API Key limits are exhausted and GCP Project ID is available, falls back to Vertex AI.
        """
        # Resolve method from current client to avoid stale bindings after client switch
        method_name = getattr(func, "__name__", "generate_content")
        current_method = getattr(self._client.models, method_name, func)
        try:
            return current_method(*args, **kwargs)
        except errors.ClientError as e:
            error_str = str(e)
            if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str) and self._project_id and not self._using_vertex:
                Messenger.warning("⚠️ Gemini API Key rate limit/quota exhausted (429 RESOURCE_EXHAUSTED). Falling back to Vertex AI...")
                self._using_vertex = True
                self._client = Client(
                    vertexai=True,
                    project=self._project_id,
                    location=self._location,
                    http_options=types.HttpOptions(timeout=300000)
                )
                # Call with the new Vertex AI client; if this ALSO fails, @retry will
                # retry and re-resolve current_method from self._client (now Vertex AI)
                return getattr(self._client.models, method_name)(*args, **kwargs)
            raise e

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
