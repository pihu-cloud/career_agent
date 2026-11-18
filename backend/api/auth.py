"""
SB1/US10, US11, US16, US23 - Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from backend.db.database import get_db
from backend.models.user import User
from backend.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token,
    PasswordChange, ForgotPasswordRequest, ResetPasswordRequest
)
from backend.auth.security import hash_password, verify_password, validate_password_strength
from backend.auth.jwt import create_access_token, create_refresh_token, decode_token, get_current_user
from backend.auth.session import blacklist_token
from backend.cache.redis_client import cache
from backend.core.logging import logger

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Validate password strength
    valid, msg = validate_password_strength(user_in.password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # Check email duplicate
    stmt = select(User).where(User.email == user_in.email.lower().strip())
    existing = await db.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="An account with this email address already exists.")

    # Check username duplicate
    stmt_u = select(User).where(User.username == user_in.username.strip())
    existing_u = await db.execute(stmt_u)
    if existing_u.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username is already taken.")

    new_user = User(
        email=user_in.email.lower().strip(),
        username=user_in.username.strip(),
        full_name=user_in.full_name.strip(),
        hashed_password=hash_password(user_in.password),
        role=user_in.role if user_in.role in ["student", "admin"] else "student",
        is_active=True,
        is_verified=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info(f"Registered new user: {new_user.email} (Role: {new_user.role})")
    return new_user

@router.post("/login", response_model=Token)
async def login(login_in: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == login_in.email.lower().strip())
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account has been suspended or deactivated.")

    user.last_login = datetime.utcnow()
    await db.commit()

    token_data = {"sub": user.id, "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/refresh")
async def refresh_token(refresh_payload: dict, db: AsyncSession = Depends(get_db)):
    r_token = refresh_payload.get("refresh_token")
    if not r_token:
        raise HTTPException(status_code=400, detail="Refresh token required.")
    
    payload = decode_token(r_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive.")

    token_data = {"sub": user.id, "email": user.email, "role": user.role}
    new_access = create_access_token(token_data)
    return {"access_token": new_access, "token_type": "bearer"}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # Blacklist current session
    blacklist_token(current_user.id)
    return {"message": "Successfully logged out."}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
async def change_password(
    pwd_in: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not verify_password(pwd_in.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password incorrect.")

    valid, msg = validate_password_strength(pwd_in.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    current_user.hashed_password = hash_password(pwd_in.new_password)
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Password updated successfully."}

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == req.email.lower().strip())
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if user:
        reset_code = f"RESET-{user.id[:8].upper()}"
        cache.set(f"reset_{req.email}", reset_code, ttl=900)
        logger.info(f"Password reset token generated for {user.email}: {reset_code}")
    return {"message": "If this email is registered, password reset instructions have been generated."}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    cached_code = cache.get(f"reset_{req.email}")
    if not cached_code or cached_code != req.token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    valid, msg = validate_password_strength(req.new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    stmt = select(User).where(User.email == req.email.lower().strip())
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.hashed_password = hash_password(req.new_password)
    await db.commit()
    cache.delete(f"reset_{req.email}")
    return {"message": "Password reset successfully. Please log in with your new password."}
