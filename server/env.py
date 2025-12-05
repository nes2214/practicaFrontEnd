from pydantic import Field

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_host: str = Field(alias="DATABASE_HOST")
    database_user: str = Field(alias="DATABASE_USER")
    database_password: str = Field(alias="DATABASE_PASSWORD")
    uvicorn_host: str = Field(alias="UVICORN_HOST")
    uvicorn_port: int = Field(alias="UVICORN_PORT")
    uvicorn_reload: bool = Field(alias="UVICORN_RELOAD")

    model_config = {"env_file": ".env"}


settings = Settings()
