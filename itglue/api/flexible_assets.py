"""
Flexible Assets API for ITGlue.

Provides methods for managing flexible assets, flexible asset types,
and their associated fields through the ITGlue API.
"""

from typing import Optional, Dict, Any, List, Union
import asyncio

from ..models.flexible_asset import (
    FlexibleAsset, 
    FlexibleAssetCollection,
    FlexibleAssetType,
    FlexibleAssetTypeCollection,
    FlexibleAssetField,
    FlexibleAssetFieldCollection,
    FlexibleAssetStatus
)
from ..models.base import ResourceType
from ..exceptions import ITGlueValidationError, ITGlueNotFoundError
from .base import BaseAPI


class FlexibleAssetsAPI(BaseAPI[FlexibleAsset]):
    """
    ITGlue Flexible Assets API client.
    
    Provides methods for managing flexible assets, which are custom data
    structures that can be defined by users to document any type of information.
    """
    
    def __init__(self, client):
        super().__init__(client, ResourceType.FLEXIBLE_ASSETS, FlexibleAsset, "flexible_assets")
    
    # Core CRUD operations (inherited from BaseAPI)
    
    # Specialized flexible asset methods
    
    async def get_by_organization(
        self, 
        organization_id: Union[str, int],
        page: int = 1,
        per_page: int = 50,
        include: Optional[List[str]] = None
    ) -> FlexibleAssetCollection:
        """
        Get flexible assets for a specific organization.
        
        Args:
            organization_id: ID of the organization
            page: Page number for pagination
            per_page: Number of items per page
            include: List of related resources to include
            
        Returns:
            Collection of flexible assets for the organization
        """
        params = {
            "filter[organization_id]": str(organization_id),
            "page[number]": page,
            "page[size]": per_page
        }
        
        if include:
            params["include"] = ",".join(include)
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetCollection.from_api_dict(response)
    
    async def get_by_type(
        self,
        flexible_asset_type_id: Union[str, int],
        organization_id: Optional[Union[str, int]] = None,
        page: int = 1,
        per_page: int = 50
    ) -> FlexibleAssetCollection:
        """
        Get flexible assets of a specific type.
        
        Args:
            flexible_asset_type_id: ID of the flexible asset type
            organization_id: Optional organization filter
            page: Page number for pagination
            per_page: Number of items per page
            
        Returns:
            Collection of flexible assets of the specified type
        """
        params = {
            "filter[flexible_asset_type_id]": str(flexible_asset_type_id),
            "page[number]": page,
            "page[size]": per_page
        }
        
        if organization_id:
            params["filter[organization_id]"] = str(organization_id)
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetCollection.from_api_dict(response)
    
    async def search_by_name(
        self,
        name: str,
        organization_id: Optional[Union[str, int]] = None,
        exact_match: bool = False
    ) -> FlexibleAssetCollection:
        """
        Search flexible assets by name.
        
        Args:
            name: Name to search for
            organization_id: Optional organization filter
            exact_match: Whether to perform exact match (default: partial)
            
        Returns:
            Collection of matching flexible assets
        """
        if exact_match:
            params = {"filter[name]": name}
        else:
            params = {"filter[name]": f"*{name}*"}
        
        if organization_id:
            params["filter[organization_id]"] = str(organization_id)
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetCollection.from_api_dict(response)
    
    async def search_by_trait(
        self,
        trait_name: str,
        trait_value: Optional[str] = None,
        organization_id: Optional[Union[str, int]] = None
    ) -> FlexibleAssetCollection:
        """
        Search flexible assets by trait values.
        
        Args:
            trait_name: Name of the trait to search
            trait_value: Optional value to match (if not provided, searches for existence)
            organization_id: Optional organization filter
            
        Returns:
            Collection of matching flexible assets
        """
        if trait_value:
            params = {f"filter[traits][{trait_name}]": trait_value}
        else:
            params = {f"filter[traits][{trait_name}]": "*"}
        
        if organization_id:
            params["filter[organization_id]"] = str(organization_id)
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetCollection.from_api_dict(response)
    
    async def search_by_tag(
        self,
        tag: str,
        organization_id: Optional[Union[str, int]] = None
    ) -> FlexibleAssetCollection:
        """
        Search flexible assets by tag.
        
        Args:
            tag: Tag to search for
            organization_id: Optional organization filter
            
        Returns:
            Collection of flexible assets with the specified tag
        """
        params = {"filter[tag_list]": tag}
        
        if organization_id:
            params["filter[organization_id]"] = str(organization_id)
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetCollection.from_api_dict(response)
    
    async def list_by_status(
        self,
        status: Union[FlexibleAssetStatus, str],
        organization_id: Optional[Union[str, int]] = None,
        page: int = 1,
        per_page: int = 50
    ) -> FlexibleAssetCollection:
        """
        List flexible assets by status.
        
        Args:
            status: Status to filter by
            organization_id: Optional organization filter
            page: Page number for pagination
            per_page: Number of items per page
            
        Returns:
            Collection of flexible assets with the specified status
        """
        status_value = status.value if isinstance(status, FlexibleAssetStatus) else status
        
        params = {
            "filter[status]": status_value,
            "page[number]": page,
            "page[size]": per_page
        }
        
        if organization_id:
            params["filter[organization_id]"] = str(organization_id)
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetCollection.from_api_dict(response)
    
    async def get_active_assets(
        self,
        organization_id: Optional[Union[str, int]] = None,
        page: int = 1,
        per_page: int = 50
    ) -> FlexibleAssetCollection:
        """
        Get all active flexible assets.
        
        Args:
            organization_id: Optional organization filter
            page: Page number for pagination
            per_page: Number of items per page
            
        Returns:
            Collection of active flexible assets
        """
        return await self.list_by_status(
            FlexibleAssetStatus.ACTIVE,
            organization_id=organization_id,
            page=page,
            per_page=per_page
        )
    
    async def create_flexible_asset(
        self,
        organization_id: Union[str, int],
        flexible_asset_type_id: Union[str, int],
        name: str,
        traits: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> FlexibleAsset:
        """
        Create a new flexible asset.
        
        Args:
            organization_id: ID of the organization
            flexible_asset_type_id: ID of the flexible asset type
            name: Name of the flexible asset
            traits: Dictionary of trait values
            tags: List of tags
            **kwargs: Additional attributes
            
        Returns:
            Created flexible asset
            
        Raises:
            ITGlueValidationError: If required fields are missing or invalid
        """
        if not name or not name.strip():
            raise ITGlueValidationError("Name is required for flexible assets")
        
        data = {
            "type": "flexible_assets",
            "attributes": {
                "name": name.strip(),
                "organization_id": str(organization_id),
                "flexible_asset_type_id": str(flexible_asset_type_id),
                **kwargs
            }
        }
        
        if traits:
            data["attributes"]["traits"] = traits
        
        if tags:
            data["attributes"]["tag_list"] = tags
        
        response = await self.client.post(self._build_url(), {"data": data})
        return FlexibleAsset.from_api_dict(response["data"])
    
    async def update_traits(
        self,
        flexible_asset_id: Union[str, int],
        traits: Dict[str, Any],
        merge: bool = True
    ) -> FlexibleAsset:
        """
        Update traits for a flexible asset.
        
        Args:
            flexible_asset_id: ID of the flexible asset
            traits: Dictionary of trait values to update
            merge: Whether to merge with existing traits (default) or replace
            
        Returns:
            Updated flexible asset
        """
        if merge:
            # Get current asset to merge traits
            current_asset = await self.get(flexible_asset_id)
            current_traits = current_asset.traits or {}
            updated_traits = {**current_traits, **traits}
        else:
            updated_traits = traits
        
        data = {
            "type": "flexible_assets",
            "attributes": {
                "traits": updated_traits
            }
        }
        
        response = await self.client.patch(
            self._build_url(flexible_asset_id),
            {"data": data}
        )
        return FlexibleAsset.from_api_dict(response["data"])
    
    async def add_tags(
        self,
        flexible_asset_id: Union[str, int],
        tags: List[str]
    ) -> FlexibleAsset:
        """
        Add tags to a flexible asset.
        
        Args:
            flexible_asset_id: ID of the flexible asset
            tags: List of tags to add
            
        Returns:
            Updated flexible asset
        """
        current_asset = await self.get(flexible_asset_id)
        current_tags = current_asset.tag_list or []
        
        # Add new tags, avoiding duplicates
        updated_tags = current_tags.copy()
        for tag in tags:
            if tag not in updated_tags:
                updated_tags.append(tag)
        
        data = {
            "type": "flexible_assets",
            "attributes": {
                "tag_list": updated_tags
            }
        }
        
        response = await self.client.patch(
            self._build_url(flexible_asset_id),
            {"data": data}
        )
        return FlexibleAsset.from_api_dict(response["data"])
    
    async def remove_tags(
        self,
        flexible_asset_id: Union[str, int],
        tags: List[str]
    ) -> FlexibleAsset:
        """
        Remove tags from a flexible asset.
        
        Args:
            flexible_asset_id: ID of the flexible asset
            tags: List of tags to remove
            
        Returns:
            Updated flexible asset
        """
        current_asset = await self.get(flexible_asset_id)
        current_tags = current_asset.tag_list or []
        
        # Remove specified tags
        updated_tags = [tag for tag in current_tags if tag not in tags]
        
        data = {
            "type": "flexible_assets",
            "attributes": {
                "tag_list": updated_tags
            }
        }
        
        response = await self.client.patch(
            self._build_url(flexible_asset_id),
            {"data": data}
        )
        return FlexibleAsset.from_api_dict(response["data"])
    
    async def update_status(
        self,
        flexible_asset_id: Union[str, int],
        status: Union[FlexibleAssetStatus, str]
    ) -> FlexibleAsset:
        """
        Update the status of a flexible asset.
        
        Args:
            flexible_asset_id: ID of the flexible asset
            status: New status
            
        Returns:
            Updated flexible asset
        """
        status_value = status.value if isinstance(status, FlexibleAssetStatus) else status
        
        data = {
            "type": "flexible_assets",
            "attributes": {
                "status": status_value
            }
        }
        
        response = await self.client.patch(
            self._build_url(flexible_asset_id),
            {"data": data}
        )
        return FlexibleAsset.from_api_dict(response["data"])
    
    async def get_asset_statistics(
        self,
        organization_id: Optional[Union[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about flexible assets.
        
        Args:
            organization_id: Optional organization filter
            
        Returns:
            Dictionary containing asset statistics
        """
        params = {}
        if organization_id:
            params["filter[organization_id]"] = str(organization_id)
        
        # Get all assets with status breakdown
        active_assets = await self.list_by_status(
            FlexibleAssetStatus.ACTIVE,
            organization_id=organization_id,
            per_page=1
        )
        
        inactive_assets = await self.list_by_status(
            FlexibleAssetStatus.INACTIVE,
            organization_id=organization_id,
            per_page=1
        )
        
        archived_assets = await self.list_by_status(
            FlexibleAssetStatus.ARCHIVED,
            organization_id=organization_id,
            per_page=1
        )
        
        return {
            "total_count": (
                (active_assets.total_count or 0) +
                (inactive_assets.total_count or 0) +
                (archived_assets.total_count or 0)
            ),
            "active_count": active_assets.total_count or 0,
            "inactive_count": inactive_assets.total_count or 0,
            "archived_count": archived_assets.total_count or 0,
            "organization_id": organization_id
        }


class FlexibleAssetTypesAPI(BaseAPI[FlexibleAssetType]):
    """
    ITGlue Flexible Asset Types API client.
    
    Provides methods for managing flexible asset types, which define
    the structure and fields for flexible assets.
    """
    
    def __init__(self, client):
        super().__init__(client, ResourceType.FLEXIBLE_ASSET_TYPES, FlexibleAssetType, "flexible_asset_types")
    
    async def get_enabled_types(self) -> FlexibleAssetTypeCollection:
        """
        Get all enabled flexible asset types.
        
        Returns:
            Collection of enabled flexible asset types
        """
        params = {"filter[enabled]": "true"}
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetTypeCollection.from_api_dict(response)
    
    async def get_builtin_types(self) -> FlexibleAssetTypeCollection:
        """
        Get all built-in flexible asset types.
        
        Returns:
            Collection of built-in flexible asset types
        """
        params = {"filter[builtin]": "true"}
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetTypeCollection.from_api_dict(response)
    
    async def search_by_name(
        self,
        name: str,
        exact_match: bool = False
    ) -> FlexibleAssetTypeCollection:
        """
        Search flexible asset types by name.
        
        Args:
            name: Name to search for
            exact_match: Whether to perform exact match (default: partial)
            
        Returns:
            Collection of matching flexible asset types
        """
        if exact_match:
            params = {"filter[name]": name}
        else:
            params = {"filter[name]": f"*{name}*"}
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetTypeCollection.from_api_dict(response)
    
    async def get_fields(
        self,
        flexible_asset_type_id: Union[str, int]
    ) -> FlexibleAssetFieldCollection:
        """
        Get fields for a specific flexible asset type.
        
        Args:
            flexible_asset_type_id: ID of the flexible asset type
            
        Returns:
            Collection of fields for the flexible asset type
        """
        url = f"{self._build_url(flexible_asset_type_id)}/relationships/flexible_asset_fields"
        
        response = await self.client.get(url)
        return FlexibleAssetFieldCollection.from_api_dict(response)


class FlexibleAssetFieldsAPI(BaseAPI[FlexibleAssetField]):
    """
    ITGlue Flexible Asset Fields API client.
    
    Provides methods for managing flexible asset fields, which define
    individual fields within flexible asset types.
    """
    
    def __init__(self, client):
        super().__init__(client, ResourceType.FLEXIBLE_ASSET_FIELDS, FlexibleAssetField, "flexible_asset_fields")
    
    async def get_by_type(
        self,
        flexible_asset_type_id: Union[str, int]
    ) -> FlexibleAssetFieldCollection:
        """
        Get fields for a specific flexible asset type.
        
        Args:
            flexible_asset_type_id: ID of the flexible asset type
            
        Returns:
            Collection of fields for the flexible asset type
        """
        params = {"filter[flexible_asset_type_id]": str(flexible_asset_type_id)}
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetFieldCollection.from_api_dict(response)
    
    async def get_required_fields(
        self,
        flexible_asset_type_id: Union[str, int]
    ) -> FlexibleAssetFieldCollection:
        """
        Get required fields for a specific flexible asset type.
        
        Args:
            flexible_asset_type_id: ID of the flexible asset type
            
        Returns:
            Collection of required fields for the flexible asset type
        """
        params = {
            "filter[flexible_asset_type_id]": str(flexible_asset_type_id),
            "filter[required]": "true"
        }
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetFieldCollection.from_api_dict(response)
    
    async def get_by_kind(
        self,
        kind: str,
        flexible_asset_type_id: Optional[Union[str, int]] = None
    ) -> FlexibleAssetFieldCollection:
        """
        Get fields by their kind/type.
        
        Args:
            kind: Field kind (Text, Number, Date, etc.)
            flexible_asset_type_id: Optional flexible asset type filter
            
        Returns:
            Collection of fields of the specified kind
        """
        params = {"filter[kind]": kind}
        
        if flexible_asset_type_id:
            params["filter[flexible_asset_type_id]"] = str(flexible_asset_type_id)
        
        response = await self.client.get(self._build_url(), params=params)
        return FlexibleAssetFieldCollection.from_api_dict(response) 