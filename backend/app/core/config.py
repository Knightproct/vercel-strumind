"""
Configuration settings for StruMind Backend
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "StruMind"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/strumind"
    SQLITE_URL: str = "sqlite:///./strumind_cache.db"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Redis (for caching and task queue)
    REDIS_URL: str = "redis://localhost:6379"
    
    # File storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Analysis settings
    MAX_NODES: int = 100000
    MAX_ELEMENTS: int = 200000
    ANALYSIS_TIMEOUT: int = 3600  # 1 hour
    
    # BIM settings
    BIM_CACHE_SIZE: int = 1000
    BIM_EXPORT_FORMATS: List[str] = ["ifc", "step", "dwg"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(exist_ok=True)
