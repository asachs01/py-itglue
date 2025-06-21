"""
ITGlue Client

Main client class for interacting with the ITGlue API.
Integrates HTTP client, pagination, caching, and provides high-level API interface.
"""

import structlog
from typing import Any, Dict, List, Optional, Generator

from .config import ITGlueConfig
from .http_client import ITGlueHTTPClient
from .pagination import PaginationHandler, PaginatedResponse
from .cache import CacheManager


class ITGlueClient:
    """Main client for ITGlue API interactions."""
    
    def __init__(self, config: Optional[ITGlueConfig] = None):
        """Initialize the ITGlue client."""
        self.config = config or ITGlueConfig.from_environment()
        
        # Validate configuration
        self.config.validate()
        
        # Initialize logger
        self.logger = structlog.get_logger().bind(component="itglue_client")
        
        # Initialize components
        self.http_client = ITGlueHTTPClient(self.config)
        self.pagination = PaginationHandler(self.http_client)
        self.cache = CacheManager(self.config)
        
        self.logger.info(
            "ITGlue client initialized",
            base_url=self.config.base_url,
            cache_enabled=self.config.enable_caching,
            rate_limiting=f"{self.config.requests_per_minute}/min"
        )
    
    @classmethod
    def from_environment(cls) -> "ITGlueClient":
        """Create client from environment variables."""
        return cls(ITGlueConfig.from_environment())
    
    def _get_cached_or_fetch(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Get data from cache or fetch from API."""
        # Check cache first (unless force refresh or non-GET method)
        if not force_refresh and method == "GET":
            cached_data = self.cache.get(endpoint, params, method)
            if cached_data:
                return cached_data
        
        # Fetch from API
        if method == "GET":
            response_data = self.http_client.get(endpoint, params)
        elif method == "POST":
            response_data = self.http_client.post(endpoint, json_data=params)
        elif method == "PATCH":
            response_data = self.http_client.patch(endpoint, json_data=params)
        elif method == "DELETE":
            response_data = self.http_client.delete(endpoint)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Cache the response (only for GET requests)
        if method == "GET":
            self.cache.set(endpoint, response_data, params)
        
        return response_data
    
    # High-level API methods
    
    def get_resource(
        self,
        endpoint: str,
        resource_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Get a single resource or list of resources."""
        if resource_id:
            endpoint = f"{endpoint}/{resource_id}"
        
        return self._get_cached_or_fetch(endpoint, params, force_refresh=force_refresh)
    
    def get_resource_page(
        self,
        endpoint: str,
        page: int = 1,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False
    ) -> PaginatedResponse:
        """Get a specific page of resources."""
        if not force_refresh:
            # Try to get from cache first
            cache_params = params.copy() if params else {}
            cache_params.update({
                'page[number]': page
            })
            if page_size:
                cache_params['page[size]'] = page_size
            
            cached_data = self.cache.get(endpoint, cache_params)
            if cached_data:
                return self.pagination.parse_response(cached_data)
        
        # Fetch from API
        return self.pagination.get_page(endpoint, page, page_size, params)
    
    def get_all_resources(
        self,
        endpoint: str,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all resources from all pages."""
        return self.pagination.get_all_pages(
            endpoint, page_size, params, max_pages
        )
    
    def iterate_resources(
        self,
        endpoint: str,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Iterate over all resources across pages."""
        return self.pagination.iterate_items(
            endpoint, page_size, params, max_pages
        )
    
    def iterate_pages(
        self,
        endpoint: str,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None
    ) -> Generator[PaginatedResponse, None, None]:
        """Iterate over pages of resources."""
        return self.pagination.iterate_pages(
            endpoint, page_size, params, max_pages
        )
    
    def create_resource(
        self,
        endpoint: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new resource."""
        response = self.http_client.post(endpoint, json_data=data)
        
        # Invalidate related cache entries
        self.cache.invalidate_endpoint(endpoint)
        
        return response
    
    def update_resource(
        self,
        endpoint: str,
        resource_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing resource."""
        full_endpoint = f"{endpoint}/{resource_id}"
        response = self.http_client.patch(full_endpoint, json_data=data)
        
        # Invalidate related cache entries
        self.cache.invalidate_endpoint(endpoint)
        self.cache.delete(full_endpoint)
        
        return response
    
    def delete_resource(
        self,
        endpoint: str,
        resource_id: str
    ) -> Dict[str, Any]:
        """Delete a resource."""
        full_endpoint = f"{endpoint}/{resource_id}"
        response = self.http_client.delete(full_endpoint)
        
        # Invalidate related cache entries
        self.cache.invalidate_endpoint(endpoint)
        self.cache.delete(full_endpoint)
        
        return response
    
    # Utility methods
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.logger.info("Cleared all cache data")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics (if available)."""
        if hasattr(self.cache.backend, 'cache'):
            return {
                'cache_enabled': self.config.enable_caching,
                'cache_backend': self.config.cache_type,
                'cache_size': len(self.cache.backend.cache),
                'cache_max_size': getattr(self.cache.backend, 'max_size', None)
            }
        return {
            'cache_enabled': self.config.enable_caching,
            'cache_backend': self.config.cache_type
        }
    
    def test_connection(self) -> bool:
        """Test connection to ITGlue API."""
        try:
            # Try to fetch a simple endpoint
            response = self.get_resource('/organizations', params={'page[size]': 1})
            return True
        except Exception as e:
            self.logger.error("Connection test failed", error=str(e))
            return False
    
    def close(self) -> None:
        """Close the client and clean up resources."""
        self.http_client.close()
        self.logger.info("ITGlue client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ITGlueClient(base_url='{self.config.base_url}')" 