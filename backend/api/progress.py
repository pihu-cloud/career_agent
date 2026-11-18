"""
SB1/US31 - Student Progress Milestones and Trajectory Tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any

from backend.db.database import get_db
from backend.models.user import User
from backend.models.progress import StudentProgress
from backend.schemas.progress import ProgressCreate, ProgressResponse
from backend.auth.jwt import get_current_user

router = APIRouter(prefix="/api/v1/progress", tags=["Student Progress"])

@router.get("", response_model=List[ProgressResponse])
async def get_progress_timeline(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(StudentProgress)
        .where(StudentProgress.user_id == current_user.id)
        .order_by(StudentProgress.completed_at.desc())
    )
    return (await db.execute(stmt)).scalars().all()

@router.post("", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
async def record_milestone(
    milestone_in: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    entry = StudentProgress(
        user_id=current_user.id,
        milestone_type=milestone_in.milestone_type,
        milestone_name=milestone_in.milestone_name,
        score=milestone_in.score,
        notes=milestone_in.notes
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry

@router.get("/summary", response_model=Dict[str, Any])
async def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentProgress).where(StudentProgress.user_id == current_user.id)
    records = (await db.execute(stmt)).scalars().all()

    total_milestones = len(records)
    avg_score = round(sum(r.score for r in records if r.score) / max(1, total_milestones), 1)

    return {
        "total_milestones": total_milestones,
        "average_score": avg_score,
        "latest_milestone": records[0] if records else None
    }
