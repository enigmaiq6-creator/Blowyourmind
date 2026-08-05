import os
import httpx
from typing import Any, Callable, List, Optional

from dotenv import load_dotenv
from google.genai import Client, errors
from pydantic import PrivateAttr
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from tools.common.base_model import BaseModelTool
from tools.common.messenger import Messenger

load_dotenv()


class GeminiUsage(BaseModelTool):
    model: str
    prompt_tokens: Optional[int] = None
    thoughts_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


def _is_daily_quota_exhausted(exc: Exception) -> bool:
    """Returns True if the error is a hard daily quota limit (limit: 0), not a per-minute rate limit."""
    msg = str(exc)
    return "limit: 0" in msg and "GenerateRequestsPerDayPerProjectPerModel" in msg


class GeminiBase(BaseModelTool):
    _clients_info: List[dict] = PrivateAttr(default_factory=list)
    _client_index: int = PrivateAttr(default=0)
    _location: str = PrivateAttr()

    @property
    def client(self) -> Client:
        return self._clients_info[self._client_index]["client"]

    @property
    def is_vertex_client(self) -> bool:
        return self._clients_info[self._client_index]["is_vertex"]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")
        self._location = location
        self._clients_info = []
        self._client_index = 0

        # Collect all API keys: GEMINI_API_KEY, GEMINI_API_KEY_2, GEMINI_API_KEY_3, ...
        api_keys = []
        primary_key = os.getenv("GEMINI_API_KEY")
        if primary_key:
            api_keys.append(primary_key)
        i = 2
        while True:
            extra_key = os.getenv(f"GEMINI_API_KEY_{i}")
            if not extra_key:
                break
            api_keys.append(extra_key)
            i += 1

        for idx, key in enumerate(api_keys):
            self._clients_info.append({
                "client": Client(api_key=key),
                "is_vertex": False
            })
            label = "primaria" if idx == 0 else f"respaldo #{idx}"
            Messenger.info(f"🔑 Clave API {label} cargada (key #{idx + 1}/{len(api_keys)})")

        # Vertex AI as final fallback if no API keys work
        if project_id:
            self._clients_info.append({
                "client": Client(vertexai=True, project=project_id, location=location),
                "is_vertex": True
            })
            Messenger.info(f"☁️  Vertex AI cargado como fallback final (proyecto: {project_id})")

        if not self._clients_info:
            raise RuntimeError("❌ Se requiere GEMINI_API_KEY o GCP_PROJECT_ID")

        Messenger.info(f"✅ Sistema de claves listo: {len(self._clients_info)} cliente(s) disponibles con rotación automática.")

    def _rotate_to_next_client(self) -> bool:
        """Rotates to the next available client. Returns True if rotation succeeded, False if all exhausted."""
        if self._client_index + 1 < len(self._clients_info):
            self._client_index += 1
            label = "Vertex AI" if self.is_vertex_client else f"clave #{self._client_index + 1}"
            Messenger.warning(f"🔄 [KEY ROTATION] Clave #{self._client_index} agotada. Cambiando a {label} (cliente #{self._client_index + 1}/{len(self._clients_info)})...")
            return True
        return False

    @retry(
        wait=wait_exponential(multiplier=2, min=5, max=60),
        stop=stop_after_attempt(7),
        retry=retry_if_exception_type((errors.APIError, httpx.RequestError, httpx.RemoteProtocolError, httpx.HTTPError)),
        before_sleep=lambda retry_state: Messenger.warning(
            f"⏳ [Intento {retry_state.attempt_number}/7] Gemini saturado: "
            f"{type(retry_state.outcome.exception()).__name__}. "
            f"Reintentando en {retry_state.next_action.sleep:.0f}s..."
        ),
        reraise=True,
    )
    def _execute_with_retry(self, method_path: str, *args: Any, **kwargs: Any) -> Any:
        """
        Executes a Gemini API call dynamically resolved on the current client.
        Rotates key on daily quota exhaustion, maps model names for Vertex AI,
        and uses exponential backoff for rate limits.
        """
        # Resolve method from current client
        client_obj = self.client
        obj = client_obj
        for attr in method_path.split('.'):
            obj = getattr(obj, attr)
        func = obj

        # Map model name if using Vertex AI client
        if self.is_vertex_client and 'model' in kwargs:
            original_model = kwargs['model']
            mapping = {
                "gemini-2.0-flash": "gemini-2.5-flash",
                "gemini-2.5-flash": "gemini-2.5-flash",
                "gemini-2.5-flash-preview-tts": "gemini-2.5-flash-tts",
                "gemini-3.1-flash-image-preview": "gemini-2.5-flash-image",
                "veo-3.1-fast-generate-001": "veo-2.0-generate-001",
            }
            kwargs['model'] = mapping.get(original_model, original_model)
            if kwargs['model'] != original_model:
                Messenger.info(f"🔄 [VERTEX MAPPING] mapped model {original_model} -> {kwargs['model']}")

        try:
            return func(*args, **kwargs)
        except errors.ClientError as e:
            # If daily quota is hard-exhausted (limit: 0), rotate to next key immediately
            if _is_daily_quota_exhausted(e):
                if self._rotate_to_next_client():
                    # Retry immediately (re-raise as APIError to trigger tenacity retry, which will resolve new client method)
                    raise errors.APIError(str(e), None)  # type: ignore[arg-type]
                else:
                    Messenger.error("🚫 Todas las claves API han alcanzado su cuota diaria. Reintentando en backoff...")
            raise

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
