"""
ITGlue Pagination Handler

Handles pagination for ITGlue API responses following JSON API specification.
Supports both automatic pagination (fetch all) and manual pagination control.
"""

from typing import Any, Dict, List, Optional, Iterator, Generator
import structlog

from .exceptions import ITGlueAPIError


class PaginationInfo:
    """Information about current pagination state."""
    
    def __init__(self, meta: Dict[str, Any]):
        self.meta = meta
        
        # Extract pagination info from meta
        self.current_page = meta.get('current-page', 1)
        self.next_page = meta.get('next-page')
        self.prev_page = meta.get('prev-page')
        self.total_pages = meta.get('total-pages', 1)
        self.total_count = meta.get('total-count', 0)
        
    @property
    def has_next(self) -> bool:
        """Check if there are more pages."""
        return self.next_page is not None
    
    @property
    def has_prev(self) -> bool:
        """Check if there are previous pages."""
        return self.prev_page is not None
    
    @property
    def is_first_page(self) -> bool:
        """Check if this is the first page."""
        return self.current_page == 1
    
    @property
    def is_last_page(self) -> bool:
        """Check if this is the last page."""
        return self.current_page == self.total_pages
    
    def __repr__(self) -> str:
        return (
            f"PaginationInfo(current={self.current_page}, "
            f"total={self.total_pages}, count={self.total_count})"
        )


class PaginatedResponse:
    """Represents a paginated API response."""
    
    def __init__(self, data: List[Dict[str, Any]], meta: Dict[str, Any], links: Optional[Dict[str, Any]] = None):
        self.data = data
        self.meta = meta
        self.links = links or {}
        self.pagination = PaginationInfo(meta)
    
    def __len__(self) -> int:
        """Return the number of items in current page."""
        return len(self.data)
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over items in current page."""
        return iter(self.data)
    
    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Get item by index from current page."""
        return self.data[index]
    
    def __repr__(self) -> str:
        return (
            f"PaginatedResponse(items={len(self.data)}, "
            f"pagination={self.pagination})"
        )


class PaginationHandler:
    """Handles pagination for ITGlue API responses."""
    
    def __init__(self, http_client):
        """Initialize with HTTP client for making requests."""
        self.http_client = http_client
        self.logger = structlog.get_logger().bind(component="pagination")
    
    def parse_response(self, response_data: Dict[str, Any]) -> PaginatedResponse:
        """Parse API response into PaginatedResponse object."""
        if not isinstance(response_data, dict):
            raise ITGlueAPIError("Invalid response format: expected dict")
        
        data = response_data.get('data', [])
        meta = response_data.get('meta', {})
        links = response_data.get('links', {})
        
        if not isinstance(data, list):
            # Single item response - wrap in list
            data = [data] if data else []
        
        return PaginatedResponse(data, meta, links)
    
    def get_page(
        self,
        endpoint: str,
        page: int = 1,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponse:
        """Get a specific page of results."""
        params = params or {}
        params.update({
            'page[number]': page
        })
        
        if page_size:
            params['page[size]'] = page_size
        
        self.logger.info(
            "Fetching page",
            endpoint=endpoint,
            page=page,
            page_size=page_size
        )
        
        response_data = self.http_client.get(endpoint, params=params)
        return self.parse_response(response_data)
    
    def get_next_page(
        self,
        current_response: PaginatedResponse,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[PaginatedResponse]:
        """Get the next page based on current response."""
        if not current_response.pagination.has_next:
            return None
        
        return self.get_page(
            endpoint,
            page=current_response.pagination.next_page,
            params=params
        )
    
    def get_prev_page(
        self,
        current_response: PaginatedResponse,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[PaginatedResponse]:
        """Get the previous page based on current response."""
        if not current_response.pagination.has_prev:
            return None
        
        return self.get_page(
            endpoint,
            page=current_response.pagination.prev_page,
            params=params
        )
    
    def get_all_pages(
        self,
        endpoint: str,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all pages and return combined data."""
        all_data = []
        page = 1
        pages_fetched = 0
        
        self.logger.info(
            "Fetching all pages",
            endpoint=endpoint,
            page_size=page_size,
            max_pages=max_pages
        )
        
        while True:
            if max_pages and pages_fetched >= max_pages:
                self.logger.warning(
                    "Reached max pages limit",
                    pages_fetched=pages_fetched,
                    max_pages=max_pages
                )
                break
            
            response = self.get_page(endpoint, page, page_size, params)
            all_data.extend(response.data)
            pages_fetched += 1
            
            self.logger.info(
                "Fetched page",
                page=page,
                items_on_page=len(response.data),
                total_items_so_far=len(all_data),
                total_pages=response.pagination.total_pages
            )
            
            if not response.pagination.has_next:
                break
            
            page = response.pagination.next_page
        
        self.logger.info(
            "Completed fetching all pages",
            total_items=len(all_data),
            pages_fetched=pages_fetched
        )
        
        return all_data
    
    def iterate_pages(
        self,
        endpoint: str,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None
    ) -> Generator[PaginatedResponse, None, None]:
        """Generator that yields each page as PaginatedResponse."""
        page = 1
        pages_yielded = 0
        
        self.logger.info(
            "Starting page iteration",
            endpoint=endpoint,
            page_size=page_size,
            max_pages=max_pages
        )
        
        while True:
            if max_pages and pages_yielded >= max_pages:
                self.logger.warning(
                    "Reached max pages limit in iteration",
                    pages_yielded=pages_yielded,
                    max_pages=max_pages
                )
                break
            
            response = self.get_page(endpoint, page, page_size, params)
            yield response
            pages_yielded += 1
            
            if not response.pagination.has_next:
                break
            
            page = response.pagination.next_page
        
        self.logger.info(
            "Completed page iteration",
            pages_yielded=pages_yielded
        )
    
    def iterate_items(
        self,
        endpoint: str,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Generator that yields individual items from all pages."""
        for page_response in self.iterate_pages(endpoint, page_size, params, max_pages):
            for item in page_response.data:
                yield item 