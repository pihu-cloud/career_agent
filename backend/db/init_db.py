"""
SB1/US1, SB1/US9 - Database Initializer and Default Seeding
"""
from backend.db.database import engine, Base, AsyncSessionLocal
from backend.models.user import User
from backend.auth.security import hash_password
from backend.core.config import settings
from backend.core.logging import logger
from sqlalchemy import select

# Import all models to ensure metadata registration
import backend.models.user
import backend.models.skills
import backend.models.interests
import backend.models.personality
import backend.models.academics
import backend.models.progress
import backend.models.audit
import backend.models.notifications
import backend.models.resume

async def init_db():
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("All database tables created or confirmed.")

    # Seed default administrator if not present
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.email == settings.admin_email)
        res = await session.execute(stmt)
        admin = res.scalar_one_or_none()
        if not admin:
            admin_user = User(
                email=settings.admin_email,
                username="administrator",
                full_name="System Administrator",
                hashed_password=hash_password(settings.admin_password),
                role="admin",
                is_active=True,
                is_verified=True
            )
            session.add(admin_user)
            await session.commit()
            logger.info(f"Default admin account initialized: {settings.admin_email}")
