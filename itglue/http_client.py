"""
ITGlue HTTP Client

Handles all HTTP interactions with the ITGlue API including:
- Authentication
- Rate limiting and retry logic
- Response handling and error management
- Request/response logging
"""

import json
import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin, urlencode

import requests
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from .config import ITGlueConfig
from .exceptions import (
    ITGlueAPIError,
    ITGlueAuthError,
    ITGlueRateLimitError,
    ITGlueNotFoundError,
    ITGlueConnectionError,
    ITGlueTimeoutError,
    ITGlueValidationError,
)


class RateLimiter:
    """Simple rate limiter for ITGlue API requests."""

    def __init__(
        self, requests_per_minute: int = 3000, requests_per_5_minutes: int = 3000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_5_minutes = requests_per_5_minutes
        self.minute_requests = []
        self.five_minute_requests = []

    def wait_if_needed(self) -> None:
        """Wait if rate limits would be exceeded."""
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(current_time)

        # Check minute limit
        if len(self.minute_requests) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.minute_requests[0])
            if wait_time > 0:
                time.sleep(wait_time)
                self._clean_old_requests(time.time())

        # Check 5-minute limit
        if len(self.five_minute_requests) >= self.requests_per_5_minutes:
            wait_time = 300 - (current_time - self.five_minute_requests[0])
            if wait_time > 0:
                time.sleep(wait_time)
                self._clean_old_requests(time.time())

        # Record this request
        current_time = time.time()
        self.minute_requests.append(current_time)
        self.five_minute_requests.append(current_time)

    def _clean_old_requests(self, current_time: float) -> None:
        """Remove old request timestamps."""
        # Remove requests older than 1 minute
        self.minute_requests = [
            req_time
            for req_time in self.minute_requests
            if current_time - req_time < 60
        ]

        # Remove requests older than 5 minutes
        self.five_minute_requests = [
            req_time
            for req_time in self.five_minute_requests
            if current_time - req_time < 300
        ]


class ITGlueHTTPClient:
    """HTTP client for ITGlue API with built-in rate limiting and error handling."""

    def __init__(self, config: ITGlueConfig):
        self.config = config
        self.logger = structlog.get_logger().bind(component="http_client")

        # Set up requests session
        self.session = requests.Session()
        self.session.headers.update(config.get_headers())

        # Set up rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=config.requests_per_minute,
            requests_per_5_minutes=config.requests_per_5_minutes,
        )

        self.logger.info(
            "ITGlue HTTP client initialized",
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    def _make_request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> requests.Response:
        """Make HTTP request with retry logic."""

        @retry(
            stop=stop_after_attempt(self.config.max_retries + 1),
            wait=wait_exponential(
                multiplier=self.config.retry_backoff_factor, min=1, max=60
            ),
            retry=retry_if_exception_type(
                (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    ITGlueRateLimitError,
                    ITGlueConnectionError,
                    ITGlueTimeoutError,
                )
            ),
        )
        def _make_request() -> requests.Response:
            # Apply rate limiting
            self.rate_limiter.wait_if_needed()

            # Set timeout if not provided
            if "timeout" not in kwargs:
                kwargs["timeout"] = self.config.timeout

            # Log request if enabled
            if self.config.log_requests:
                self.logger.info(
                    "Making API request",
                    method=method,
                    url=url,
                    headers=dict(self.session.headers),
                    **{k: v for k, v in kwargs.items() if k != "timeout"},
                )

            try:
                response = self.session.request(method, url, **kwargs)

                # Log response if enabled
                if self.config.log_responses:
                    self.logger.info(
                        "Received API response",
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        content_length=len(response.content),
                    )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    raise ITGlueRateLimitError(
                        f"Rate limit exceeded. Retry after {retry_after} seconds.",
                        retry_after=retry_after,
                    )

                return response

            except requests.exceptions.ConnectionError as e:
                raise ITGlueConnectionError(f"Connection error: {e}")
            except requests.exceptions.Timeout as e:
                raise ITGlueTimeoutError(f"Request timeout: {e}")
            except requests.exceptions.RequestException as e:
                raise ITGlueAPIError(f"Request error: {e}")

        return _make_request()

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and convert to JSON."""
        try:
            # Handle different status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {}  # No content
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise ITGlueValidationError(
                    "Bad request - validation error", details=error_data
                )
            elif response.status_code == 401:
                raise ITGlueAuthError("Unauthorized - check your API key")
            elif response.status_code == 403:
                raise ITGlueAuthError("Forbidden - insufficient permissions")
            elif response.status_code == 404:
                raise ITGlueNotFoundError("Resource not found")
            elif response.status_code == 422:
                error_data = response.json() if response.content else {}
                raise ITGlueValidationError(
                    "Unprocessable entity - validation error", details=error_data
                )
            elif response.status_code == 429:
                # This should be handled by retry logic, but just in case
                retry_after = int(response.headers.get("Retry-After", 60))
                raise ITGlueRateLimitError(
                    "Rate limit exceeded", retry_after=retry_after
                )
            elif response.status_code >= 500:
                raise ITGlueAPIError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            else:
                raise ITGlueAPIError(
                    f"Unexpected status code: {response.status_code}",
                    status_code=response.status_code,
                    response_body=response.text,
                )

        except json.JSONDecodeError as e:
            raise ITGlueAPIError(
                f"Invalid JSON response: {e}",
                status_code=response.status_code,
                response_body=response.text,
            )

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        """Make GET request."""
        url = self.config.get_full_url(endpoint)
        if params:
            url += "?" + urlencode(params, doseq=True)

        response = self._make_request_with_retry("GET", url, **kwargs)
        return self._handle_response(response)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make POST request."""
        url = self.config.get_full_url(endpoint)

        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["data"] = json.dumps(data)
            kwargs["headers"] = kwargs.get("headers", {})
            kwargs["headers"]["Content-Type"] = "application/vnd.api+json"

        response = self._make_request_with_retry("POST", url, **kwargs)
        return self._handle_response(response)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make PATCH request."""
        url = self.config.get_full_url(endpoint)

        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["data"] = json.dumps(data)
            kwargs["headers"] = kwargs.get("headers", {})
            kwargs["headers"]["Content-Type"] = "application/vnd.api+json"

        response = self._make_request_with_retry("PATCH", url, **kwargs)
        return self._handle_response(response)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make DELETE request."""
        url = self.config.get_full_url(endpoint)

        response = self._make_request_with_retry("DELETE", url, **kwargs)
        return self._handle_response(response)

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
        self.logger.info("HTTP client session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
