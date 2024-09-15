import redis
import json
from functools import wraps
from personal_ai_assistant.config import settings

redis_client = redis.Redis.from_url(settings.redis_url)

def cache_key(*args, **kwargs):
    """Generate a cache key based on the function arguments."""
    key = ":".join(str(arg) for arg in args)
    key += ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return key

def cache(expire=3600):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            cached_result = redis_client.get(key)
            if cached_result:
                return json.loads(cached_result)
            result = await func(*args, **kwargs)
            redis_client.setex(key, expire, json.dumps(result))
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern):
    """Invalidate cache entries matching the given pattern."""
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)
