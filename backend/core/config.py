"""
SB1/US38 - Environment variables and configuration management
SB1/US42 - CORS configuration
"""
import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "Intelligent Career Pathway Navigator with Adaptive Skill-Gap Analysis"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production-min-32-chars"

    # Database
    database_url: str = "sqlite:///./careerpilot.db"

    # JWT
    jwt_secret_key: str = "dev-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # File Upload
    upload_dir: str = "./uploads"
    max_resume_size_mb: int = 10

    # CORS
    frontend_url: str = "http://localhost:3000"
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Admin
    admin_email: str = "admin@careerpilot.edu"
    admin_password: str = "Admin@123456"

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # ML
    ml_model_dir: str = "./ml/models/saved"
    sample_data_mode: bool = True

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
