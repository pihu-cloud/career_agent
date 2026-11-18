"""
SB2/US6, US16, US24, US26 - Career Recommendation and Skill Gap API Endpoints
"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Dict, Any

from backend.db.database import get_db
from backend.models.user import User
from backend.models.skills import StudentSkill
from backend.models.interests import Interest
from backend.models.personality import PersonalityTrait
from backend.models.academics import AcademicRecord
from backend.models.recommendations import CareerRecommendation, RecommendationFeedback
from backend.schemas.recommendations import (
    RecommendationResponse, FeedbackCreate, FeedbackResponse
)
from backend.auth.jwt import get_current_user
from backend.services.ml_service import ml_service
from backend.cache.redis_client import cache

router = APIRouter(prefix="/api/v1/recommendations", tags=["AI Recommendations"])

async def _build_user_profile_dict(user: User, db: AsyncSession) -> Dict[str, Any]:
    skills = (await db.execute(select(StudentSkill).where(StudentSkill.user_id == user.id))).scalars().all()
    interests = (await db.execute(select(Interest).where(Interest.user_id == user.id))).scalars().all()
    traits = (await db.execute(select(PersonalityTrait).where(PersonalityTrait.user_id == user.id))).scalars().all()
    acads = (await db.execute(select(AcademicRecord).where(AcademicRecord.user_id == user.id))).scalars().all()

    avg_cgpa = 7.5
    if acads:
        avg_cgpa = sum(a.cgpa for a in acads if a.cgpa) / len(acads)

    return {
        "user_id": user.id,
        "cgpa": avg_cgpa,
        "skills": [{"skill_name": s.skill_name, "proficiency_level": s.proficiency_level, "skill_type": s.skill_type} for s in skills],
        "interests": [{"category": i.category, "interest_name": i.interest_name, "strength": i.strength} for i in interests],
        "personality_traits": [{"trait_name": t.trait_name, "score": t.score} for t in traits],
        "num_academics": len(acads)
    }

@router.get("", response_model=List[RecommendationResponse])
async def get_career_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    profile = await _build_user_profile_dict(current_user, db)
    recs = ml_service.generate_recommendations(profile)

    # Persist latest recommendations in DB
    await db.execute(delete(CareerRecommendation).where(CareerRecommendation.user_id == current_user.id))
    for r in recs:
        rec_entry = CareerRecommendation(
            user_id=current_user.id,
            career_title=r["career"],
            score=round(r["score"], 2),
            confidence=round(r.get("confidence", 0.85), 2),
            reason=r.get("reason"),
            skill_gaps=json.dumps(r.get("skill_gaps", {})),
            is_latest=True
        )
        db.add(rec_entry)
    await db.commit()

    return [
        RecommendationResponse(
            career_title=r["career"],
            score=round(r["score"], 2),
            confidence=round(r.get("confidence", 0.85), 2),
            reason=r.get("reason"),
            skill_gaps=r.get("skill_gaps"),
            explanation=r.get("explanation")
        ) for r in recs
    ]

@router.post("/analyze")
async def force_fresh_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Invalidate cache
    cache.delete(f"rec_{current_user.id}")
    return await get_career_recommendations(current_user, db)

@router.get("/{career_title}/skill-gaps")
async def get_career_skill_gaps(
    career_title: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    skills = (await db.execute(select(StudentSkill).where(StudentSkill.user_id == current_user.id))).scalars().all()
    user_skill_names = [s.skill_name for s in skills]
    return ml_service.get_skill_gaps(user_skill_names, career_title)

@router.get("/{career_title}/growth")
async def get_career_growth_timeline(
    career_title: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    skills = (await db.execute(select(StudentSkill).where(StudentSkill.user_id == current_user.id))).scalars().all()
    user_skill_names = [s.skill_name for s in skills]
    acads = (await db.execute(select(AcademicRecord).where(AcademicRecord.user_id == current_user.id))).scalars().all()
    cgpa = acads[0].cgpa if acads and acads[0].cgpa else 7.5
    return ml_service.get_growth_trajectory(career_title, user_skill_names, cgpa)

@router.get("/market-insights")
async def get_labor_market_insights():
    return ml_service.get_market_insights()

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_recommendation_feedback(
    fb_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    fb = RecommendationFeedback(
        user_id=current_user.id,
        career_title=fb_in.career_title,
        liked=fb_in.liked,
        comment=fb_in.comment
    )
    db.add(fb)
    await db.commit()
    await db.refresh(fb)
    return fb
