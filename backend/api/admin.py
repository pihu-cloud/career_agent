"""
SB1/US12, SB1/US37 - Role-Based Administrative Control Center
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any

from backend.db.database import get_db
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.audit import AuditLog
from backend.schemas.user import UserResponse
from backend.auth.rbac import require_admin

router = APIRouter(prefix="/api/v1/admin", tags=["Administrator Console"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_admin_system_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    active_users = (await db.execute(select(func.count(User.id)).where(User.is_active == True))).scalar() or 0
    total_resumes = (await db.execute(select(func.count(Resume.id)))).scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "total_resumes_uploaded": total_resumes
    }

@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    return (await db.execute(stmt)).scalars().all()

@router.put("/users/{user_id}/status")
async def toggle_user_active_status(
    user_id: str,
    status_payload: Dict[str, bool],
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.id == user_id)
    target_user = (await db.execute(stmt)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found.")

    target_user.is_active = status_payload.get("is_active", True)
    await db.commit()
    return {"message": f"User status updated to {'active' if target_user.is_active else 'inactive'}."}

@router.get("/audit-logs")
async def get_audit_trail(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    logs = (await db.execute(stmt)).scalars().all()
    return logs
