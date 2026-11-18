"""
SB1/US20, SB1/US43 - Input Validation and Sanitization Unit Tests
"""
from backend.schemas.user import UserCreate
from backend.schemas.skills import SkillCreate
from backend.middleware.sanitizer import _sanitize_value

def test_user_create_validation():
    user = UserCreate(
        email="student@univ.edu",
        username="john_doe",
        full_name="John Doe",
        password="SecurePass@123",
        role="student"
    )
    assert user.email == "student@univ.edu"

def test_skill_create_validation():
    skill = SkillCreate(
        skill_name="React.js",
        proficiency_level=5,
        skill_type="technical",
        years_experience=3.0
    )
    assert skill.proficiency_level == 5

def test_sanitizer_removes_script_tags():
    malicious = "<script>alert('XSS')</script>John Doe"
    clean = _sanitize_value(malicious)
    assert "<script>" not in clean
    assert clean == "John Doe"

def test_sanitizer_cleans_nested_dict():
    payload = {
        "name": "<script>evil()</script>Alice",
        "nested": {"note": "safe text"}
    }
    cleaned = _sanitize_value(payload)
    assert cleaned["name"] == "Alice"
    assert cleaned["nested"]["note"] == "safe text"
