"""
SB2/US6, US10, US24 - Pydantic Schemas for AI/ML Recommendations and Gap Analysis
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class SkillGapInfo(BaseModel):
    gap_score: float
    missing_skills: List[str]
    present_skills: List[str]
    gap_percentage: float

class RecommendationResponse(BaseModel):
    career_title: str
    score: float
    confidence: float
    reason: Optional[str] = None
    skill_gaps: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None

class FeedbackCreate(BaseModel):
    career_title: str
    liked: bool
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    career_title: str
    liked: bool
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeAnalysisResult(BaseModel):
    extracted_skills: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    total_skills_found: int
    readiness_summary: str
