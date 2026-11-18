"""
SB1/US11, US14, US22 - Student Profile, Skills, Interests & Personality Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Dict, Any

from backend.db.database import get_db
from backend.models.user import User
from backend.models.skills import StudentSkill
from backend.models.interests import Interest
from backend.models.personality import PersonalityTrait
from backend.models.academics import AcademicRecord
from backend.models.resume import Resume
from backend.schemas.user import UserResponse, UserUpdate
from backend.schemas.skills import SkillCreate, SkillResponse, SkillUpdate
from backend.schemas.interests import InterestCreate, InterestResponse
from backend.schemas.personality import PersonalityCreate, PersonalityResponse
from backend.auth.jwt import get_current_user

router = APIRouter(prefix="/api/v1/profile", tags=["Profile & Assessments"])

@router.get("", response_model=Dict[str, Any])
async def get_full_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch user skills
    skills_stmt = select(StudentSkill).where(StudentSkill.user_id == current_user.id)
    skills = (await db.execute(skills_stmt)).scalars().all()

    # Fetch interests
    interests_stmt = select(Interest).where(Interest.user_id == current_user.id)
    interests = (await db.execute(interests_stmt)).scalars().all()

    # Fetch personality traits
    traits_stmt = select(PersonalityTrait).where(PersonalityTrait.user_id == current_user.id)
    traits = (await db.execute(traits_stmt)).scalars().all()

    # Fetch academics
    acad_stmt = select(AcademicRecord).where(AcademicRecord.user_id == current_user.id)
    academics = (await db.execute(acad_stmt)).scalars().all()

    # Fetch resume
    resume_stmt = select(Resume).where(Resume.user_id == current_user.id)
    resumes = (await db.execute(resume_stmt)).scalars().all()

    return {
        "user": current_user,
        "skills": skills,
        "interests": interests,
        "personality": traits,
        "academics": academics,
        "resumes": resumes
    }

@router.put("", response_model=UserResponse)
async def update_profile_details(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/completion")
async def get_profile_completion(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    sections = {
        "skills": False,
        "interests": False,
        "personality": False,
        "academics": False,
        "resume": False
    }

    s_count = len((await db.execute(select(StudentSkill).where(StudentSkill.user_id == current_user.id))).scalars().all())
    if s_count > 0: sections["skills"] = True

    i_count = len((await db.execute(select(Interest).where(Interest.user_id == current_user.id))).scalars().all())
    if i_count > 0: sections["interests"] = True

    p_count = len((await db.execute(select(PersonalityTrait).where(PersonalityTrait.user_id == current_user.id))).scalars().all())
    if p_count > 0: sections["personality"] = True

    a_count = len((await db.execute(select(AcademicRecord).where(AcademicRecord.user_id == current_user.id))).scalars().all())
    if a_count > 0: sections["academics"] = True

    r_count = len((await db.execute(select(Resume).where(Resume.user_id == current_user.id))).scalars().all())
    if r_count > 0: sections["resume"] = True

    completed_count = sum(1 for v in sections.values() if v)
    percentage = int((completed_count / len(sections)) * 100)

    missing = [k for k, v in sections.items() if not v]

    return {
        "percentage": percentage,
        "is_complete": percentage == 100,
        "sections": sections,
        "missing_sections": missing
    }

# ==================== SKILLS (SB1/US3) ====================

@router.get("/skills", response_model=List[SkillResponse])
async def list_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentSkill).where(StudentSkill.user_id == current_user.id)
    return (await db.execute(stmt)).scalars().all()

@router.post("/skills", response_model=List[SkillResponse], status_code=status.HTTP_201_CREATED)
async def add_skills(
    skills_in: List[SkillCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    created = []
    for s in skills_in:
        item = StudentSkill(
            user_id=current_user.id,
            skill_name=s.skill_name.strip(),
            proficiency_level=s.proficiency_level,
            skill_type=s.skill_type or "technical",
            years_experience=s.years_experience or 0.0
        )
        db.add(item)
        created.append(item)
    await db.commit()
    for item in created:
        await db.refresh(item)
    return created

@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: str,
    skill_update: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentSkill).where(StudentSkill.id == skill_id, StudentSkill.user_id == current_user.id)
    skill = (await db.execute(stmt)).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill record not found.")

    if skill_update.skill_name is not None:
        skill.skill_name = skill_update.skill_name
    if skill_update.proficiency_level is not None:
        skill.proficiency_level = skill_update.proficiency_level
    if skill_update.skill_type is not None:
        skill.skill_type = skill_update.skill_type
    if skill_update.years_experience is not None:
        skill.years_experience = skill_update.years_experience

    await db.commit()
    await db.refresh(skill)
    return skill

@router.delete("/skills/{skill_id}")
async def delete_skill(
    skill_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(StudentSkill).where(StudentSkill.id == skill_id, StudentSkill.user_id == current_user.id)
    skill = (await db.execute(stmt)).scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill record not found.")
    await db.delete(skill)
    await db.commit()
    return {"message": "Skill removed successfully."}

# ==================== INTERESTS (SB1/US4) ====================

@router.get("/interests", response_model=List[InterestResponse])
async def list_interests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Interest).where(Interest.user_id == current_user.id)
    return (await db.execute(stmt)).scalars().all()

@router.post("/interests", response_model=List[InterestResponse], status_code=status.HTTP_201_CREATED)
async def add_interests(
    interests_in: List[InterestCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    created = []
    for i in interests_in:
        item = Interest(
            user_id=current_user.id,
            category=i.category,
            interest_name=i.interest_name.strip(),
            strength=i.strength
        )
        db.add(item)
        created.append(item)
    await db.commit()
    for item in created:
        await db.refresh(item)
    return created

@router.delete("/interests/{interest_id}")
async def delete_interest(
    interest_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Interest).where(Interest.id == interest_id, Interest.user_id == current_user.id)
    item = (await db.execute(stmt)).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Interest record not found.")
    await db.delete(item)
    await db.commit()
    return {"message": "Interest removed successfully."}

# ==================== PERSONALITY (SB1/US5) ====================

@router.get("/personality", response_model=List[PersonalityResponse])
async def get_personality_traits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(PersonalityTrait).where(PersonalityTrait.user_id == current_user.id)
    return (await db.execute(stmt)).scalars().all()

@router.post("/personality", response_model=List[PersonalityResponse], status_code=status.HTTP_201_CREATED)
async def save_personality_traits(
    traits_in: List[PersonalityCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Overwrite prior traits for fresh assessment
    await db.execute(delete(PersonalityTrait).where(PersonalityTrait.user_id == current_user.id))

    created = []
    for t in traits_in:
        item = PersonalityTrait(
            user_id=current_user.id,
            trait_name=t.trait_name,
            score=t.score,
            assessment_type=t.assessment_type or "Big5"
        )
        db.add(item)
        created.append(item)
    await db.commit()
    for item in created:
        await db.refresh(item)
    return created
