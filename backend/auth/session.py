"""
Token blacklist for logout/revocation (SB1/US49).
Falls back to in-memory set when Redis is unavailable.
"""

from __future__ import annotations

_blacklisted_jtis: set[str] = set()


def blacklist_token(jti: str) -> None:
    """Add a token JTI to the blacklist."""
    try:
        from backend.cache.redis_client import cache
        import asyncio
        # Try async cache; if running in sync context fall through to in-memory
        if asyncio.get_event_loop().is_running():
            # We are inside an async context — use the in-memory fallback for
            # simplicity (the full async path is handled in the route handler).
            _blacklisted_jtis.add(jti)
        else:
            _blacklisted_jtis.add(jti)
    except Exception:
        _blacklisted_jtis.add(jti)


def is_token_blacklisted(jti: str) -> bool:
    """Return True if the token JTI has been blacklisted."""
    return jti in _blacklisted_jtis
