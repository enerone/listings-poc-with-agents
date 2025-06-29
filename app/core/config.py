from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./listings.db"
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:32b"
    ollama_timeout: int = 300
    
    # API Keys
    unsplash_api_key: Optional[str] = None
    unsplash_access_key: Optional[str] = None
    pexels_api_key: Optional[str] = None
    
    # File Upload Configuration
    max_file_size: int = 5 * 1024 * 1024  # 5MB
    allowed_extensions: set = {"png", "jpg", "jpeg", "gif", "webp"}
    allowed_mime_types: set = {
        "image/png", "image/jpeg", "image/gif", "image/webp"
    }
    upload_directory: str = "uploads"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_url: Optional[str] = None
    
    # App Configuration
    app_name: str = "Amazon Listings Generator"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()