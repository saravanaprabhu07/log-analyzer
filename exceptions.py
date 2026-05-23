"""
Custom Exception Classes for Intelligent Log Analyzer
Provides structured error handling with proper HTTP status codes
"""

from fastapi import HTTPException, status
from typing import Any, Optional, Dict


class AppException(Exception):
    """Base exception class for all application errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Raised when input validation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class FileUploadError(AppException):
    """Raised when file upload fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_UPLOAD_ERROR",
            details=details,
        )


class FileSizeExceeded(FileUploadError):
    """Raised when uploaded file exceeds maximum size"""

    def __init__(self, max_size_mb: int):
        super().__init__(
            message=f"File size exceeds maximum allowed size of {max_size_mb}MB",
            details={"max_size_mb": max_size_mb},
        )


class InvalidFileFormat(FileUploadError):
    """Raised when file format is not allowed"""

    def __init__(self, filename: str, allowed_extensions: list):
        super().__init__(
            message=f"File '{filename}' has invalid format. Allowed: {', '.join(allowed_extensions)}",
            details={"allowed_extensions": allowed_extensions},
        )


class ParsingError(AppException):
    """Raised when log parsing fails"""

    def __init__(self, message: str, line_number: Optional[int] = None):
        details = {}
        if line_number:
            details["line_number"] = line_number
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="PARSING_ERROR",
            details=details,
        )


class DatabaseError(AppException):
    """Raised when database operations fail"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
        )


class ResourceNotFound(AppException):
    """Raised when requested resource is not found"""

    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            message=f"{resource_type} with ID {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class RateLimitExceeded(AppException):
    """Raised when rate limit is exceeded"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after},
        )


class AuthenticationError(AppException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(AppException):
    """Raised when user lacks required permissions"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
        )


def get_http_exception(app_exception: AppException) -> HTTPException:
    """Convert AppException to HTTPException for FastAPI"""
    return HTTPException(
        status_code=app_exception.status_code,
        detail={
            "error": app_exception.error_code,
            "message": app_exception.message,
            "details": app_exception.details,
        },
    )
