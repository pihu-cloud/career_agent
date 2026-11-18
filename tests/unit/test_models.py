"""
SB1/US1, US2, US3, US4, US5, US8, US9, US18 - Database Models & Constraints Tests (Synchronous)
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.database import Base
from backend.models.user import User
from backend.models.skills import StudentSkill
from backend.models.interests import Interest
from backend.models.personality import PersonalityTrait
from backend.models.academics import AcademicRecord
from backend.models.notifications import Notification
from backend.models.resume import Resume

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def sync_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()

def test_user_creation(sync_session):
    user = User(
        email="test_student@example.com",
        username="teststudent",
        full_name="Test Student",
        hashed_password="hashed_pass_value",
        role="student"
    )
    sync_session.add(user)
    sync_session.commit()
    sync_session.refresh(user)

    assert user.id is not None
    assert user.email == "test_student@example.com"
    assert user.is_active is True

def test_skills_and_relationships(sync_session):
    user = User(
        email="skills_student@example.com",
        username="skillstudent",
        full_name="Skill Student",
        hashed_password="dummy_hash_pass",
        role="student"
    )
    sync_session.add(user)
    sync_session.commit()
    sync_session.refresh(user)

    skill = StudentSkill(
        user_id=user.id,
        skill_name="Python",
        proficiency_level=4,
        skill_type="technical",
        years_experience=2.5
    )
    interest = Interest(
        user_id=user.id,
        category="Technology",
        interest_name="Artificial Intelligence",
        strength=9
    )
    personality = PersonalityTrait(
        user_id=user.id,
        trait_name="Openness",
        score=8.5,
        assessment_type="Big5"
    )

    sync_session.add_all([skill, interest, personality])
    sync_session.commit()
    sync_session.refresh(skill)
    sync_session.refresh(interest)
    sync_session.refresh(personality)

    assert skill.id is not None
    assert skill.user_id == user.id
    assert skill.skill_name == "Python"
    assert interest.interest_name == "Artificial Intelligence"
    assert personality.trait_name == "Openness"
