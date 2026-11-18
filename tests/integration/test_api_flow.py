"""
SB1/US10, US11, US13, US33, US35 - Authentication and Profile API Integration Tests
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check_api():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Career Pathway" in data["app"]

def test_user_registration_and_login_flow():
    test_email = "api_test_student@careerpilot.edu"
    test_user = "apiteststudent"
    test_pass = "TestPass@2026"

    # Register
    reg_res = client.post("/api/v1/auth/register", json={
        "email": test_email,
        "username": test_user,
        "full_name": "API Test Student",
        "password": test_pass,
        "role": "student"
    })
    # Either 201 or 400 (if already exists)
    assert reg_res.status_code in [201, 400]

    # Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": test_pass
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    token = data["access_token"]

    # Access Protected Profile Route
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == test_email

    # Add Skills
    skill_res = client.post("/api/v1/profile/skills", json=[{
        "skill_name": "Machine Learning",
        "proficiency_level": 4,
        "skill_type": "technical",
        "years_experience": 2.0
    }], headers=headers)
    assert skill_res.status_code == 201
    assert len(skill_res.json()) >= 1

    # Check Completion
    comp_res = client.get("/api/v1/profile/completion", headers=headers)
    assert comp_res.status_code == 200
    assert comp_res.json()["sections"]["skills"] is True
