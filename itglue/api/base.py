"""Base API Resource Class

Provides common functionality for all ITGlue API resource endpoints including
CRUD operations, pagination handling, error management, and response processing.
"""

import logging
from typing import Dict, List, Optional, TypeVar, Generic, Union, Any, Type, Callable
from urllib.parse import urljoin, urlencode
import structlog

from ..http_client import ITGlueHTTPClient
from ..models.base import ITGlueResource, ITGlueResourceCollection, ResourceType
from ..pagination import PaginatedResponse, PaginationHandler
from ..exceptions import ITGlueValidationError, ITGlueNotFoundError, ITGlueAPIError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=ITGlueResource)


class BaseAPI(Generic[T]):
    """Base class for all ITGlue API resource endpoints.

    Provides common CRUD operations, pagination handling, and response processing
    for any ITGlue resource type. Subclasses should specify the resource type
    and provide endpoint-specific customizations.

    Args:
        client: Authenticated ITGlue HTTP client
        resource_type: The ITGlue resource type this API handles
        model_class: Pydantic model class for this resource
        endpoint_path: Base endpoint path (e.g., 'organizations')
    """

    def __init__(
        self,
        client: ITGlueHTTPClient,
        resource_type: ResourceType,
        model_class: Type[T],
        endpoint_path: str,
    ):
        self.client = client
        self.resource_type = resource_type
        self.model_class = model_class
        self.endpoint_path = endpoint_path
        self.base_url = f"/{endpoint_path}"
        self.logger = structlog.get_logger().bind(component=self.__class__.__name__)

    def _build_url(self, resource_id: Optional[str] = None, subpath: str = "") -> str:
        """Build complete URL for API endpoint.

        Args:
            resource_id: Optional resource ID for specific resource operations
            subpath: Additional path components

        Returns:
            Complete URL path for the endpoint
        """
        url = self.base_url
        if resource_id:
            url = f"{url}/{resource_id}"
        if subpath:
            url = f"{url}/{subpath.lstrip('/')}"
        return url

    def _build_query_params(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        sort: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """Build query parameters for API requests.

        Args:
            page: Page number for pagination
            per_page: Number of items per page
            sort: Sort field and direction (e.g., 'name', '-created_at')
            filter_params: Dictionary of filter parameters
            include: List of related resources to include
            **kwargs: Additional query parameters

        Returns:
            Dictionary of query parameters
        """
        params = {}

        # Pagination
        if page is not None:
            params["page[number]"] = str(page)
        if per_page is not None:
            params["page[size]"] = str(per_page)

        # Sorting
        if sort:
            params["sort"] = sort

        # Filters
        if filter_params:
            for key, value in filter_params.items():
                if value is not None:
                    if isinstance(value, (list, tuple)):
                        # Multiple values for same filter
                        params[f"filter[{key}]"] = ",".join(str(v) for v in value)
                    else:
                        params[f"filter[{key}]"] = str(value)

        # Includes (JSON API side-loading)
        if include:
            params["include"] = ",".join(include)

        # Additional parameters
        params.update({k: str(v) for k, v in kwargs.items() if v is not None})

        return params

    def _process_response(
        self, response_data: Dict[str, Any], is_collection: bool = False
    ) -> Union[T, ITGlueResourceCollection[T]]:
        """Process API response into model instances.

        Args:
            response_data: Raw JSON response from API
            is_collection: Whether response contains multiple resources

        Returns:
            Model instance or collection of model instances

        Raises:
            ITGlueValidationError: If response data is invalid
        """
        try:
            if is_collection:
                # Collection response
                items = []
                for item_data in response_data.get("data", []):
                    item = self.model_class.from_api_dict(item_data)
                    items.append(item)

                # Create collection with pagination metadata
                collection = ITGlueResourceCollection[self.model_class](
                    data=items,
                    meta=response_data.get("meta", {}),
                    links=response_data.get("links", {}),
                    included=response_data.get("included", []),
                )
                return collection
            else:
                # Single resource response
                resource_data = response_data.get("data")
                if not resource_data:
                    raise ITGlueValidationError("No data in response")
                return self.model_class.from_api_dict(resource_data)

        except Exception as e:
            logger.error(f"Failed to process {self.resource_type.value} response: {e}")
            raise ITGlueValidationError(f"Invalid response format: {e}")

    async def get(
        self, resource_id: str, include: Optional[List[str]] = None, **kwargs
    ) -> T:
        """Get a single resource by ID.

        Args:
            resource_id: Resource ID to retrieve
            include: List of related resources to include
            **kwargs: Additional query parameters

        Returns:
            Resource model instance

        Raises:
            ITGlueNotFoundError: If resource doesn't exist
            ITGlueAPIError: If API request fails
        """
        logger.info(f"Getting {self.resource_type.value} {resource_id}")

        url = self._build_url(resource_id)
        params = self._build_query_params(include=include, **kwargs)

        try:
            response = await self.client.get(url, params=params)
            return self._process_response(response, is_collection=False)
        except ITGlueAPIError as e:
            if e.status_code == 404:
                raise ITGlueNotFoundError(
                    f"{self.resource_type.value.title()} {resource_id} not found"
                )
            raise

    async def list(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        sort: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
        **kwargs,
    ) -> ITGlueResourceCollection[T]:
        """List resources with optional filtering and pagination.

        Args:
            page: Page number for pagination
            per_page: Number of items per page
            sort: Sort field and direction (e.g., 'name', '-created_at')
            filter_params: Dictionary of filter parameters
            include: List of related resources to include
            **kwargs: Additional query parameters

        Returns:
            Collection of resource model instances
        """
        logger.info(f"Listing {self.resource_type.value}")

        url = self._build_url()
        params = self._build_query_params(
            page=page,
            per_page=per_page,
            sort=sort,
            filter_params=filter_params,
            include=include,
            **kwargs,
        )

        response = await self.client.get(url, params=params)
        return self._process_response(response, is_collection=True)

    async def list_all(
        self,
        per_page: Optional[int] = None,
        sort: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
        **kwargs,
    ) -> ITGlueResourceCollection[T]:
        """List all resources by automatically handling pagination.

        Args:
            per_page: Number of items per page (default: client default)
            sort: Sort field and direction
            filter_params: Dictionary of filter parameters
            include: List of related resources to include
            **kwargs: Additional query parameters

        Returns:
            Collection containing all resources across all pages
        """
        logger.info(f"Listing all {self.resource_type.value}")

        url = self._build_url()
        params = self._build_query_params(
            per_page=per_page,
            sort=sort,
            filter_params=filter_params,
            include=include,
            **kwargs,
        )

        # Use pagination handler to get all pages
        pagination_handler = PaginationHandler(self.client)
        paginated_response = await pagination_handler.get_all_pages(url, params)

        # Process the aggregated response
        return self._process_response(paginated_response.to_dict(), is_collection=True)

    async def create(self, data: Union[T, Dict[str, Any]], **kwargs) -> T:
        """Create a new resource.

        Args:
            data: Resource data as model instance or dictionary
            **kwargs: Additional query parameters

        Returns:
            Created resource model instance

        Raises:
            ITGlueValidationError: If data is invalid
            ITGlueAPIError: If API request fails
        """
        logger.info(f"Creating {self.resource_type.value}")

        # Convert model to API format if needed
        if isinstance(data, self.model_class):
            request_data = data.to_api_dict()
        else:
            # Validate and wrap raw dictionary data
            try:
                model_instance = self.model_class(**data)
                request_data = model_instance.to_api_dict()
            except Exception as e:
                raise ITGlueValidationError(
                    f"Invalid {self.resource_type.value} data: {e}"
                )

        url = self._build_url()
        params = self._build_query_params(**kwargs)

        response = await self.client.post(url, json=request_data, params=params)
        return self._process_response(response, is_collection=False)

    async def update(
        self, resource_id: str, data: Union[T, Dict[str, Any]], **kwargs
    ) -> T:
        """Update an existing resource.

        Args:
            resource_id: ID of resource to update
            data: Updated resource data as model instance or dictionary
            **kwargs: Additional query parameters

        Returns:
            Updated resource model instance

        Raises:
            ITGlueNotFoundError: If resource doesn't exist
            ITGlueValidationError: If data is invalid
            ITGlueAPIError: If API request fails
        """
        logger.info(f"Updating {self.resource_type.value} {resource_id}")

        # Convert model to API format if needed
        if isinstance(data, self.model_class):
            request_data = data.to_api_dict()
        else:
            # For updates, we might want partial data validation
            request_data = {
                "data": {
                    "type": self.resource_type.value,
                    "id": str(resource_id),
                    "attributes": data,
                }
            }

        url = self._build_url(resource_id)
        params = self._build_query_params(**kwargs)

        try:
            response = await self.client.patch(url, json=request_data, params=params)
            return self._process_response(response, is_collection=False)
        except ITGlueAPIError as e:
            if e.status_code == 404:
                raise ITGlueNotFoundError(
                    f"{self.resource_type.value.title()} {resource_id} not found"
                )
            raise

    async def delete(self, resource_id: str, **kwargs) -> None:
        """Delete a resource.

        Args:
            resource_id: ID of resource to delete
            **kwargs: Additional query parameters

        Raises:
            ITGlueNotFoundError: If resource doesn't exist
            ITGlueAPIError: If API request fails
        """
        logger.info(f"Deleting {self.resource_type.value} {resource_id}")

        url = self._build_url(resource_id)
        params = self._build_query_params(**kwargs)

        try:
            await self.client.delete(url, params=params)
            logger.info(
                f"Successfully deleted {self.resource_type.value} {resource_id}"
            )
        except ITGlueAPIError as e:
            if e.status_code == 404:
                raise ITGlueNotFoundError(
                    f"{self.resource_type.value.title()} {resource_id} not found"
                )
            raise

    async def search(
        self,
        query: str,
        filter_params: Optional[Dict[str, Any]] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs,
    ) -> ITGlueResourceCollection[T]:
        """Search resources using a query string.

        Args:
            query: Search query string
            filter_params: Additional filter parameters
            page: Page number for pagination
            per_page: Number of items per page
            **kwargs: Additional query parameters

        Returns:
            Collection of matching resource model instances
        """
        logger.info(f"Searching {self.resource_type.value} for: {query}")

        # Add search query to filter parameters
        search_filters = filter_params or {}
        search_filters["name"] = query  # Most resources support name searching

        return await self.list(
            page=page, per_page=per_page, filter_params=search_filters, **kwargs
        )

    def get_by_id(self, resource_id: str, params: Optional[Dict[str, str]] = None) -> Optional[T]:
        """Get a single resource by ID."""
        endpoint = self._build_url(resource_id)
        self.logger.info("Getting resource by ID", resource_id=resource_id)
        
        try:
            response = self.client.get(endpoint, params=params or {})
            
            if response and "data" in response:
                return self.model_class.from_api_dict(response["data"])
            return None
            
        except Exception as e:
            self.logger.error("Failed to get resource", resource_id=resource_id, error=str(e))
            raise

    def get_all(self, params: Optional[Dict[str, str]] = None, **kwargs) -> List[T]:
        """Get all resources with pagination."""
        endpoint = self._build_url()
        self.logger.info("Getting all resources", params=params)
        
        try:
            response = self.client.get(endpoint, params=params or {})
            
            if response and "data" in response:
                all_data = response["data"]
                if isinstance(all_data, list):
                    return [self.model_class.from_api_dict(item) for item in all_data]
                else:
                    return [self.model_class.from_api_dict(all_data)]
            return []
            
        except Exception as e:
            self.logger.error("Failed to get all resources", error=str(e))
            raise

    def create(self, data: Dict[str, Any], params: Optional[Dict[str, str]] = None) -> Optional[T]:
        """Create a new resource."""
        endpoint = self._build_url()
        self.logger.info("Creating resource", data=data)
        
        try:
            response = self.client.post(endpoint, data=data, params=params or {})
            
            if response and "data" in response:
                return self.model_class.from_api_dict(response["data"])
            return None
            
        except Exception as e:
            self.logger.error("Failed to create resource", error=str(e))
            raise

    def update(self, resource_id: str, data: Dict[str, Any], params: Optional[Dict[str, str]] = None) -> Optional[T]:
        """Update an existing resource."""
        endpoint = self._build_url(resource_id)
        self.logger.info("Updating resource", resource_id=resource_id, data=data)
        
        try:
            response = self.client.patch(endpoint, data=data, params=params or {})
            
            if response and "data" in response:
                return self.model_class.from_api_dict(response["data"])
            return None
            
        except Exception as e:
            self.logger.error("Failed to update resource", resource_id=resource_id, error=str(e))
            raise
