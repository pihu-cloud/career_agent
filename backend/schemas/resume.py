"""
Resume Pydantic schemas.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    is_primary: bool
    uploaded_at: datetime

    model_config = {"from_attributes": True}
