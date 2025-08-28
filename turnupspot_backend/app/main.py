from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
from .celery_app import celery_app

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.exceptions import setup_exception_handlers
from app.core.env_validator import validate_environment
from app.seed_sports import seed_sports

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up TurnUp Spot API...")
    # Validate environment variables
    validate_environment()
    # If seed_sports is synchronous, run it in a threadpool to avoid blocking
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, seed_sports)
    
    yield
    # Shutdown
    print("Shutting down TurnUp Spot API...")


app = FastAPI(
    title="TurnUp Spot API",
    description="Backend API for TurnUp Spot - Events, Sports, and Vendor Management Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)




# Security middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["turnupspot.com", "*.turnupspot.com", "localhost", "*.turnupspot-api.onrender.com", "turnupspot-api.onrender.com"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception handlers
setup_exception_handlers(app)

# API routes
app.include_router(api_router, prefix="/api/v1")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {
        "message": "Welcome to TurnUp Spot API",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Contact admin for API documentation"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )