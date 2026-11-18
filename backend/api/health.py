"""
SB1/US41, SB1/US45 - System Health and Operational Status Endpoints
"""
from fastapi import APIRouter
from backend.monitoring.health import health_checker
from backend.core.config import settings

router = APIRouter(prefix="/api/v1/health", tags=["Health & Monitoring"])

@router.get("")
async def get_health_status():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "uptime": health_checker.get_uptime_seconds()
    }

@router.get("/detailed")
async def get_detailed_health():
    return await health_checker.get_system_health()
