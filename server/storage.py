"""
storage.py
----------
Centralized configuration for environment variables, database URL, JWT settings,
and MinIO/Filebase client setup.

This module provides:
    - Pydantic Settings class for structured configuration
    - MinIO client for file operations
    - Centralized access to all critical settings
"""

from minio import Minio
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# -------------------------------------------------------------------
# Load environment variables from .env
# -------------------------------------------------------------------
# Using dotenv to ensure environment variables are loaded from a .env file.
# This makes it easy to configure different environments (dev, prod, test).
load_dotenv()


# -------------------------------------------------------------------
# Settings class
# -------------------------------------------------------------------
class Settings(BaseSettings):
    """
    Centralized configuration using Pydantic BaseSettings.

    Reads environment variables for database, JWT, and Filebase credentials.

    Attributes:
        access_key (str): MinIO/Filebase access key (from ACCESS_KEY).
        secret_key (str): MinIO/Filebase secret key (from SECRET_KEY).
        bucket_name (str): Bucket name in Filebase (from BUCKET_NAME).
        endpoint (str): Filebase endpoint, defaults to "s3.filebase.com".
        filebase_gateway (str): Optional Filebase gateway for CDN, defaults to "anxious-amber-raccoon.myfilebase.com".
        database_url (str): Full database URL (from DATABASE_URL).
        database_host (str): Database host, defaults to "localhost".
        database_user (str): Database user, defaults to "postgres".
        database_password (str): Database password, defaults to "password".
        database_name (str): Database name, defaults to "clinic_db".
        jwt_secret_key (str): Secret key used for JWT encoding/decoding (from JWT_SECRET_KEY).
        algorithm (str): Algorithm used for JWT (from ALGORITHM).
    """

    # Filebase / MinIO configuration
    access_key: str = Field(alias="ACCESS_KEY")
    secret_key: str = Field(alias="SECRET_KEY")
    bucket_name: str = Field(alias="BUCKET_NAME")
    endpoint: str = Field(default="s3.filebase.com")
    filebase_gateway: str = Field(default="anxious-amber-raccoon.myfilebase.com")

    # JWT configuration
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    algorithm: str = Field(alias="ALGORITHM")

    # Database configuration
    database_url: str = Field(alias="DATABASE_URL")
    database_host: str = Field(default="localhost")
    database_user: str = Field(default="postgres")
    database_password: str = Field(default="password")
    database_name: str = Field(default="clinic_db")

    # Pydantic configuration to read from .env
    model_config = {"env_file": ".env"}


# -------------------------------------------------------------------
# Instantiate global settings object
# -------------------------------------------------------------------
# This object will be imported by other modules to access all configuration
# in a centralized way.
settings = Settings()


# -------------------------------------------------------------------
# MinIO / Filebase client
# -------------------------------------------------------------------
"""
MinIO client configured to interact with Filebase.

This client is used for:
    - Uploading files to Filebase bucket
    - Removing files from bucket
    - Listing and retrieving file objects

The 'secure=True' flag ensures all connections use HTTPS.
"""
client = Minio(
    endpoint=settings.endpoint,
    access_key=settings.access_key,
    secret_key=settings.secret_key,  # Corrected typo
    secure=True
)
