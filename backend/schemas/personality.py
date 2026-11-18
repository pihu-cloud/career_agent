"""
Personality Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PersonalityCreate(BaseModel):
    trait_name: str = Field(..., min_length=1, max_length=200)
    score: int = Field(..., ge=1, le=10)
    assessment_type: str = Field(default="self", max_length=100)


class PersonalityResponse(BaseModel):
    id: str
    user_id: str
    trait_name: str
    score: int
    assessment_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
