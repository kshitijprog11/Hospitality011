from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/feedback_platform"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "feedback_platform"
    database_user: str = "username"
    database_password: str = "password"
    
    # Application Settings
    secret_key: str = "your-secret-key-change-in-production"
    debug: bool = True
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Authentication
    jwt_secret_key: str = "your-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API Keys
    openai_api_key: Optional[str] = None
    hugging_face_api_key: Optional[str] = None
    
    # Communication APIs
    whatsapp_api_token: Optional[str] = None
    email_api_key: Optional[str] = None
    email_from: str = "noreply@yourdomain.com"
    
    # NLP Configuration
    sentiment_threshold_negative: float = -0.5
    sentiment_threshold_positive: float = 0.5
    flagged_keywords: List[str] = ["urgent", "emergency", "terrible", "awful", "disgusting", "worst"]
    
    # Notification Settings
    enable_email_alerts: bool = True
    enable_browser_notifications: bool = True
    alert_threshold_sentiment: float = -0.7
    
    # File Upload Settings
    max_file_size: int = 10485760  # 10MB
    allowed_file_types: List[str] = ["txt", "csv", "json"]
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Construct database URL if individual components are provided
if not settings.database_url.startswith("postgresql://"):
    settings.database_url = (
        f"postgresql://{settings.database_user}:{settings.database_password}"
        f"@{settings.database_host}:{settings.database_port}/{settings.database_name}"
    )