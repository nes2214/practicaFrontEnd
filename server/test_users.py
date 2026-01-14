# test_users.py
# -----------------------------
# Tests for user utilities: password hashing and JWT handling
# -----------------------------
# This module tests the functions in users.py for hashing passwords,
# verifying passwords, creating JWT tokens, and decoding them.
# -----------------------------

from datetime import datetime, timedelta
import pytest
import jwt

from users import hash_password, verify_password, create_access_token, decode_access_token
from model import UserToken
from storage import settings

# ---------------------------
# PASSWORD HASHING
# ---------------------------
@pytest.mark.asyncio
async def test_hash_and_verify_password():
    """
    Test hashing a password and verifying it.
    Ensures correct password passes and wrong password fails.
    """
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


# ---------------------------
# JWT CREATION / DECODING
# ---------------------------
def test_jwt_create_and_decode():
    """
    Test creating a JWT token and decoding it.
    Ensures the returned UserToken contains correct username and role.
    """
    data = {"sub": "alice", "role": "admin"}
    token = create_access_token(data, expires_minutes=1)
    user_token: UserToken = decode_access_token(token)
    assert user_token.username == "alice"
    assert user_token.role == "admin"


def test_decode_invalid_token():
    """
    Test decoding an invalid JWT token.
    The function should return a UserToken with None fields.
    """
    user_token = decode_access_token("this.is.not.a.valid.token")
    assert user_token.username is None
    assert user_token.role is None


def test_decode_expired_token():
    """
    Test decoding an expired JWT token.
    The function should return a UserToken with None fields.
    """
    data = {"sub": "bob", "role": "doctor"}
    expired_token = jwt.encode(
        {**data, "exp": int((datetime.now() - timedelta(seconds=1)).timestamp())},
        settings.jwt_secret_key,
        algorithm=settings.algorithm,
    )
    user_token = decode_access_token(expired_token)
    assert user_token.username is None
    assert user_token.role is None
