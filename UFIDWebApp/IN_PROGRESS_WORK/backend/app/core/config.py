import secrets
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = "../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
    FRONTEND_HOST: str = "http://localhost:5173"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    FIRST_SUPERUSER_EMAIL: str = "Admin1@ufl.edu"
    FIRST_SUPERUSER_USERNAME: str = "Admin1"
    FIRST_SUPERUSER_PASSWORD: str = "Admin1"


settings = Settings()