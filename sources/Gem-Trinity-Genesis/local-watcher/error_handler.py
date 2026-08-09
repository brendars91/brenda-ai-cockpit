"""
Centralized Error Handler for Gem Trinity Genesis
Provides consistent error responses and logging.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(AppError):
    """Input validation error."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class NotFoundError(AppError):
    """Resource not found error."""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} not found: {identifier}",
            "NOT_FOUND", 
            404,
            {"resource": resource, "identifier": identifier}
        )


class RateLimitError(AppError):
    """Rate limit exceeded error."""
    def __init__(self, limit: int, window: str):
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window}",
            "RATE_LIMIT_EXCEEDED",
            429,
            {"limit": limit, "window": window}
        )


class ExternalServiceError(AppError):
    """External service (LLM, API) error."""
    def __init__(self, service: str, original_error: str):
        super().__init__(
            f"External service error: {service}",
            "EXTERNAL_SERVICE_ERROR",
            502,
            {"service": service, "original_error": original_error}
        )


def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized error response."""
    content = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    if request_id:
        content["error"]["request_id"] = request_id
    
    return JSONResponse(status_code=status_code, content=content)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle custom application errors."""
    logger.error(
        f"AppError: {exc.error_code} - {exc.message}",
        extra={"details": exc.details, "path": request.url.path}
    )
    return create_error_response(
        exc.status_code,
        exc.error_code,
        exc.message,
        exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(
        f"HTTPException: {exc.status_code} - {exc.detail}",
        extra={"path": request.url.path}
    )
    return create_error_response(
        exc.status_code,
        f"HTTP_{exc.status_code}",
        str(exc.detail)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error on {request.url.path}",
        extra={"errors": errors}
    )
    
    return create_error_response(
        422,
        "VALIDATION_ERROR",
        "Request validation failed",
        {"errors": errors}
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    error_id = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    
    logger.critical(
        f"Unhandled exception [{error_id}]: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    return create_error_response(
        500,
        "INTERNAL_ERROR",
        "An unexpected error occurred",
        {"error_id": error_id}
    )


def register_error_handlers(app):
    """Register all error handlers with FastAPI app."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
