"""JWT (HS256) auth, bcrypt password hashing and the require_auth / require_admin dependencies."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.models import Role, User

ALGORITHM = "HS256"
BCRYPT_ROUNDS = 12
# bcrypt only uses the first 72 bytes; bcryptjs truncated silently, newer `bcrypt` raises instead.
BCRYPT_MAX_BYTES = 72

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthPayload:
    sub: int
    email: str
    role: Role


def sign_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        # `sub` stays numeric: the frontend reads it as the user id.
        "sub": user.id,
        "email": user.email,
        "role": user.role.value,
        "iat": now,
        "exp": now + timedelta(days=settings.jwt_expires_days),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> AuthPayload:
    """Raises jwt.InvalidTokenError (or KeyError/ValueError for malformed claims)."""
    data = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[ALGORITHM],
        options={"require": ["exp", "sub"], "verify_sub": False},
    )
    return AuthPayload(sub=int(data["sub"]), email=data["email"], role=Role(data["role"]))


def _password_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:BCRYPT_MAX_BYTES]


async def hash_password(password: str) -> str:
    hashed = await run_in_threadpool(
        bcrypt.hashpw, _password_bytes(password), bcrypt.gensalt(BCRYPT_ROUNDS)
    )
    return hashed.decode("utf-8")


async def verify_password(password: str, password_hash: str) -> bool:
    try:
        return await run_in_threadpool(
            bcrypt.checkpw, _password_bytes(password), password_hash.encode("utf-8")
        )
    except ValueError:
        return False


def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> AuthPayload:
    """Any authenticated user."""
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    try:
        return decode_token(credentials.credentials)
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from None


def require_admin(payload: Annotated[AuthPayload, Depends(require_auth)]) -> AuthPayload:
    """Admin role required."""
    if payload.role != Role.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
    return payload


CurrentUser = Annotated[AuthPayload, Depends(require_auth)]
CurrentAdmin = Annotated[AuthPayload, Depends(require_admin)]
