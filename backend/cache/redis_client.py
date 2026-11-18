"""
SB1/US29 - Redis caching layer with robust in-memory fallback
"""
import time
import json
from typing import Any, Optional
from backend.core.logging import logger
from backend.core.config import settings

class CacheClient:
    def __init__(self):
        self._memory_cache = {}
        self._redis = None
        self._is_redis_available = False
        self._init_redis()

    def _init_redis(self):
        try:
            import redis
            self._redis = redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=1.0)
            self._redis.ping()
            self._is_redis_available = True
            logger.info("Connected to Redis cache server successfully.")
        except Exception as e:
            self._is_redis_available = False
            logger.info(f"Redis not available ({e}). Using thread-safe in-memory cache as fallback.")

    def get(self, key: str) -> Optional[Any]:
        if self._is_redis_available and self._redis:
            try:
                val = self._redis.get(key)
                if val is not None:
                    try:
                        return json.loads(val)
                    except Exception:
                        return val
            except Exception as e:
                logger.warning(f"Redis get failed ({e}), falling back to memory.")
        
        # In-memory lookup
        item = self._memory_cache.get(key)
        if item is not None:
            val, expire_at = item
            if expire_at is None or expire_at > time.time():
                return val
            else:
                del self._memory_cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if self._is_redis_available and self._redis:
            try:
                dumped = json.dumps(value) if not isinstance(value, str) else value
                self._redis.set(key, dumped, ex=ttl)
                return True
            except Exception as e:
                logger.warning(f"Redis set failed ({e}), using memory.")

        expire_at = time.time() + ttl if ttl else None
        self._memory_cache[key] = (value, expire_at)
        return True

    def delete(self, key: str) -> bool:
        deleted = False
        if self._is_redis_available and self._redis:
            try:
                self._redis.delete(key)
                deleted = True
            except Exception:
                pass
        if key in self._memory_cache:
            del self._memory_cache[key]
            deleted = True
        return deleted

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

cache = CacheClient()
