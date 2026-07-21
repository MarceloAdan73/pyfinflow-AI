from app.core.cache import (
    cache_get,
    cache_set,
    cache_delete,
    cache_delete_pattern,
    redis_rate_limit_check,
    redis_is_blocked,
    redis_rate_limit_reset,
    MAX_LOGIN_ATTEMPTS,
)


def test_cache_set_get_none_when_redis_unavailable():
    result = cache_set("test_key", {"data": "value"}, ttl=60)
    assert result is False


def test_cache_get_none_when_redis_unavailable():
    result = cache_get("test_key")
    assert result is None


def test_cache_delete_false_when_redis_unavailable():
    result = cache_delete("test_key")
    assert result is False


def test_cache_delete_pattern_false_when_redis_unavailable():
    result = cache_delete_pattern("test:*")
    assert result is False


def test_redis_rate_limit_fallback():
    assert redis_rate_limit_check("test_ip") is True


def test_redis_rate_limit_reset_noop():
    redis_rate_limit_reset("test_ip")


def test_redis_is_blocked_fallback():
    assert redis_is_blocked("test_ip") is False
