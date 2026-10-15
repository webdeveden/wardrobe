from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.schemas import AuthIn, AuthOut, UserOut
from app.security import CurrentUser, hash_password, sign_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

Session = Annotated[AsyncSession, Depends(get_session)]


def _auth_response(user: User) -> AuthOut:
    return AuthOut(token=sign_token(user), user=UserOut.model_validate(user))


@router.get("/me", response_model=AuthOut)
async def me(payload: CurrentUser, session: Session) -> AuthOut:
    """Re-read the user's role from the DB and issue a fresh token.

    Called on app load so role changes made directly in the DB (e.g. promoting to ADMIN)
    take effect without logging out.
    """
    user = await session.get(User, payload.sub)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return _auth_response(user)


@router.post("/register", response_model=AuthOut, status_code=status.HTTP_201_CREATED)
async def register(body: AuthIn, session: Session) -> AuthOut:
    existing = await session.scalar(select(User).where(User.email == body.email))
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = User(email=body.email, password_hash=await hash_password(body.password))
    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered") from None
    return _auth_response(user)


@router.post("/login", response_model=AuthOut)
async def login(body: AuthIn, session: Session) -> AuthOut:
    user = await session.scalar(select(User).where(User.email == body.email))
    if user is None or not await verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return _auth_response(user)
