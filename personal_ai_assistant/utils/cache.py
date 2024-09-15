from functools import wraps
from personal_ai_assistant.database.db_manager import DatabaseManager
from personal_ai_assistant.config import settings
import json


class Cache:
    def __init__(self):
        self.db_manager = DatabaseManager(settings.database_url)


def cache(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs)}"
            cached_result = Cache().db_manager.get_cached_data(cache_key)
            if cached_result:
                return cached_result
            result = func(*args, **kwargs)
            Cache().db_manager.cache_data(cache_key, result, expiration)
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    Cache().db_manager.invalidate_cache(pattern)
