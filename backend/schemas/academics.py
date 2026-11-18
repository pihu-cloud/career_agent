"""
Academics Pydantic schemas.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AcademicCreate(BaseModel):
    institution: str = Field(..., min_length=1, max_length=300)
    degree: str = Field(..., min_length=1, max_length=200)
    field_of_study: str = Field(..., min_length=1, max_length=200)
    cgpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    start_year: int = Field(..., ge=1900, le=2100)
    end_year: Optional[int] = Field(None, ge=1900, le=2100)
    is_current: bool = False


class AcademicResponse(BaseModel):
    id: str
    user_id: str
    institution: str
    degree: str
    field_of_study: str
    cgpa: Optional[float]
    start_year: int
    end_year: Optional[int]
    is_current: bool

    model_config = {"from_attributes": True}
