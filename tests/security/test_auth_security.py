"""Security test suite: Argon2id password hashing and JWT token handling (Section 15)."""

from datetime import timedelta

import pytest

from src.common.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    needs_rehash,
    verify_password,
)


def test_argon2id_hashing_and_verification() -> None:
    raw_pw = "SuperSecretP@ssw0rd!2026"
    h = hash_password(raw_pw)

    # Must start with $argon2id$
    assert h.startswith("$argon2id$")

    # Positive verification
    assert verify_password(raw_pw, h) is True

    # Negative verification
    assert verify_password("WrongPassword!", h) is False
    assert verify_password("", h) is False
    assert verify_password(raw_pw, "") is False

    # Does not need rehash with current params
    assert needs_rehash(h) is False


def test_argon2id_unique_salts() -> None:
    pw = "CommonPassword123"
    h1 = hash_password(pw)
    h2 = hash_password(pw)
    # Even identical passwords must have distinct hashes due to random salt
    assert h1 != h2
    assert verify_password(pw, h1) is True
    assert verify_password(pw, h2) is True


def test_argon2id_empty_password_rejection() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        hash_password("")


def test_jwt_token_roundtrip_and_expiration() -> None:
    data = {"sub": "user_uuid_123", "email": "engineer@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=15))
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload["sub"] == "user_uuid_123"
    assert payload["email"] == "engineer@example.com"
    assert "exp" in payload


def test_jwt_expired_token_rejection() -> None:
    data = {"sub": "user_expired"}
    expired_token = create_access_token(data, expires_delta=timedelta(seconds=-10))

    with pytest.raises(ValueError, match="Invalid or expired"):
        decode_access_token(expired_token)


def test_jwt_algorithm_confusion_rejection() -> None:
    """Ensure tokens signed with unwhitelisted algorithms (e.g. HS512) are strictly rejected."""
    from jose import jwt

    from src.common.security import JWT_SECRET_KEY

    payload = {"sub": "attacker", "email": "attacker@exploit.com"}
    # Sign with a different HMAC algorithm than HS256
    confused_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS512")

    with pytest.raises(ValueError, match="Invalid or expired"):
        decode_access_token(confused_token)
