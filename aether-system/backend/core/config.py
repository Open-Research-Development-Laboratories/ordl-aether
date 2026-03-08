"""
AETHER Configuration Management
Inspired by NASA's mission configuration systems
"""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """System configuration - centralized like NASA's ground systems"""
    
    # Application
    APP_NAME: str = "AETHER"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/aether.db"
    VECTOR_DB_PATH: str = "./data/vector_db"
    
    # AI Models
    MODEL_CACHE_DIR: str = "./ai_models/cache"
    DEFAULT_IMAGE_MODEL: str = "google/vit-base-patch16-224"
    DEFAULT_TEXT_MODEL: str = "facebook/bart-large-cnn"
    DEFAULT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    PREWARM_MODELS: bool = False
    ANALYSIS_TIMEOUT_SECONDS: int = 300
    
    # Data Ingestion
    NASA_API_KEY: str = ""
    DATA_RETENTION_DAYS: int = 30
    MAX_FILE_SIZE_MB: int = 50
    
    # Processing
    MAX_WORKERS: int = 4
    BATCH_SIZE: int = 32
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path(settings.VECTOR_DB_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.MODEL_CACHE_DIR).mkdir(parents=True, exist_ok=True)
