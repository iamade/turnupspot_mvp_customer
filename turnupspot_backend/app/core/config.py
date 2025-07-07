import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic_settings import BaseSettings

# Auto-load the correct .env file based on ENVIRONMENT
env = os.getenv("ENVIRONMENT", "development")
if env == "production":
    load_dotenv(".env.production")
else:
    load_dotenv(".env.development")


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TurnUp Spot API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = env
    
    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://turnupspot.com",
        "https://www.turnupspot.com"
    ]
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: str = "ca-central-1"
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # SendGrid
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@turnupspot.com"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: str
    
    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str

    # Supabase (optional, for compatibility with envs that include these)
    supabase_anon_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()