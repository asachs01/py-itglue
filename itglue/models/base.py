"""
Base models for ITGlue API resources.

Provides base classes that implement JSON API specification compliance,
including resource structure, relationships, links, and meta information.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union, Type, TypeVar, Generic
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator

from .common import ITGlueDateTime, itglue_id_field, optional_itglue_id_field


class ResourceType(str, Enum):
    """
    Enumeration of ITGlue resource types.
    
    These correspond to the 'type' field in JSON API resources.
    """
    # Core resources
    ORGANIZATIONS = "organizations"
    CONFIGURATIONS = "configurations"
    PASSWORDS = "passwords"
    CONTACTS = "contacts"
    LOCATIONS = "locations"
    
    # Asset types
    FLEXIBLE_ASSETS = "flexible_assets"
    FLEXIBLE_ASSET_TYPES = "flexible_asset_types" 
    FLEXIBLE_ASSET_FIELDS = "flexible_asset_fields"
    
    # Documentation
    ARTICLES = "articles"
    CHECKLISTS = "checklists"
    CHECKLIST_TEMPLATES = "checklist_templates"
    
    # Ticketing
    TICKETS = "tickets"
    TICKET_STATUSES = "ticket_statuses"
    
    # Inventory
    ASSETS = "assets"
    ASSET_TYPES = "asset_types"
    MANUFACTURERS = "manufacturers"
    MODELS = "models"
    
    # Network
    DOMAINS = "domains"
    SSL_CERTIFICATES = "ssl_certificates"
    
    # Users and security
    USERS = "users"
    USER_METRICS = "user_metrics"
    GROUPS = "groups"
    
    # System
    ACTIVITY_LOGS = "activity_logs"
    WEBHOOKS = "webhooks"
    
    # Resource types (type references)
    ORGANIZATION_TYPES = "organization-types"
    ORGANIZATION_STATUSES = "organization-statuses"
    CONFIGURATION_TYPES = "configuration-types" 
    CONFIGURATION_STATUSES = "configuration-statuses"


class ITGlueLinks(BaseModel):
    """
    JSON API links object.
    
    Contains URLs for related resources and navigation.
    """
    model_config = ConfigDict(extra="allow")
    
    self: Optional[str] = Field(None, description="Link to this resource")
    related: Optional[str] = Field(None, description="Link to related resource")
    first: Optional[str] = Field(None, description="First page link")
    last: Optional[str] = Field(None, description="Last page link") 
    prev: Optional[str] = Field(None, description="Previous page link")
    next: Optional[str] = Field(None, description="Next page link")


class ITGlueMeta(BaseModel):
    """
    JSON API meta object.
    
    Contains metadata about the resource or collection.
    """
    model_config = ConfigDict(extra="allow")
    
    # Pagination metadata
    current_page: Optional[int] = Field(None, alias="current-page")
    next_page: Optional[int] = Field(None, alias="next-page")
    prev_page: Optional[int] = Field(None, alias="prev-page")
    total_pages: Optional[int] = Field(None, alias="total-pages")
    total_count: Optional[int] = Field(None, alias="total-count")
    
    # Other common metadata
    created_at: Optional[ITGlueDateTime] = Field(None, alias="created-at")
    updated_at: Optional[ITGlueDateTime] = Field(None, alias="updated-at")


class ITGlueRelationshipData(BaseModel):
    """
    JSON API relationship data object.
    
    References another resource by type and id.
    """
    type: ResourceType = Field(..., description="Resource type")
    id: str = itglue_id_field()


class ITGlueRelationship(BaseModel):
    """
    JSON API relationship object.
    
    Contains data and links for related resources.
    """
    data: Optional[Union[ITGlueRelationshipData, List[ITGlueRelationshipData]]] = Field(
        None, 
        description="Related resource(s) reference"
    )
    links: Optional[ITGlueLinks] = Field(None, description="Relationship links")
    meta: Optional[ITGlueMeta] = Field(None, description="Relationship metadata")


T = TypeVar('T', bound='ITGlueResource')


class ITGlueResource(BaseModel, Generic[T]):
    """
    Base class for all ITGlue resources.
    
    Implements JSON API resource structure with id, type, attributes,
    relationships, links, and meta fields.
    """
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        ser_by_alias=True
    )
    
    # JSON API structure
    id: Optional[str] = optional_itglue_id_field()
    type: ResourceType = Field(..., description="Resource type")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Resource attributes")
    relationships: Optional[Dict[str, ITGlueRelationship]] = Field(
        None, 
        description="Resource relationships"
    )
    links: Optional[ITGlueLinks] = Field(None, description="Resource links")
    meta: Optional[ITGlueMeta] = Field(None, description="Resource metadata")
    
    def __init__(self, **data):
        """Initialize resource with attribute flattening."""
        # If attributes are provided at top level, move them to attributes dict
        if 'attributes' not in data:
            data['attributes'] = {}
        
        # Move top-level fields to attributes if they don't belong to JSON API structure
        json_api_fields = {'id', 'type', 'attributes', 'relationships', 'links', 'meta'}
        for key, value in list(data.items()):
            if key not in json_api_fields and not key.startswith('_'):
                data['attributes'][key] = value
                del data[key]
        
        super().__init__(**data)
    
    def __getattr__(self, name: str) -> Any:
        """Allow access to attributes as direct properties."""
        if name in self.attributes:
            return self.attributes[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Allow setting attributes as direct properties."""
        if name in {'id', 'type', 'attributes', 'relationships', 'links', 'meta', 'model_config'}:
            super().__setattr__(name, value)
        else:
            if not hasattr(self, 'attributes'):
                super().__setattr__('attributes', {})
            self.attributes[name] = value
    
    @property
    def resource_id(self) -> Optional[str]:
        """Get the resource ID."""
        return self.id
    
    @property
    def resource_type(self) -> ResourceType:
        """Get the resource type."""
        return self.type
    
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """Get an attribute value with optional default."""
        return self.attributes.get(name, default)
    
    def set_attribute(self, name: str, value: Any) -> None:
        """Set an attribute value."""
        self.attributes[name] = value
    
    def get_relationship(self, name: str) -> Optional[ITGlueRelationship]:
        """Get a relationship by name."""
        if not self.relationships:
            return None
        return self.relationships.get(name)
    
    def set_relationship(self, name: str, relationship: ITGlueRelationship) -> None:
        """Set a relationship."""
        if not self.relationships:
            self.relationships = {}
        self.relationships[name] = relationship
    
    def get_related_id(self, relationship_name: str) -> Optional[str]:
        """Get the ID of a related resource."""
        relationship = self.get_relationship(relationship_name)
        if not relationship or not relationship.data:
            return None
        
        if isinstance(relationship.data, list):
            return relationship.data[0].id if relationship.data else None
        return relationship.data.id
    
    def get_related_ids(self, relationship_name: str) -> List[str]:
        """Get the IDs of related resources (for to-many relationships)."""
        relationship = self.get_relationship(relationship_name)
        if not relationship or not relationship.data:
            return []
        
        if isinstance(relationship.data, list):
            return [item.id for item in relationship.data]
        return [relationship.data.id]
    
    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for API requests."""
        # Handle both string and enum types
        type_value = self.type.value if hasattr(self.type, 'value') else str(self.type)
        
        result = {
            "type": type_value,
            "attributes": self.attributes.copy()
        }
        
        if self.id:
            result["id"] = self.id
        
        if self.relationships:
            result["relationships"] = {}
            for name, rel in self.relationships.items():
                result["relationships"][name] = rel.model_dump(by_alias=True, exclude_none=True)
        
        return result
    
    @classmethod
    def from_api_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create instance from API response dictionary."""
        return cls.model_validate(data)
    
    def model_dump_api(self) -> Dict[str, Any]:
        """Dump model in API format (alias for to_api_dict)."""
        return self.to_api_dict()


class ITGlueResourceCollection(BaseModel, Generic[T]):
    """
    Collection of ITGlue resources with pagination and metadata.
    
    Represents a JSON API response containing multiple resources.
    """
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True
    )
    
    data: List[T] = Field(default_factory=list, description="Collection of resources")
    links: Optional[ITGlueLinks] = Field(None, description="Collection links")
    meta: Optional[ITGlueMeta] = Field(None, description="Collection metadata")
    included: Optional[List[ITGlueResource]] = Field(
        None, 
        description="Included related resources"
    )
    
    def __len__(self) -> int:
        """Get the number of resources in the collection."""
        return len(self.data)
    
    def __iter__(self):
        """Iterate over resources in the collection."""
        return iter(self.data)
    
    def __getitem__(self, index: int) -> T:
        """Get resource by index."""
        return self.data[index]
    
    @property
    def count(self) -> int:
        """Get the number of resources in this page."""
        return len(self.data)
    
    @property
    def total_count(self) -> Optional[int]:
        """Get the total number of resources across all pages."""
        if self.meta:
            return getattr(self.meta, 'total_count', None) or getattr(self.meta, 'total-count', None)
        return None
    
    @property
    def current_page(self) -> Optional[int]:
        """Get the current page number."""
        if self.meta:
            # Check both direct attribute and aliased field
            return getattr(self.meta, 'current_page', None) or getattr(self.meta, 'current-page', None)
        return None
    
    @property
    def total_pages(self) -> Optional[int]:
        """Get the total number of pages."""
        if self.meta:
            return getattr(self.meta, 'total_pages', None) or getattr(self.meta, 'total-pages', None)
        return None
    
    @property
    def has_next_page(self) -> bool:
        """Check if there is a next page."""
        if self.meta:
            next_page = getattr(self.meta, 'next_page', None) or getattr(self.meta, 'next-page', None)
            if next_page:
                return True
        if self.links and self.links.next:
            return True
        return False
    
    @property
    def has_prev_page(self) -> bool:
        """Check if there is a previous page."""
        if self.meta:
            prev_page = getattr(self.meta, 'prev_page', None) or getattr(self.meta, 'prev-page', None)
            if prev_page:
                return True
        if self.links and self.links.prev:
            return True
        return False
    
    def get_included(self, resource_type: ResourceType, resource_id: str) -> Optional[ITGlueResource]:
        """Get an included resource by type and ID."""
        if not self.included:
            return None
        
        for resource in self.included:
            if resource.type == resource_type and resource.id == resource_id:
                return resource
        
        return None
    
    @classmethod
    def from_api_dict(cls, data: Dict[str, Any], resource_class: Type[T]) -> 'ITGlueResourceCollection[T]':
        """Create collection from API response dictionary."""
        # Parse the resources
        resources = []
        if 'data' in data:
            for item in data['data']:
                resources.append(resource_class.from_api_dict(item))
        
        # Parse included resources
        included = []
        if 'included' in data:
            for item in data['included']:
                included.append(ITGlueResource.from_api_dict(item))
        
        return cls(
            data=resources,
            links=ITGlueLinks.model_validate(data.get('links', {})) if 'links' in data else None,
            meta=ITGlueMeta.model_validate(data.get('meta', {})) if 'meta' in data else None,
            included=included if included else None
        ) 