from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_host: str = Field(alias="DATABASE_HOST")
    database_user: str = Field(alias="DATABASE_USER")
    database_password: str = Field(alias="DATABASE_PASSWORD")

    model_config = {"env_file": ".env"}


settings = Settings()
