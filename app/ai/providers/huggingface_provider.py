import structlog

from app.ai.providers.base_provider import BaseProvider
from app.core.config import settings

logger = structlog.get_logger()


class HuggingFaceProvider(BaseProvider):
    """Provider cloud usando HuggingFace Inference API"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not settings.HF_TOKEN:
                return None
            try:
                from huggingface_hub import InferenceClient
                self._client = InferenceClient(token=settings.HF_TOKEN)
            except ImportError:
                return None
        return self._client

    @property
    def name(self) -> str:
        return "huggingface"

    def is_available(self) -> bool:
        return bool(settings.HF_TOKEN) and self._get_client() is not None

    def chat(self, messages: list[dict], **kwargs) -> str:
        client = self._get_client()
        if not client:
            raise RuntimeError("HuggingFace token not configured")

        response = client.chat_completion(
            messages=messages,
            model=settings.HF_MODEL,
            max_tokens=kwargs.get("max_tokens", settings.AI_MAX_TOKENS),
            temperature=kwargs.get("temperature", settings.AI_TEMPERATURE),
        )
        return response.choices[0].message.content
