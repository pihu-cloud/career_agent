"""
SB1/US32 - In-app Notifications Service for Student Milestones & System Alerts
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.models.notifications import Notification

class NotificationService:
    async def create_notification(
        self,
        db: AsyncSession,
        user_id: str,
        title: str,
        message: str,
        type: str = "milestone"
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            is_read=False
        )
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        return notif

    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> List[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_unread_count(self, db: AsyncSession, user_id: str) -> int:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        res = await db.execute(stmt)
        return len(res.scalars().all())

    async def mark_as_read(self, db: AsyncSession, notification_id: str, user_id: str) -> bool:
        stmt = (
            update(Notification)
            .where(Notification.id == notification_id, Notification.user_id == user_id)
            .values(is_read=True)
        )
        res = await db.execute(stmt)
        await db.commit()
        return res.rowcount > 0

    async def mark_all_as_read(self, db: AsyncSession, user_id: str) -> int:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
        )
        res = await db.execute(stmt)
        await db.commit()
        return res.rowcount

notification_service = NotificationService()
