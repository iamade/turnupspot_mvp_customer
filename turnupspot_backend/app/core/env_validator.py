from typing import Optional
import os
from pydantic import BaseModel, field_validator, HttpUrl, ValidationInfo
from urllib.parse import urlparse

class EnvironmentValidator(BaseModel):
    # Database
    DATABASE_URL: str
    
    # Supabase (Required for production)
    SUPABASE_URL: Optional[HttpUrl] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # JWT
    SECRET_KEY: str = "dev-secret-key-local-development-only"  # Default for development only
    ALGORITHM: str = "HS256"  # Default value
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Default value
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"  # Default value
    
    # Environment
    ENVIRONMENT: str = "development"  # Default value
    DEBUG: bool = True  # Default value
    
    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str

    @field_validator('DATABASE_URL')
    def validate_database_url(cls, v: str, info: ValidationInfo) -> str:
        try:
            result = urlparse(v)
            assert all([result.scheme, result.netloc])
            
            # For production environment, ensure it's a Supabase URL
            if info.data.get('ENVIRONMENT') == 'production':
                assert 'supabase' in result.netloc, "Production DATABASE_URL must be a Supabase URL"
            
            # For development, ensure it's a local or Docker PostgreSQL URL
            if info.data.get('ENVIRONMENT') == 'development':
                assert 'localhost' in result.netloc or 'postgres' in result.netloc, \
                    "Development DATABASE_URL must be a local or Docker PostgreSQL URL"
            
            return v
        except AssertionError as e:
            raise ValueError(str(e))
        except:
            raise ValueError('Invalid DATABASE_URL format')

    @field_validator('REDIS_URL')
    def validate_redis_url(cls, v: str) -> str:
        try:
            result = urlparse(v)
            assert all([result.scheme, result.netloc])
            return v
        except:
            raise ValueError('Invalid REDIS_URL format')

    @field_validator('MONGODB_URI')
    def validate_mongodb_uri(cls, v: str) -> str:
        try:
            result = urlparse(v)
            assert all([result.scheme, result.netloc])
            return v
        except:
            raise ValueError('Invalid MONGODB_URI format')

    @field_validator('ENVIRONMENT')
    def validate_environment(cls, v: str) -> str:
        allowed = {'development', 'testing', 'production'}
        if v.lower() not in allowed:
            raise ValueError(f'ENVIRONMENT must be one of: {", ".join(allowed)}')
        return v.lower()

    @field_validator('SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY')
    def validate_supabase_config(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if info.data.get('ENVIRONMENT') == 'production':
            if not v:
                raise ValueError(f'{info.field_name} is required in production environment')
        return v

def validate_environment():
    """Validate all environment variables on application startup"""
    try:
        # Get environment variables with defaults for missing values
        env_vars = {}
        for key in EnvironmentValidator.__annotations__.keys():
            value = os.getenv(key)
            if value is not None:
                # Convert ACCESS_TOKEN_EXPIRE_MINUTES to int and DEBUG to bool
                if key == 'ACCESS_TOKEN_EXPIRE_MINUTES' and value:
                    value = int(value)
                elif key == 'DEBUG':
                    value = value.lower() in ('true', '1', 't', 'yes')
                env_vars[key] = value

        validator = EnvironmentValidator(**env_vars)
        
        # Critical validation for required fields
        if not validator.DATABASE_URL:
            raise ValueError("DATABASE_URL is required")
            
        # Ensure SECRET_KEY is explicitly set in production
        if validator.ENVIRONMENT == 'production':
            if validator.SECRET_KEY == "dev-secret-key-local-development-only":
                raise ValueError("A secure SECRET_KEY must be set in production environment")
            
        # Additional validation for production environment
            if not all([
                validator.SUPABASE_URL,
                validator.SUPABASE_ANON_KEY,
                validator.SUPABASE_SERVICE_ROLE_KEY
            ]):
                raise ValueError("Supabase configuration is required in production environment")
        
        return validator
    except Exception as e:
        raise ValueError(f"Environment validation failed: {str(e)}")
