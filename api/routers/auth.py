"""Authentication router implementing signup, login, and user profile endpoints."""

import uuid
from datetime import timedelta

from database.connection import get_db
from database.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from api.schemas import Token, UserCreate, UserLogin, UserResponse
from src.common.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def signup(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register a new user account with Argon2id password hashing."""
    existing_user = db.scalar(select(User).where(User.email == user_in.email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists.",
        )

    user = User(
        id=uuid.uuid4(),
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Authenticate with email and password, returning a signed JWT access token."""
    user = db.scalar(select(User).where(User.email == credentials.email))
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    token_data = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Retrieve details for the currently authenticated user."""
    return current_user
