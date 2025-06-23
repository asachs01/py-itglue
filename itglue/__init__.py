"""
ITGlue Python SDK

A comprehensive Python SDK for the ITGlue API with built-in pagination,
rate limiting, caching, and data validation.
"""

from .version import __version__
from .config import ITGlueConfig, ITGlueRegion
from .client import ITGlueClient
from .http_client import ITGlueHTTPClient
from .pagination import PaginationHandler, PaginatedResponse, PaginationInfo
from .cache import CacheManager
from .exceptions import (
    ITGlueError,
    ITGlueAPIError,
    ITGlueAuthError,
    ITGlueValidationError,
    ITGlueRateLimitError,
    ITGlueNotFoundError,
    ITGlueConnectionError,
    ITGlueTimeoutError,
    ITGlueCacheError,
    ITGlueBulkOperationError,
)
from .models import (
    ITGlueResource,
    ITGlueResourceCollection,
    ResourceType,
    Organization,
    OrganizationCollection,
    Configuration,
    ConfigurationCollection,
)

__all__ = [
    "__version__",
    "ITGlueClient",
    "ITGlueConfig",
    "ITGlueRegion",
    "ITGlueHTTPClient",
    "PaginationHandler",
    "PaginatedResponse",
    "PaginationInfo",
    "CacheManager",
    "ITGlueError",
    "ITGlueAPIError",
    "ITGlueAuthError",
    "ITGlueValidationError",
    "ITGlueRateLimitError",
    "ITGlueNotFoundError",
    "ITGlueConnectionError",
    "ITGlueTimeoutError",
    "ITGlueCacheError",
    "ITGlueBulkOperationError",
    # Models
    "ITGlueResource",
    "ITGlueResourceCollection",
    "ResourceType",
    "Organization",
    "OrganizationCollection",
    "Configuration",
    "ConfigurationCollection",
] 