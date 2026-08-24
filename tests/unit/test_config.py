from app.core.config import Settings

# ============================
# Settings defaults (class attrs evaluated at import time, .env may override)
# ============================

def test_settings_has_database_url():
    s = Settings()
    assert isinstance(s.DATABASE_URL, str)
    assert len(s.DATABASE_URL) > 0


def test_settings_has_redis_url():
    s = Settings()
    assert isinstance(s.REDIS_URL, str)
    assert "redis" in s.REDIS_URL


def test_settings_has_jwt_secret():
    s = Settings()
    assert isinstance(s.JWT_SECRET, str)
    assert len(s.JWT_SECRET) > 0


def test_settings_environment_default():
    s = Settings()
    assert s.ENVIRONMENT in ("development", "production", "testing")


def test_settings_smtp_port_is_int():
    s = Settings()
    assert isinstance(s.SMTP_PORT, int)
    assert s.SMTP_PORT > 0


def test_settings_smtp_tls_is_bool():
    s = Settings()
    assert isinstance(s.SMTP_TLS, bool)


def test_settings_has_ollama_url():
    s = Settings()
    assert isinstance(s.OLLAMA_URL, str)


def test_settings_ai_max_tokens_is_int():
    s = Settings()
    assert isinstance(s.AI_MAX_TOKENS, int)
    assert s.AI_MAX_TOKENS > 0


def test_settings_ai_temperature_is_float():
    s = Settings()
    assert isinstance(s.AI_TEMPERATURE, float)
    assert 0.0 <= s.AI_TEMPERATURE <= 2.0


def test_settings_ai_context_window_is_int():
    s = Settings()
    assert isinstance(s.AI_CONTEXT_WINDOW, int)
    assert s.AI_CONTEXT_WINDOW > 0


def test_settings_engine_options():
    s = Settings()
    assert s.SQLALCHEMY_ENGINE_OPTIONS["pool_pre_ping"] is True
    assert s.SQLALCHEMY_ENGINE_OPTIONS["pool_size"] == 5
    assert s.SQLALCHEMY_ENGINE_OPTIONS["max_overflow"] == 10
