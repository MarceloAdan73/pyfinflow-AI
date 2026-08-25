"""Rate limiting para llamadas a la IA (por usuario, ventana deslizante)."""

import time
from typing import Dict, List

from app.core.config import settings

AI_RATE_LIMIT = settings.AI_RATE_LIMIT_PER_MIN
AI_RATE_WINDOW = 60

_ai_calls: Dict[str, List[float]] = {}


def check_ai_rate_limit(user_id: str) -> bool:
    """Registra una llamada IA del usuario. Retorna False si excede el límite."""
    now = time.time()
    calls = [t for t in _ai_calls.get(user_id, []) if now - t < AI_RATE_WINDOW]
    if len(calls) >= AI_RATE_LIMIT:
        _ai_calls[user_id] = calls
        return False
    calls.append(now)
    _ai_calls[user_id] = calls
    return True


def reset_ai_rate_limit(user_id: str):
    """Limpia el contador de un usuario (útil para tests y soporte)."""
    _ai_calls.pop(user_id, None)
