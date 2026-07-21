import structlog

from app.ai.providers.base_provider import BaseProvider
from app.core.config import settings

logger = structlog.get_logger()


class OllamaProvider(BaseProvider):
    """Provider local usando Ollama"""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import ollama
                self._client = ollama
            except ImportError:
                return None
        return self._client

    @property
    def name(self) -> str:
        return "ollama"

    def is_available(self) -> bool:
        try:
            client = self._get_client()
            if not client:
                return False
            client.list(host=settings.OLLAMA_URL)
            return True
        except Exception:
            return False

    def chat(self, messages: list[dict], **kwargs) -> str:
        client = self._get_client()
        if not client:
            raise RuntimeError("Ollama client not installed")

        response = client.chat(
            model=settings.OLLAMA_MODEL,
            messages=messages,
            options={
                "num_predict": kwargs.get("max_tokens", settings.AI_MAX_TOKENS),
                "temperature": kwargs.get("temperature", settings.AI_TEMPERATURE),
            },
            host=settings.OLLAMA_URL,
        )
        return response["message"]["content"]
