"""
StudentProgress ORM model (SB1/US31).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    milestone_type: Mapped[str] = mapped_column(String(100), nullable=False)
    milestone_name: Mapped[str] = mapped_column(String(300), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
