"""
ITGlue SDK Configuration Management

Handles configuration for different ITGlue regions and environments.
"""

import os
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ITGlueRegion(Enum):
    """ITGlue API regions."""

    US = "https://api.itglue.com"
    EU = "https://api.eu.itglue.com"
    AU = "https://api.au.itglue.com"


@dataclass
class ITGlueConfig:
    """Configuration class for ITGlue SDK."""

    # Authentication
    api_key: str

    # API Configuration
    base_url: str = ITGlueRegion.US.value
    api_version: str = "v1"

    # Request Configuration
    timeout: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 0.3

    # Rate Limiting
    requests_per_minute: int = 3000
    requests_per_5_minutes: int = 3000

    # Pagination
    default_page_size: int = 50
    max_page_size: int = 1000

    # Caching
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes
    cache_type: str = "memory"  # "memory", "redis"
    redis_url: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_requests: bool = False
    log_responses: bool = False

    # Performance
    connection_pool_size: int = 10
    enable_async: bool = True

    # Agent Features
    enable_ai_features: bool = True
    enable_bulk_operations: bool = True
    bulk_batch_size: int = 100

    # Headers
    user_agent: str = "py-itglue/0.1.0"
    custom_headers: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_environment(cls) -> "ITGlueConfig":
        """Create configuration from environment variables."""
        api_key = os.getenv("ITGLUE_API_KEY")
        if not api_key:
            raise ValueError("ITGLUE_API_KEY environment variable is required")

        # Determine region from environment or default to US
        region_env = os.getenv("ITGLUE_REGION", "US").upper()
        try:
            region = ITGlueRegion[region_env]
            base_url = region.value
        except KeyError:
            base_url = os.getenv("ITGLUE_BASE_URL", ITGlueRegion.US.value)

        return cls(
            api_key=api_key,
            base_url=base_url,
            timeout=int(os.getenv("ITGLUE_TIMEOUT", "30")),
            max_retries=int(os.getenv("ITGLUE_MAX_RETRIES", "3")),
            default_page_size=int(os.getenv("ITGLUE_PAGE_SIZE", "50")),
            enable_caching=os.getenv("ITGLUE_ENABLE_CACHING", "true").lower() == "true",
            cache_ttl=int(os.getenv("ITGLUE_CACHE_TTL", "300")),
            cache_type=os.getenv("ITGLUE_CACHE_TYPE", "memory"),
            redis_url=os.getenv("ITGLUE_REDIS_URL"),
            log_level=os.getenv("ITGLUE_LOG_LEVEL", "INFO"),
            log_requests=os.getenv("ITGLUE_LOG_REQUESTS", "false").lower() == "true",
            log_responses=os.getenv("ITGLUE_LOG_RESPONSES", "false").lower() == "true",
            enable_ai_features=os.getenv("ITGLUE_ENABLE_AI", "true").lower() == "true",
            bulk_batch_size=int(os.getenv("ITGLUE_BULK_BATCH_SIZE", "100")),
        )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ITGlueConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "api_version": self.api_version,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_backoff_factor": self.retry_backoff_factor,
            "requests_per_minute": self.requests_per_minute,
            "requests_per_5_minutes": self.requests_per_5_minutes,
            "default_page_size": self.default_page_size,
            "max_page_size": self.max_page_size,
            "enable_caching": self.enable_caching,
            "cache_ttl": self.cache_ttl,
            "cache_type": self.cache_type,
            "redis_url": self.redis_url,
            "log_level": self.log_level,
            "log_requests": self.log_requests,
            "log_responses": self.log_responses,
            "connection_pool_size": self.connection_pool_size,
            "enable_async": self.enable_async,
            "enable_ai_features": self.enable_ai_features,
            "enable_bulk_operations": self.enable_bulk_operations,
            "bulk_batch_size": self.bulk_batch_size,
            "user_agent": self.user_agent,
            "custom_headers": self.custom_headers,
        }

    def get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/vnd.api+json",
            "User-Agent": self.user_agent,
        }
        headers.update(self.custom_headers)
        return headers

    def get_full_url(self, endpoint: str) -> str:
        """Get full URL for an endpoint."""
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("API key is required")

        if not self.base_url:
            raise ValueError("Base URL is required")

        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")

        if self.default_page_size <= 0 or self.default_page_size > self.max_page_size:
            raise ValueError(f"Page size must be between 1 and {self.max_page_size}")

        if self.cache_type == "redis" and not self.redis_url:
            raise ValueError("Redis URL is required when using Redis cache")

        if self.bulk_batch_size <= 0:
            raise ValueError("Bulk batch size must be positive")
