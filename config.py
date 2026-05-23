"""
Application Configuration Management
This module handles all configuration parameters from environment variables
with proper validation and defaults for different environments.
"""

import json
from typing import Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application configuration from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    # Application Settings
    app_name: str = "Intelligent Log Analyzer"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    log_level: str = "INFO"

    # Database
    database_url: str = "sqlite:///./intelligent_logs.db"
    database_echo: bool = False

    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # File Upload
    max_upload_size_mb: int = 50
    allowed_file_extensions: List[str] = ["log", "txt"]

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    allow_credentials: bool = True

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    pagination_limit: int = 100

    # Feature Flags
    enable_email_alerts: bool = False
    enable_slack_alerts: bool = False
    enable_rate_limiting: bool = True

    # Email Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    @field_validator("allowed_origins", "allowed_file_extensions", mode="before")
    @classmethod
    def parse_list_value(cls, v: Any) -> Any:
        if isinstance(v, str):
            value = v.strip()
            if not value:
                return []
            if value.startswith("[") and value.endswith("]"):
                try:
                    return json.loads(value)
                except ValueError:
                    pass
            return [item.strip() for item in value.split(",") if item.strip()]
        return v

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes"""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"


# Create global settings instance
settings = Settings()
