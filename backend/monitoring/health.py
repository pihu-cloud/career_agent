"""
SB1/US41, SB1/US45 - System Health Monitoring and Diagnostic Service
"""
import time
from sqlalchemy import text
from backend.db.database import AsyncSessionLocal
from backend.cache.redis_client import cache
from backend.core.config import settings

class HealthChecker:
    def __init__(self):
        self.start_time = time.time()

    async def check_database(self) -> dict:
        t0 = time.time()
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            latency_ms = round((time.time() - t0) * 1000, 2)
            return {"status": "healthy", "latency_ms": latency_ms}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def check_cache(self) -> dict:
        t0 = time.time()
        try:
            cache.set("__health_check__", "ok", ttl=10)
            val = cache.get("__health_check__")
            latency_ms = round((time.time() - t0) * 1000, 2)
            is_redis = cache._is_redis_available
            return {
                "status": "healthy" if val == "ok" else "degraded",
                "backend": "redis" if is_redis else "in-memory-fallback",
                "latency_ms": latency_ms
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def get_uptime_seconds(self) -> float:
        return round(time.time() - self.start_time, 2)

    async def get_system_health(self) -> dict:
        db_res = await self.check_database()
        cache_res = self.check_cache()
        overall = "healthy" if db_res["status"] == "healthy" else "unhealthy"

        return {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "status": overall,
            "uptime_seconds": self.get_uptime_seconds(),
            "environment": settings.app_env,
            "services": {
                "database": db_res,
                "cache": cache_res
            }
        }

health_checker = HealthChecker()
