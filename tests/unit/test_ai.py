from unittest.mock import MagicMock, patch

import pytest

from app.ai.analytics import FinancialAnalytics
from app.ai.chat_memory import ChatMemoryService
from app.ai.provider_factory import ProviderFactory, _local_fallback
from app.ai.providers.base_provider import BaseProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.huggingface_provider import HuggingFaceProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.core.config import settings

# ============================
# BASE PROVIDER
# ============================

def test_base_provider_is_abstract():
    with pytest.raises(TypeError):
        BaseProvider()


# ============================
# OLLAMA PROVIDER
# ============================

def test_ollama_provider_name():
    p = OllamaProvider()
    assert p.name == "ollama"


@patch("app.ai.providers.ollama_provider.OllamaProvider._get_client")
def test_ollama_provider_not_available_without_client(mock_get):
    mock_get.return_value = None
    p = OllamaProvider()
    assert p.is_available() is False


@patch("app.ai.providers.ollama_provider.OllamaProvider._get_client")
def test_ollama_provider_available_with_client(mock_get):
    mock_client = MagicMock()
    mock_get.return_value = mock_client
    p = OllamaProvider()
    assert p.is_available() is True


# ============================
# HUGGINGFACE PROVIDER
# ============================

def test_huggingface_provider_name():
    p = HuggingFaceProvider()
    assert p.name == "huggingface"


def test_huggingface_not_available_without_token():
    with patch.object(settings, "HF_TOKEN", ""):
        p = HuggingFaceProvider()
        assert p.is_available() is False


# ============================
# GEMINI PROVIDER
# ============================

def test_gemini_provider_name():
    p = GeminiProvider()
    assert p.name == "gemini"


def test_gemini_not_available_without_key():
    with patch.object(settings, "GEMINI_API_KEY", ""):
        p = GeminiProvider()
        assert p.is_available() is False


# ============================
# LOCAL FALLBACK
# ============================

def test_local_fallback_empty():
    response = _local_fallback([])
    assert "procesar" in response.lower() or "pregunta" in response.lower()


def test_local_fallback_saldo():
    messages = [{"role": "user", "content": "¿Cuál es mi saldo?"}]
    response = _local_fallback(messages)
    assert "saldo" in response.lower() or "dashboard" in response.lower()


def test_local_fallback_gastos():
    messages = [{"role": "user", "content": "¿Cuánto gasté?"}]
    response = _local_fallback(messages)
    assert "gasto" in response.lower() or "historial" in response.lower()


def test_local_fallback_ingresos():
    messages = [{"role": "user", "content": "Muéstrame mis ingresos"}]
    response = _local_fallback(messages)
    assert "ingreso" in response.lower()


def test_local_fallback_ahorro():
    messages = [{"role": "user", "content": "Quiero ahorrar"}]
    response = _local_fallback(messages)
    assert "ahorro" in response.lower() or "meta" in response.lower()


def test_local_fallback_presupuesto():
    messages = [{"role": "user", "content": "Háblame de presupuestos"}]
    response = _local_fallback(messages)
    assert "presupuesto" in response.lower()


def test_local_fallback_generic():
    messages = [{"role": "user", "content": "blablabla"}]
    response = _local_fallback(messages)
    assert "finanzas" in response.lower() or "ayudar" in response.lower()


# ============================
# PROVIDER FACTORY
# ============================

def test_provider_factory_builds_chain():
    factory = ProviderFactory()
    assert len(factory.providers) > 0


def test_provider_factory_names():
    factory = ProviderFactory()
    names = [p.name for p in factory.providers]
    assert "ollama" in names or "huggingface" in names or "gemini" in names


@patch("app.ai.provider_factory.ProviderFactory._build_chain")
def test_provider_factory_chat_fallback_to_local(mock_build):
    mock_build.return_value = []
    factory = ProviderFactory()
    response, provider = factory.chat([{"role": "user", "content": "test"}])
    assert provider == "local_rules"
    assert len(response) > 0


# ============================
# ANALYTICS
# ============================

def test_analytics_tendencias_empty():
    analytics = FinancialAnalytics()
    result = analytics.analizar_tendencias([])
    assert result == {}


def test_analytics_tendencias_basic():
    analytics = FinancialAnalytics()
    txns = [
        {"tipo": "Gasto", "monto": 1000, "categoria": "Comida", "fecha": "2026-01-15"},
        {"tipo": "Gasto", "monto": 1200, "categoria": "Comida", "fecha": "2026-02-15"},
        {"tipo": "Gasto", "monto": 1500, "categoria": "Comida", "fecha": "2026-03-15"},
    ]
    result = analytics.analizar_tendencias(txns)
    assert "Comida" in result
    assert result["Comida"]["trend"] == "up"
    assert result["Comida"]["change_pct"] > 0


def test_analytics_prediccion_empty():
    analytics = FinancialAnalytics()
    result = analytics.predecir_gasto_mensual([])
    assert result["prediccion"] == 0
    assert result["confianza"] == 0.0


def test_analytics_prediccion_with_data():
    analytics = FinancialAnalytics()
    txns = [
        {"tipo": "Gasto", "monto": 100000, "categoria": "Comida", "fecha": "2026-01-15"},
        {"tipo": "Gasto", "monto": 110000, "categoria": "Comida", "fecha": "2026-02-15"},
        {"tipo": "Gasto", "monto": 120000, "categoria": "Comida", "fecha": "2026-03-15"},
    ]
    result = analytics.predecir_gasto_mensual(txns)
    assert result["prediccion"] > 0
    assert result["confianza"] > 0


def test_analytics_anomalias_none():
    analytics = FinancialAnalytics()
    txns = [
        {"tipo": "Gasto", "monto": 100, "categoria": "Comida", "fecha": "2026-01-01"},
        {"tipo": "Gasto", "monto": 100, "categoria": "Comida", "fecha": "2026-01-02"},
        {"tipo": "Gasto", "monto": 100, "categoria": "Comida", "fecha": "2026-01-03"},
    ]
    result = analytics.detectar_anomalias(txns)
    assert len(result) == 0


def test_analytics_anomalias_detected():
    analytics = FinancialAnalytics()
    txns = [
        {"tipo": "Gasto", "monto": 100, "categoria": "Comida", "fecha": "2026-01-01", "id": "t1"},
        {"tipo": "Gasto", "monto": 110, "categoria": "Comida", "fecha": "2026-01-02", "id": "t2"},
        {"tipo": "Gasto", "monto": 90, "categoria": "Comida", "fecha": "2026-01-03", "id": "t3"},
        {"tipo": "Gasto", "monto": 105, "categoria": "Comida", "fecha": "2026-01-04", "id": "t4"},
        {"tipo": "Gasto", "monto": 95, "categoria": "Comida", "fecha": "2026-01-05", "id": "t5"},
        {"tipo": "Gasto", "monto": 10000, "categoria": "Comida", "fecha": "2026-01-06", "id": "t6"},
    ]
    result = analytics.detectar_anomalias(txns)
    assert len(result) > 0
    assert result[0]["id"] == "t6"
    assert result[0]["z_score"] > 2


def test_analytics_insights_empty():
    analytics = FinancialAnalytics()
    result = analytics.generar_insights([])
    assert len(result) > 0


def test_analytics_insights_with_data():
    analytics = FinancialAnalytics()
    txns = [
        {"tipo": "Ingreso", "monto": 200000, "categoria": "Salario", "fecha": "2026-01-15"},
        {"tipo": "Gasto", "monto": 50000, "categoria": "Comida", "fecha": "2026-01-20"},
        {"tipo": "Gasto", "monto": 30000, "categoria": "Transporte", "fecha": "2026-01-21"},
    ]
    result = analytics.generar_insights(txns)
    assert len(result) > 0


# ============================
# CHAT MEMORY
# ============================

class FakeChatRepo:
    def __init__(self):
        self.messages = []

    def create(self, data):
        msg = {"id": f"chat_{len(self.messages)}", **data}
        self.messages.append(msg)
        return msg

    def get_history(self, user_id, limit=20):
        user_msgs = [m for m in self.messages if m["user_id"] == user_id]
        return user_msgs[-limit:]

    def clear_history(self, user_id):
        before = len(self.messages)
        self.messages = [m for m in self.messages if m["user_id"] != user_id]
        return before - len(self.messages)


def test_chat_memory_save():
    repo = FakeChatRepo()
    memory = ChatMemoryService(repo)
    msg = memory.guardar_mensaje("user1", "user", "Hola")
    assert msg["role"] == "user"
    assert msg["content"] == "Hola"


def test_chat_memory_load():
    repo = FakeChatRepo()
    memory = ChatMemoryService(repo)
    memory.guardar_mensaje("user1", "user", "Hola")
    memory.guardar_mensaje("user1", "assistant", "Hola! Cómo estás?")
    history = memory.cargar_historial("user1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_chat_memory_clear():
    repo = FakeChatRepo()
    memory = ChatMemoryService(repo)
    memory.guardar_mensaje("user1", "user", "test")
    count = memory.limpiar_historial("user1")
    assert count == 1
    assert len(memory.cargar_historial("user1")) == 0


def test_chat_memory_context():
    repo = FakeChatRepo()
    memory = ChatMemoryService(repo)
    memory.guardar_mensaje("user1", "user", "Hola")
    memory.guardar_mensaje("user1", "assistant", "Hi!")
    ctx = memory.construir_contexto_conversacion("user1")
    assert len(ctx) == 2
    assert ctx[0]["role"] == "user"
    assert ctx[1]["role"] == "assistant"


# ============================
# RATE LIMITER IA
# ============================

def test_rate_limiter_permite_bajo_el_limite():
    from app.ai.rate_limiter import check_ai_rate_limit, reset_ai_rate_limit

    reset_ai_rate_limit("rl_user")
    results = [check_ai_rate_limit("rl_user") for _ in range(10)]
    assert all(results)
    reset_ai_rate_limit("rl_user")


def test_rate_limiter_bloquea_despues_del_limite():
    from app.ai.rate_limiter import AI_RATE_LIMIT, check_ai_rate_limit, reset_ai_rate_limit

    reset_ai_rate_limit("rl_user2")
    for _ in range(AI_RATE_LIMIT):
        assert check_ai_rate_limit("rl_user2") is True
    assert check_ai_rate_limit("rl_user2") is False
    assert check_ai_rate_limit("rl_user2") is False
    reset_ai_rate_limit("rl_user2")


def test_rate_limiter_usuarios_independientes():
    from app.ai.rate_limiter import AI_RATE_LIMIT, check_ai_rate_limit, reset_ai_rate_limit

    reset_ai_rate_limit("u_a")
    reset_ai_rate_limit("u_b")
    for _ in range(AI_RATE_LIMIT):
        check_ai_rate_limit("u_a")
    assert check_ai_rate_limit("u_a") is False
    assert check_ai_rate_limit("u_b") is True
    reset_ai_rate_limit("u_a")
    reset_ai_rate_limit("u_b")


def test_rate_limiter_reset():
    from app.ai.rate_limiter import AI_RATE_LIMIT, check_ai_rate_limit, reset_ai_rate_limit

    reset_ai_rate_limit("u_c")
    for _ in range(AI_RATE_LIMIT):
        check_ai_rate_limit("u_c")
    assert check_ai_rate_limit("u_c") is False
    reset_ai_rate_limit("u_c")
    assert check_ai_rate_limit("u_c") is True
    reset_ai_rate_limit("u_c")
