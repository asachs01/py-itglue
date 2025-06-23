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
        self.current_page = meta.get("current-page", 1)
        self.next_page = meta.get("next-page")
        self.prev_page = meta.get("prev-page")
        self.total_pages = meta.get("total-pages", 1)
        self.total_count = meta.get("total-count", 0)

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

    def __init__(
        self,
        data: List[Dict[str, Any]],
        meta: Dict[str, Any],
        links: Optional[Dict[str, Any]] = None,
    ):
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

        data = response_data.get("data", [])
        meta = response_data.get("meta", {})
        links = response_data.get("links", {})

        if not isinstance(data, list):
            # Single item response - wrap in list
            data = [data] if data else []

        return PaginatedResponse(data, meta, links)

    def get_page(self, page: Optional[int] = None) -> Dict[str, Any]:
        """Get specific page."""
        if page is None:
            page = 1
        
        params = self.build_params()
        params["page[number]"] = page
        
        response = self.http_client.get(self.endpoint, params=params)
        return response

    def get_next_page(self) -> Optional[Dict[str, Any]]:
        """Get next page of results."""
        if not self.has_next_page():
            return None
        
        next_page = self.current_page + 1 if self.current_page else 1
        return self.get_page(next_page)

    def get_prev_page(
        self,
        current_response: PaginatedResponse,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[PaginatedResponse]:
        """Get the previous page based on current response."""
        if not current_response.pagination.has_prev:
            return None

        return self.get_page(
            current_response.pagination.prev_page,
        )

    def get_all_pages(self) -> List[Dict[str, Any]]:
        """Get all pages of results."""
        all_data = []
        page_num = 1
        
        while True:
            response = self.get_page(page_num)
            if not response or "data" not in response:
                break
                
            all_data.extend(response["data"])
            
            # Check if there are more pages
            meta = response.get("meta", {})
            if not meta.get("has-next-page", False):
                break
                
            page_num += 1
            
        return all_data

    def iterate_pages(
        self,
        endpoint: str,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None,
    ) -> Generator[PaginatedResponse, None, None]:
        """Generator that yields each page as PaginatedResponse."""
        page = 1
        pages_yielded = 0

        self.logger.info(
            "Starting page iteration",
            endpoint=endpoint,
            page_size=page_size,
            max_pages=max_pages,
        )

        while True:
            if max_pages and pages_yielded >= max_pages:
                self.logger.warning(
                    "Reached max pages limit in iteration",
                    pages_yielded=pages_yielded,
                    max_pages=max_pages,
                )
                break

            response = self.get_page(page)
            yield response
            pages_yielded += 1

            if not response.pagination.has_next:
                break

            page = response.pagination.next_page

        self.logger.info("Completed page iteration", pages_yielded=pages_yielded)

    def iterate_items(
        self,
        endpoint: str,
        page_size: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Generator that yields individual items from all pages."""
        for page_response in self.iterate_pages(endpoint, page_size, params, max_pages):
            for item in page_response.data:
                yield item

    def get_current_page_info(self) -> Dict[str, Any]:
        """Get current page information from last response."""
        if not self.last_response:
            return {}
            
        meta = self.last_response.get("meta", {})
        return {
            "current_page": meta.get("current-page", 1),
            "total_pages": meta.get("total-pages", 1),
            "total_count": meta.get("total-count", 0),
            "per_page": meta.get("per-page", 50),
            "has_next_page": meta.get("has-next-page", False),
            "has_prev_page": meta.get("has-prev-page", False),
        }
