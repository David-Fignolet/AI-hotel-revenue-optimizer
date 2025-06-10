# src/utils/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Hotel Revenue Optimizer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # API settings
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./hotel_revenue.db")
    
    # Redis settings (for caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    
    # Authentication settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # External API settings
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    COMPETITOR_SCRAPER_API: Optional[str] = os.getenv("COMPETITOR_SCRAPER_API")
    
    # Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "models/demand_forecast_model.pkl")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Initialize settings
settings = Settings()

# Update SQLAlchemy URL for async support
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgres"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)