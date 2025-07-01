from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class TurnUpSpotException(Exception):
    """Base exception for TurnUp Spot application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserNotFoundException(TurnUpSpotException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message, 404)


class GroupNotFoundException(TurnUpSpotException):
    def __init__(self, message: str = "Group not found"):
        super().__init__(message, 404)


class EventNotFoundException(TurnUpSpotException):
    def __init__(self, message: str = "Event not found"):
        super().__init__(message, 404)


class UnauthorizedException(TurnUpSpotException):
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, 401)


class ForbiddenException(TurnUpSpotException):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, 403)


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(TurnUpSpotException)
    async def turnupspot_exception_handler(request: Request, exc: TurnUpSpotException):
        logger.error(f"TurnUpSpot exception: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "type": "TurnUpSpotException"}
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(f"HTTP exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "type": "HTTPException"}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "type": "ValidationError"}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": "InternalServerError"}
        )