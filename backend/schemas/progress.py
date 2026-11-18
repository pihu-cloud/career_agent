"""
Progress Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProgressCreate(BaseModel):
    milestone_type: str = Field(..., min_length=1, max_length=100)
    milestone_name: str = Field(..., min_length=1, max_length=300)
    completed_at: Optional[datetime] = None
    score: Optional[float] = Field(None, ge=0.0, le=100.0)
    notes: Optional[str] = None


class ProgressResponse(BaseModel):
    id: str
    user_id: str
    milestone_type: str
    milestone_name: str
    completed_at: Optional[datetime]
    score: Optional[float]
    notes: Optional[str]

    model_config = {"from_attributes": True}
