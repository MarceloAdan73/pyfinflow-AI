import structlog

from app.ai.providers.base_provider import BaseProvider
from app.core.config import settings

logger = structlog.get_logger()


class GeminiProvider(BaseProvider):
    """Provider cloud usando Google Gemini"""

    def __init__(self):
        self._genai = None

    def _get_genai(self):
        if self._genai is None:
            if not settings.GEMINI_API_KEY:
                return None
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._genai = genai
            except ImportError:
                return None
        return self._genai

    @property
    def name(self) -> str:
        return "gemini"

    def is_available(self) -> bool:
        return bool(settings.GEMINI_API_KEY) and self._get_genai() is not None

    def chat(self, messages: list[dict], **kwargs) -> str:
        genai = self._get_genai()
        if not genai:
            raise RuntimeError("Gemini API key not configured")

        model = genai.GenerativeModel(settings.GEMINI_MODEL)

        history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=history[:-1] if len(history) > 1 else [])
        response = chat.send_message(
            messages[-1]["content"],
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=kwargs.get("max_tokens", settings.AI_MAX_TOKENS),
                temperature=kwargs.get("temperature", settings.AI_TEMPERATURE),
            ),
        )
        return response.text
