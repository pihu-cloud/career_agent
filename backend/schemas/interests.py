"""
Interest Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class InterestCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    interest_name: str = Field(..., min_length=1, max_length=200)
    strength: int = Field(default=5, ge=1, le=10)


class InterestResponse(BaseModel):
    id: str
    user_id: str
    category: str
    interest_name: str
    strength: int
    created_at: datetime

    model_config = {"from_attributes": True}
