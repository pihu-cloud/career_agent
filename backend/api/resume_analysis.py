"""
SB2/US10 - AI-Powered Resume Analysis and Automatic Skill Extraction Endpoints
"""
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db.database import get_db
from backend.models.user import User
from backend.models.resume import Resume
from backend.models.skills import StudentSkill
from backend.schemas.recommendations import ResumeAnalysisResult
from backend.auth.jwt import get_current_user
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/api/v1/resume-analysis", tags=["Resume AI Parsing"])

@router.post("/{resume_id}", response_model=ResumeAnalysisResult)
async def analyze_resume_content(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    resume = (await db.execute(stmt)).scalar_one_or_none()
    if not resume or not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume record or file not found.")

    res = ml_service.extract_skills_from_file(resume.file_path)
    all_skills = res.get("all", [])
    tech_skills = res.get("technical", [])
    soft_skills = res.get("soft", [])

    summary = (
        f"Detected {len(tech_skills)} technical competencies and {len(soft_skills)} professional soft skills. "
        "Resume demonstrates solid alignment with core engineering and technology pathways."
    )

    return ResumeAnalysisResult(
        extracted_skills=all_skills,
        technical_skills=tech_skills,
        soft_skills=soft_skills,
        total_skills_found=len(all_skills),
        readiness_summary=summary
    )

@router.post("/{resume_id}/sync-skills")
async def sync_extracted_skills_to_profile(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    resume = (await db.execute(stmt)).scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    res = ml_service.extract_skills_from_file(resume.file_path)
    existing_skills = (await db.execute(select(StudentSkill).where(StudentSkill.user_id == current_user.id))).scalars().all()
    existing_names = {s.skill_name.lower() for s in existing_skills}

    added_count = 0
    for s_name in res.get("technical", []):
        if s_name.lower() not in existing_names:
            db.add(StudentSkill(
                user_id=current_user.id,
                skill_name=s_name,
                proficiency_level=3,
                skill_type="technical",
                is_verified=True
            ))
            existing_names.add(s_name.lower())
            added_count += 1

    for s_name in res.get("soft", []):
        if s_name.lower() not in existing_names:
            db.add(StudentSkill(
                user_id=current_user.id,
                skill_name=s_name,
                proficiency_level=4,
                skill_type="soft",
                is_verified=True
            ))
            existing_names.add(s_name.lower())
            added_count += 1

    await db.commit()
    return {"message": f"Successfully synced {added_count} skills from resume into student profile."}
