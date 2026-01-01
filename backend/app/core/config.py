"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Union


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
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
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

