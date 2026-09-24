"""Security, authentication, and password hashing utilities (Section 15).

Implements Argon2id password hashing and JWT token management.
Strictly prohibits plain MD5, SHA1, or unsalted hashing algorithms.
"""

import os
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

# Password Hasher with Argon2id RFC 9106 recommended defaults
ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

# JWT Secret Configuration
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id with automatic salt generation."""
    if not password:
        raise ValueError("Password cannot be empty.")
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a candidate plaintext password against an Argon2id hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Check if the hash was generated with older or weaker Argon2 parameters."""
    return ph.check_needs_rehash(hashed_password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a signed JWT access token.

    Security Rule: Strictly restricts acceptable algorithms to [JWT_ALGORITHM] to
    mitigate algorithm confusion attacks (e.g. none-algorithm or key-confusion exploits).
    """
    if not token or not isinstance(token, str):
        raise ValueError("Invalid authentication token.")
    if JWT_ALGORITHM.lower() == "none":
        raise ValueError("Insecure JWT algorithm 'none' is strictly prohibited.")
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_signature": True, "verify_exp": True},
        )
        return payload
    except JWTError as err:
        raise ValueError("Invalid or expired authentication token.") from err
