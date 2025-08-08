"""Application configuration settings."""

import json
from typing import Any, List, Optional

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SantaServer"

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_SERVER")
        port = values.get("POSTGRES_PORT")
        db = values.get("POSTGRES_DB")

        # Build URL string manually for pydantic v2
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        return url

    # CORS - stored as string, parsed to list
    BACKEND_CORS_ORIGINS: str = ""

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from string to list."""
        if not self.BACKEND_CORS_ORIGINS:
            return []

        cors_str = self.BACKEND_CORS_ORIGINS
        if cors_str.startswith("[") and cors_str.endswith("]"):
            # Handle JSON-like format
            return json.loads(cors_str)
        else:
            # Handle comma-separated values
            return [url.strip() for url in cors_str.split(",") if url.strip()]

    # Azure AD Authentication
    TENANT_ID: str
    CLIENT_ID: str
    CLIENT_SECRET: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password Policy
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SYMBOLS: bool = True
    PASSWORD_EXPIRY_DAYS: int = 90
    PASSWORD_HISTORY_COUNT: int = 5
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 480
    REFRESH_TOKEN_ROTATION: bool = True
    SESSION_ABSOLUTE_TIMEOUT_HOURS: int = 24

    # Environment
    ENVIRONMENT: str = "development"

    model_config = {"case_sensitive": True, "env_file": ".env"}


settings = Settings()
