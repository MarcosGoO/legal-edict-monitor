"""
Application configuration using Pydantic Settings.

This module provides centralized configuration management with:
- Environment variable loading
- Type validation
- Default values
- Secrets management
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================================================================
    # Application
    # =========================================================================
    app_name: str = "edict-guardian"
    app_env: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = False
    secret_key: str = Field(..., min_length=32)

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env in ["development", "test"]

    # =========================================================================
    # Database
    # =========================================================================
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/edict_guardian"
    )
    database_pool_size: int = Field(default=10, ge=1, le=100)
    database_max_overflow: int = Field(default=20, ge=0, le=50)

    @property
    def async_database_url(self) -> str:
        """Ensure async driver is used."""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url

    @property
    def sync_database_url(self) -> str:
        """Get sync URL for Alembic migrations."""
        if "+asyncpg" in self.database_url:
            return self.database_url.replace("+asyncpg", "")
        return self.database_url

    # =========================================================================
    # Redis
    # =========================================================================
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # =========================================================================
    # AWS Configuration
    # =========================================================================
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "edict-guardian-documents"

    # =========================================================================
    # OCR Configuration
    # =========================================================================
    tesseract_lang: str = "spa"
    ocr_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    enable_textract_fallback: bool = True

    # =========================================================================
    # NLP Configuration
    # =========================================================================
    spacy_model: str = "es_core_news_lg"

    # =========================================================================
    # Notifications - Twilio
    # =========================================================================
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None
    twilio_whatsapp_number: str | None = None

    @property
    def twilio_configured(self) -> bool:
        return all([
            self.twilio_account_sid,
            self.twilio_auth_token,
            self.twilio_phone_number,
        ])

    # =========================================================================
    # Notifications - SendGrid
    # =========================================================================
    sendgrid_api_key: str | None = None
    sendgrid_from_email: str = "noreply@edictguardian.com"

    @property
    def sendgrid_configured(self) -> bool:
        return self.sendgrid_api_key is not None

    # =========================================================================
    # Security
    # =========================================================================
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, ge=5)
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1)

    # =========================================================================
    # Crawler
    # =========================================================================
    crawler_user_agent: str = "EdictGuardian/1.0 (Legal Notification System)"
    crawler_timeout: int = Field(default=30, ge=5, le=120)
    crawler_max_retries: int = Field(default=3, ge=1, le=10)

    # =========================================================================
    # Logging
    # =========================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "json"

    # =========================================================================
    # CORS
    # =========================================================================
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="List of allowed CORS origins"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Convenience export
settings = get_settings()
