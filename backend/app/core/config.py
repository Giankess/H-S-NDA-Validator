from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    
    # MinIO settings
    MINIO_URL: str = "minio:9000"  # Using container name instead of localhost
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str = "nda-validator"
    
    # Vector DB settings
    VECTOR_DB_URL: str = "http://qdrant:6333"
    
    # Redis settings
    REDIS_URL: str = "redis://redis:6379"
    
    # File storage settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"docx"}
    
    class Config:
        env_file = ".env"

settings = Settings() 