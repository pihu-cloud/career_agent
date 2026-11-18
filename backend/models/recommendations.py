"""
SB2/US15 - Database ORM Models for ML Recommendations, Explanations, Logs & Feedback
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from backend.db.database import Base

class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    career_title = Column(String(150), nullable=False, index=True)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    skill_gaps = Column(Text, nullable=True)  # JSON-encoded string
    model_version = Column(String(50), default="1.0.0")
    is_latest = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    career_title = Column(String(150), nullable=False)
    liked = Column(Boolean, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ABTestGroup(Base):
    __tablename__ = "ab_test_groups"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    group_name = Column(String(20), nullable=False)  # 'control' or 'variant'
    assigned_at = Column(DateTime, default=datetime.utcnow)

class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    input_features = Column(Text, nullable=True)  # JSON
    output_careers = Column(Text, nullable=True)  # JSON
    model_used = Column(String(100), default="HybridRecommender")
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
