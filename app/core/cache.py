import json
from typing import Any, Optional

import structlog
from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = structlog.get_logger()

_redis_client: Optional[Redis] = None


def get_redis() -> Optional[Redis]:
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            _redis_client.ping()
            logger.info("redis_connected")
        except RedisError:
            logger.warning("redis_unavailable", url=settings.REDIS_URL)
            _redis_client = None
    return _redis_client


def cache_get(key: str) -> Optional[Any]:
    client = get_redis()
    if not client:
        return None
    try:
        data = client.get(key)
        if data:
            return json.loads(data)
    except RedisError:
        logger.warning("cache_get_error", key=key)
    return None


def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    client = get_redis()
    if not client:
        return False
    try:
        client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except RedisError:
        logger.warning("cache_set_error", key=key)
    return False


def cache_delete(key: str) -> bool:
    client = get_redis()
    if not client:
        return False
    try:
        client.delete(key)
        return True
    except RedisError:
        logger.warning("cache_delete_error", key=key)
    return False


def cache_delete_pattern(pattern: str) -> bool:
    client = get_redis()
    if not client:
        return False
    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
        return True
    except RedisError:
        logger.warning("cache_delete_pattern_error", pattern=pattern)
    return False


# --- Session caching ---

def cache_user_session(user_id: str, data: dict, ttl: int = 3600):
    return cache_set(f"session:{user_id}", data, ttl)


def get_user_session(user_id: str) -> Optional[dict]:
    return cache_get(f"session:{user_id}")


def invalidate_user_session(user_id: str):
    return cache_delete(f"session:{user_id}")


# --- Query caching ---

def cache_query_result(user_id: str, query_key: str, data: Any, ttl: int = 300):
    return cache_set(f"query:{user_id}:{query_key}", data, ttl)


def get_cached_query(user_id: str, query_key: str) -> Optional[Any]:
    return cache_get(f"query:{user_id}:{query_key}")


def invalidate_user_queries(user_id: str):
    return cache_delete_pattern(f"query:{user_id}:*")


# --- Rate limiting with Redis ---

MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW = 60


def redis_rate_limit_check(ip: str) -> bool:
    client = get_redis()
    if not client:
        return True
    try:
        key = f"ratelimit:login:{ip}"
        current = client.get(key)
        if current and int(current) >= MAX_LOGIN_ATTEMPTS:
            return False
        client.incr(key, 1)
        client.expire(key, LOGIN_WINDOW)
        return True
    except RedisError:
        return True


def redis_rate_limit_reset(ip: str):
    client = get_redis()
    if not client:
        return
    try:
        client.delete(f"ratelimit:login:{ip}")
    except RedisError:
        pass


def redis_is_blocked(ip: str) -> bool:
    client = get_redis()
    if not client:
        return False
    try:
        key = f"ratelimit:login:{ip}"
        current = client.get(key)
        return current is not None and int(current) >= MAX_LOGIN_ATTEMPTS
    except RedisError:
        return False
