"""
ITGlue SDK Exception Classes

Comprehensive error handling for all ITGlue API interactions.
"""

from typing import Any, Dict, Optional


class ITGlueError(Exception):
    """Base exception class for all ITGlue SDK errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ITGlueAPIError(ITGlueError):
    """Exception raised for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.response_body = response_body


class ITGlueAuthError(ITGlueAPIError):
    """Exception raised for authentication-related errors."""

    pass


class ITGlueValidationError(ITGlueError):
    """Exception raised for data validation errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.field = field
        self.value = value


class ITGlueRateLimitError(ITGlueAPIError):
    """Exception raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after


class ITGlueNotFoundError(ITGlueAPIError):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code=404, details=details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ITGlueConnectionError(ITGlueError):
    """Exception raised for connection-related errors."""

    pass


class ITGlueTimeoutError(ITGlueError):
    """Exception raised for timeout-related errors."""

    pass


class ITGlueCacheError(ITGlueError):
    """Exception raised for cache-related errors."""

    pass


class ITGlueBulkOperationError(ITGlueError):
    """Exception raised for bulk operation errors."""

    def __init__(
        self,
        message: str,
        successful_operations: int = 0,
        failed_operations: int = 0,
        errors: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.successful_operations = successful_operations
        self.failed_operations = failed_operations
        self.errors = errors or []
