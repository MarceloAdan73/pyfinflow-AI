import json
import time
import structlog

from app.ai.vector_store import ChromaDBStore
from app.ai.provider_factory import ProviderFactory
from app.core.config import settings
from app.core.metrics import metrics_collector

logger = structlog.get_logger()

SYSTEM_PROMPT = (
    "Eres un asesor financiero experto, amigable y práctico. "
    "Respondes en español de manera clara y concisa. "
    "Usas los datos financieros del usuario para dar respuestas personalizadas."
)


class RAGEngine:
    """Pipeline RAG: query → buscar contexto → construir prompt → LLM"""

    def __init__(
        self,
        vector_store: ChromaDBStore = None,
        provider_factory: ProviderFactory = None,
    ):
        self.vector_store = vector_store or ChromaDBStore()
        self.provider_factory = provider_factory or ProviderFactory()

    def consultar(
        self, user_id: str, pregunta: str, contexto_financiero: dict
    ) -> dict:
        start = time.time()

        transacciones_relevantes = self.vector_store.buscar_contexto(
            user_id, pregunta, top_k=5
        )

        messages = self._build_messages(
            pregunta, contexto_financiero, transacciones_relevantes
        )

        respuesta, provider_name = self.provider_factory.chat(messages)

        latency_ms = round((time.time() - start) * 1000, 2)
        metrics_collector.record_ai_latency(latency_ms)

        logger.info(
            "ai_consultation",
            user_id=user_id,
            provider=provider_name,
            latency_ms=latency_ms,
            context_results=len(transacciones_relevantes),
        )

        return {
            "respuesta": respuesta,
            "provider": provider_name,
            "contexto_usado": len(transacciones_relevantes),
            "latency_ms": latency_ms,
        }

    def _build_messages(
        self,
        pregunta: str,
        contexto_financiero: dict,
        transacciones_relevantes: list[dict],
    ) -> list[dict]:
        context_parts = []

        context_parts.append(
            f"Resumen financiero:\n"
            f"- Ingresos: ${contexto_financiero.get('ingresos', 0):,.2f}\n"
            f"- Gastos: ${contexto_financiero.get('gastos', 0):,.2f}\n"
            f"- Balance: ${contexto_financiero.get('balance', 0):,.2f}\n"
            f"- Categoría con más gastos: {contexto_financiero.get('top_categoria', 'N/A')}\n"
            f"- Total de transacciones: {contexto_financiero.get('total_transacciones', 0)}"
        )

        if transacciones_relevantes:
            txns_text = "\n".join(
                f"  - {t['texto']} (relevancia: {t['relevancia']})"
                for t in transacciones_relevantes
            )
            context_parts.append(
                f"Transacciones relevantes para la pregunta:\n{txns_text}"
            )

        user_content = (
            f"Contexto financiero del usuario:\n"
            f"{chr(10).join(context_parts)}\n\n"
            f"Pregunta del usuario: {pregunta}\n\n"
            f"Responde de manera útil, breve y en español."
        )

        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
