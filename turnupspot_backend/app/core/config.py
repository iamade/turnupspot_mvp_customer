from typing import List, Optional
from pydantic_settings import BaseSettings
from decouple import config


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TurnUp Spot API"
    VERSION: str = "1.0.0"
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")
    
    # Database
    DATABASE_URL: str = config("DATABASE_URL")
    TEST_DATABASE_URL: Optional[str] = config("TEST_DATABASE_URL", default=None)
    
    # Security
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://turnupspot.com",
        "https://www.turnupspot.com"
    ]
    
    # Redis
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379")
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = config("AWS_ACCESS_KEY_ID", default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = config("AWS_SECRET_ACCESS_KEY", default=None)
    AWS_BUCKET_NAME: Optional[str] = config("AWS_BUCKET_NAME", default=None)
    AWS_REGION: str = config("AWS_REGION", default="ca-central-1")
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = config("STRIPE_SECRET_KEY", default=None)
    STRIPE_WEBHOOK_SECRET: Optional[str] = config("STRIPE_WEBHOOK_SECRET", default=None)
    
    # SendGrid
    SENDGRID_API_KEY: Optional[str] = config("SENDGRID_API_KEY", default=None)
    FROM_EMAIL: str = config("FROM_EMAIL", default="noreply@turnupspot.com")
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: str = config("GOOGLE_MAPS_API_KEY")
    
    # MongoDB
    MONGODB_URI: str = config("MONGODB_URI")
    MONGODB_DB_NAME: str = config("MONGODB_DB_NAME")
    
    class Config:
        env_file = ".env"


settings = Settings()