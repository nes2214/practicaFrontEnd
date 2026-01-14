"""
users.py
-------
This module contains user-related utility functions for:
    - Password hashing and verification using Argon2
    - JWT creation and validation
    - Database operations for user management
"""

from datetime import datetime, timedelta
from typing import Optional
from loguru import logger
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
import asyncpg
from jwt import ExpiredSignatureError, InvalidTokenError

from storage import settings
from model import UserToken

# -------------------------------------------------------------------
# 1) PASSWORD HASHING AND VERIFICATION
# -------------------------------------------------------------------
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """
    Hash a plain password using Argon2.

    Args:
        password (str): Plain text password.

    Returns:
        str: Argon2 hashed password.
    """
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed Argon2 password.

    Args:
        plain_password (str): Password entered by the user.
        hashed_password (str): Stored Argon2 hashed password.

    Returns:
        bool: True if password matches, False otherwise.
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False


# -------------------------------------------------------------------
# 2) JWT CREATION
# -------------------------------------------------------------------
def create_access_token(data: dict, expires_minutes: int = 60) -> str:
    """
    Create a JWT access token with expiration.

    Args:
        data (dict): Data to encode in the token (typically {'sub': username, 'role': role}).
        expires_minutes (int, optional): Expiration time in minutes. Defaults to 60.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.algorithm)


# -------------------------------------------------------------------
# 3) JWT VALIDATION
# -------------------------------------------------------------------
def decode_access_token(token: str) -> UserToken:
    """
    Decode a JWT token and return a UserToken object.

    If the token is expired or invalid, returns a UserToken with None fields.

    Args:
        token (str): JWT token string.

    Returns:
        UserToken: Object containing 'username' and 'role', or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.algorithm],
            options={"verify_exp": True}  # Ensure expiration is checked
        )
        username: str = payload.get("sub")
        role: str = payload.get("role")
        return UserToken(username=username, role=role)
    except ExpiredSignatureError:
        logger.warning("JWT token expired")
        return UserToken(username=None, role=None)
    except InvalidTokenError:
        logger.warning("JWT token invalid")
        return UserToken(username=None, role=None)


# -------------------------------------------------------------------
# 4) DATABASE OPERATIONS
# -------------------------------------------------------------------
async def get_user(username: str, pool) -> Optional[dict]:
    """
    Retrieve a user row from the database by username.

    Args:
        username (str): Username of the user to fetch.
        pool (asyncpg.Pool): AsyncPG connection pool.

    Returns:
        Optional[dict]: Dictionary with user data ('username', 'hashed_password', 'role')
                        or None if user does not exist.
    """
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT username, hashed_password, role FROM users WHERE username=$1",
            username,
        )


async def create_user(username: str, password: str, pool: asyncpg.Pool, role: str):
    """
    Create a new user in the database and set up their Postgres role.

    Args:
        username (str): Username for the new user.
        password (str): Plain text password to be hashed and stored.
        pool (asyncpg.Pool): AsyncPG connection pool.
        role (str): Role to assign ('patient', 'doctor', 'admin').

    Steps:
        1. Hash the password using Argon2.
        2. Insert user into 'users' table.
        3. Create a corresponding Postgres role (NOLOGIN).
        4. Grant privileges of the given role to the new user.
    """
    hashed = hash_password(password)

    async with pool.acquire() as conn:
        async with conn.transaction():
            # 1) Create user in 'users' table
            await conn.execute(
                """
                INSERT INTO users (username, hashed_password, role)
                VALUES ($1, $2, $3)
                """,
                username, hashed, role
            )

            # 2) Create ROLE in Postgres (no login)
            await conn.execute(f'CREATE ROLE "{username}" NOLOGIN')

            # 3) Grant privileges according to role
            await conn.execute(f'GRANT {role} TO "{username}"')