"""
Skill Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SkillCreate(BaseModel):
    skill_name: str = Field(..., min_length=1, max_length=200)
    proficiency_level: int = Field(..., ge=1, le=5)
    skill_type: str = Field(default="technical", pattern="^(technical|soft)$")
    years_experience: float = Field(default=0.0, ge=0.0)


class SkillUpdate(BaseModel):
    skill_name: Optional[str] = Field(None, min_length=1, max_length=200)
    proficiency_level: Optional[int] = Field(None, ge=1, le=5)
    skill_type: Optional[str] = Field(None, pattern="^(technical|soft)$")
    years_experience: Optional[float] = Field(None, ge=0.0)


class SkillResponse(BaseModel):
    id: str
    user_id: str
    skill_name: str
    proficiency_level: int
    skill_type: str
    years_experience: float
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
