"""
SB1/US32 - In-App Notifications API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from backend.db.database import get_db
from backend.models.user import User
from backend.schemas.notifications import NotificationResponse
from backend.auth.jwt import get_current_user
from backend.services.notifications import notification_service

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

@router.get("", response_model=Dict[str, Any])
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    notifs = await notification_service.get_user_notifications(db, current_user.id)
    unread = await notification_service.get_unread_count(db, current_user.id)
    return {
        "notifications": notifs,
        "unread_count": unread
    }

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    success = await notification_service.mark_as_read(db, notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"message": "Notification marked as read."}

@router.put("/read-all")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    count = await notification_service.mark_all_as_read(db, current_user.id)
    return {"message": f"Marked {count} notifications as read."}
