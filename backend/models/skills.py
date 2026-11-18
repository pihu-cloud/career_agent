"""
StudentSkill ORM model (SB1/US3).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_name: Mapped[str] = mapped_column(String(200), nullable=False)
    proficiency_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    skill_type: Mapped[str] = mapped_column(String(20), nullable=False, default="technical")
    years_experience: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
