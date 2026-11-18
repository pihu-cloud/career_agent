"""
SB1/US16, SB1/US23 - Security and Authentication Unit Tests
"""
import pytest
from datetime import timedelta
from backend.auth.security import hash_password, verify_password, validate_password_strength
from backend.auth.jwt import create_access_token, decode_token

def test_password_hashing():
    pwd = "SecureStudentPass@123"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword@123", hashed) is False

def test_password_strength_validation():
    # Weak passwords
    is_valid, msg = validate_password_strength("short")
    assert is_valid is False
    assert "8 characters" in msg

    is_valid, msg = validate_password_strength("alllowercaseletters")
    assert is_valid is False
    assert "uppercase" in msg

    # Strong password
    is_valid, msg = validate_password_strength("StrongPass@2026")
    assert is_valid is True
    assert msg == "Password is strong"

def test_jwt_token_generation_and_decoding():
    payload = {"sub": "user-12345", "email": "student@college.edu", "role": "student"}
    token = create_access_token(payload, expires_delta=timedelta(minutes=15))
    assert isinstance(token, str)

    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-12345"
    assert decoded["email"] == "student@college.edu"
    assert decoded["role"] == "student"

def test_invalid_jwt_token():
    invalid_token = "invalid.bearer.token.content"
    decoded = decode_token(invalid_token)
    assert decoded is None
