"""
Global Error Handler Middleware

Handles all exceptions and provides consistent, user-friendly error responses.
Includes comprehensive logging and error tracking.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError as PydanticValidationError
import logging
import traceback
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Import custom exceptions
from backend.core.exceptions import (
    BaseAPIException,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ValidationError,
    DatabaseError,
    ExternalServiceError,
    RateLimitExceededError
)

# Setup logging
logger = logging.getLogger(__name__)

# Create logs directory if it doesn't exist
log_dir = Path("backend/logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Setup file handler for errors
error_log_handler = logging.FileHandler(log_dir / "errors.log")
error_log_handler.setLevel(logging.ERROR)
error_log_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger.addHandler(error_log_handler)


class APIError(Exception):
    """
    Legacy API Error Exception (kept for backward compatibility)
    """
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}


def create_error_response(
    status_code: int,
    message: str,
    error_code: str,
    details: Optional[Dict[str, Any]] = None,
    path: Optional[str] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized error response
    """
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if path:
        response["error"]["path"] = path
    
    if request_id:
        response["error"]["request_id"] = request_id
    
    # Add helpful hints for common errors
    if status_code == 401:
        response["error"]["hint"] = "Please check your authentication credentials"
    elif status_code == 403:
        response["error"]["hint"] = "You don't have permission to access this resource"
    elif status_code == 404:
        response["error"]["hint"] = "The requested resource was not found"
    elif status_code == 422:
        response["error"]["hint"] = "Please check your input data for errors"
    elif status_code == 429:
        response["error"]["hint"] = "Too many requests. Please try again later"
    elif status_code >= 500:
        response["error"]["hint"] = "An internal error occurred. Please try again or contact support"
    
    return response


def log_error(
    exc: Exception,
    request: Request,
    status_code: int,
    include_traceback: bool = True
):
    """
    Log error with context information
    """
    error_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": str(request.url),
        "client": request.client.host if request.client else "unknown",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "status_code": status_code
    }
    
    # Log based on severity
    if status_code >= 500:
        logger.error(f"Server Error: {error_info}", exc_info=include_traceback)
    elif status_code >= 400:
        logger.warning(f"Client Error: {error_info}")
    else:
        logger.info(f"Error: {error_info}")
    
    # Log full traceback for server errors
    if include_traceback and status_code >= 500:
        logger.error(f"Traceback: {traceback.format_exc()}")


async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """
    Handler for custom BaseAPIException and its subclasses
    """
    log_error(exc, request, exc.status_code, include_traceback=False)
    
    response = create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details,
        path=str(request.url)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response
    )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    Handler for legacy APIError (backward compatibility)
    """
    log_error(exc, request, exc.status_code, include_traceback=False)
    
    response = create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_code="API_ERROR",
        details=exc.details,
        path=str(request.url)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for Pydantic request validation errors
    """
    log_error(exc, request, status.HTTP_422_UNPROCESSABLE_ENTITY, include_traceback=False)
    
    # Format validation errors in a user-friendly way
    formatted_errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        formatted_errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    response = create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation error in request data",
        error_code="VALIDATION_ERROR",
        details={"errors": formatted_errors},
        path=str(request.url)
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response
    )


async def pydantic_validation_error_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    """
    Handler for Pydantic validation errors
    """
    log_error(exc, request, status.HTTP_422_UNPROCESSABLE_ENTITY, include_traceback=False)
    
    response = create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Data validation error",
        error_code="VALIDATION_ERROR",
        details={"errors": exc.errors()},
        path=str(request.url)
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response
    )


async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for SQLAlchemy database errors
    """
    log_error(exc, request, status.HTTP_500_INTERNAL_SERVER_ERROR, include_traceback=True)
    
    # Check for specific database errors
    if isinstance(exc, IntegrityError):
        message = "Database integrity constraint violated"
        error_code = "DATABASE_INTEGRITY_ERROR"
        status_code = status.HTTP_409_CONFLICT
    else:
        message = "Database operation failed"
        error_code = "DATABASE_ERROR"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    response = create_error_response(
        status_code=status_code,
        message=message,
        error_code=error_code,
        details={"type": type(exc).__name__},
        path=str(request.url)
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for all other unhandled exceptions
    """
    log_error(exc, request, status.HTTP_500_INTERNAL_SERVER_ERROR, include_traceback=True)
    
    # In production, don't expose internal error details
    is_production = sys.argv[0].endswith('gunicorn') or 'production' in sys.argv
    
    details = {} if is_production else {
        "type": type(exc).__name__,
        "message": str(exc)
    }
    
    response = create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred",
        error_code="INTERNAL_SERVER_ERROR",
        details=details,
        path=str(request.url)
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response
    )


def setup_error_handlers(app: FastAPI):
    """
    Setup all error handlers for the FastAPI application
    """
    # Custom exception handlers (most specific first)
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    app.add_exception_handler(APIError, api_error_handler)
    
    # Validation error handlers
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(PydanticValidationError, pydantic_validation_error_handler)
    
    # Database error handler
    app.add_exception_handler(SQLAlchemyError, database_error_handler)
    
    # Catch-all handler (must be last)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured successfully")
