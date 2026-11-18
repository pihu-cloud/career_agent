"""
Role-based access control dependencies (SB1/US12).
"""

from fastapi import Depends, HTTPException, status

from backend.auth.jwt import get_current_user
from backend.models.user import User


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_student_or_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require student or admin role."""
    if current_user.role not in ("student", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user
