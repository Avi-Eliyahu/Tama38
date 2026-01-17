"""
Application configuration
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import json
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "TAMA38 API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@database:5432/tama38_dev"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours (NFR-SEC-007: Sessions must expire after 8 hours of inactivity)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days (reasonable balance between security and usability)
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from environment variable (supports JSON array or comma-separated string)"""
        if isinstance(v, str):
            # Try JSON first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Fall back to comma-separated string
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # Storage (Phase 1 - Local)
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "/app/storage"
    
    # Mock Services (Phase 1)
    MOCK_WHATSAPP_ENABLED: bool = True
    MOCK_SMS_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "/app/logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

