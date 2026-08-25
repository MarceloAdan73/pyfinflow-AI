import structlog

from app.ai.providers.base_provider import BaseProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.huggingface_provider import HuggingFaceProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.core.config import settings

logger = structlog.get_logger()

PROVIDER_MAP = {
    "ollama": OllamaProvider,
    "huggingface": HuggingFaceProvider,
    "gemini": GeminiProvider,
}


def _local_fallback(messages: list[dict]) -> str:
    """Fallback 100% local con keyword matching (sin LLM)"""
    pregunta = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            pregunta = msg["content"].lower()
            break

    if not pregunta:
        return "No pude procesar tu pregunta. Intenta reformularla."

    keywords_response = {
        "saldo": "Para ver tu saldo, revisa el dashboard principal donde se muestra el balance de ingresos y gastos.",
        "balance": "Para ver tu saldo, revisa el dashboard principal donde se muestra el balance de ingresos y gastos.",
        "gasto": "Tus gastos se muestran en el dashboard y en la sección de historial. Puedes filtrar por categoría y fecha.",
        "gastos": "Tus gastos se muestran en el dashboard y en la sección de historial. Puedes filtrar por categoría y fecha.",
        "ahorrar": "Para ahorrar, revisa tus metas de ahorro en la sección de metas. Puedes establecer objetivos mensuales.",
        "ahorro": "Para ahorrar, revisa tus metas de ahorro en la sección de metas. Puedes establecer objetivos mensuales.",
        "ingreso": "Tus ingresos se registran como transacciones de tipo 'Ingreso'. Revisa el historial para ver todos.",
        "ingresos": "Tus ingresos se registran como transacciones de tipo 'Ingreso'. Revisa el historial para ver todos.",
        "presupuesto": "Puedes configurar presupuestos por categoría en la sección de presupuestos del dashboard.",
        "presupuestos": "Puedes configurar presupuestos por categoría en la sección de presupuestos del dashboard.",
        "meta": "Las metas de ahorro te ayudan a planificar. Puedes crearlas y seguir tu progreso.",
        "metas": "Las metas de ahorro te ayudan a planificar. Puedes crearlas y seguir tu progreso.",
    }

    for keyword, response in keywords_response.items():
        if keyword in pregunta:
            return response

    return (
        "Puedo ayudarte con información sobre tus finanzas. "
        "Pregúntame por tu saldo, gastos, ingresos, presupuestos o metas de ahorro."
    )


class ProviderFactory:
    """Factory con fallback chain: Ollama → HuggingFace → Gemini → local rules"""

    def __init__(self):
        self.providers = self._build_chain()

    def _build_chain(self) -> list[BaseProvider]:
        priority = [p.strip() for p in settings.AI_PROVIDER_PRIORITY.split(",")]
        providers = []
        for name in priority:
            cls = PROVIDER_MAP.get(name)
            if cls:
                providers.append(cls())
        return providers

    def chat(self, messages: list[dict]) -> tuple[str, str]:
        """Retorna (respuesta, provider_name)"""
        for provider in self.providers:
            if provider.is_available():
                try:
                    response = provider.chat(messages)
                    if not response or not response.strip():
                        raise ValueError("empty response from provider")
                    logger.info("ai_provider_success", provider=provider.name)
                    return response, provider.name
                except Exception as e:
                    logger.warning(
                        "ai_provider_failed",
                        provider=provider.name,
                        error=str(e),
                    )
                    continue

        logger.info("ai_using_local_fallback")
        return _local_fallback(messages), "local_rules"
