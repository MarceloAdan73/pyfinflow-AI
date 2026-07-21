import json
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class ChatMemoryService:
    """Servicio de memoria de conversación persistente en PostgreSQL"""

    def __init__(self, chat_repo):
        self.chat_repo = chat_repo

    def guardar_mensaje(
        self,
        user_id: str,
        role: str,
        content: str,
        provider: str = None,
        context: dict = None,
        tokens_used: int = 0,
    ) -> dict:
        data = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "provider": provider,
            "context_used": json.dumps(context) if context else None,
            "tokens_used": tokens_used,
        }
        return self.chat_repo.create(data)

    def cargar_historial(self, user_id: str, limit: int = None) -> list[dict]:
        limit = limit or settings.AI_CONTEXT_WINDOW
        return self.chat_repo.get_history(user_id, limit=limit)

    def limpiar_historial(self, user_id: str) -> int:
        return self.chat_repo.clear_history(user_id)

    def construir_contexto_conversacion(self, user_id: str) -> list[dict]:
        mensajes = self.cargar_historial(user_id)
        messages = []
        for msg in mensajes:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })
        return messages
