"""
Flexible Asset model for ITGlue API.

Flexible Assets represent custom data structures that can be defined
by users to document any type of information not covered by standard resources.
"""

from enum import Enum
from typing import Optional, List, Any, Dict, Union, Type
from datetime import datetime

from pydantic import Field, field_validator

from .base import ITGlueResource, ResourceType, ITGlueResourceCollection
from .common import (
    ITGlueDateTime,
    ITGlueURL,
    required_string,
    optional_string,
    optional_int,
)


class FlexibleAssetStatus(str, Enum):
    """Flexible Asset status enumeration."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"
    ARCHIVED = "Archived"


class FlexibleAsset(ITGlueResource):
    """
    ITGlue Flexible Asset resource.

    Flexible Assets are custom data structures that allow organizations
    to document any type of information using user-defined fields and types.
    """

    def __init__(self, **data):
        if "type" not in data:
            data["type"] = ResourceType.FLEXIBLE_ASSETS

        # Convert snake_case attribute names to hyphen-case for API compatibility
        attribute_mappings = {
            "flexible_asset_type_name": "flexible-asset-type-name",
            "tag_list": "tag-list",
            "organization_id": "organization-id",
            "created_at": "created-at",
            "updated_at": "updated-at",
        }

        for snake_case, hyphen_case in attribute_mappings.items():
            if snake_case in data:
                data[hyphen_case] = data.pop(snake_case)

        super().__init__(**data)

    def __setattr__(self, name: str, value: Any) -> None:
        """Override to ensure property setters are called."""
        # Check if this is a property with a setter
        prop = getattr(type(self), name, None)
        if isinstance(prop, property) and prop.fset is not None:
            prop.fset(self, value)
        else:
            super().__setattr__(name, value)

    # Core attributes with validation
    @property
    def name(self) -> Optional[str]:
        """Flexible asset name."""
        return self.get_attribute("name")

    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute("name", value)

    @property
    def description(self) -> Optional[str]:
        """Flexible asset description."""
        return self.get_attribute("description")

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self.set_attribute("description", value)

    @property
    def flexible_asset_type_name(self) -> Optional[str]:
        """Name of the flexible asset type."""
        return self.get_attribute("flexible-asset-type-name")

    @flexible_asset_type_name.setter
    def flexible_asset_type_name(self, value: Optional[str]) -> None:
        self.set_attribute("flexible-asset-type-name", value)

    @property
    def status(self) -> Optional[str]:
        """Flexible asset status."""
        return self.get_attribute("status")

    @status.setter
    def status(self, value: Optional[str]) -> None:
        self.set_attribute("status", value)

    @property
    def traits(self) -> Optional[Dict[str, Any]]:
        """Dynamic traits/fields defined by the flexible asset type."""
        return self.get_attribute("traits")

    @traits.setter
    def traits(self, value: Optional[Dict[str, Any]]) -> None:
        self.set_attribute("traits", value)

    @property
    def tag_list(self) -> Optional[List[str]]:
        """List of tags associated with this flexible asset."""
        return self.get_attribute("tag-list")

    @tag_list.setter
    def tag_list(self, value: Optional[List[str]]) -> None:
        self.set_attribute("tag-list", value)

    # Timestamps
    @property
    def created_at(self) -> Optional[datetime]:
        """Get created timestamp."""
        return self._parse_datetime(self.get_attribute("created-at"))

    @property
    def updated_at(self) -> Optional[datetime]:
        """Get updated timestamp."""
        return self._parse_datetime(self.get_attribute("updated-at"))

    # Relationship helpers
    @property
    def organization_id(self) -> Optional[str]:
        """ID of the organization this flexible asset belongs to."""
        # Check relationship first, then attribute (for creation scenarios)
        relationship_id = self.get_related_id("organization")
        if relationship_id:
            return relationship_id
        return self.get_attribute("organization-id")

    @property
    def flexible_asset_type_id(self) -> Optional[str]:
        """ID of the flexible asset type."""
        return self.get_related_id("flexible-asset-type")

    @property
    def attachments_ids(self) -> List[str]:
        """IDs of associated attachments."""
        return self.get_related_ids("attachments")

    # Convenience methods for traits
    def get_trait(self, trait_name: str, default: Any = None) -> Any:
        """Get a specific trait value."""
        if self.traits:
            return self.traits.get(trait_name, default)
        return default

    def set_trait(self, trait_name: str, value: Any) -> None:
        """Set a specific trait value."""
        if self.traits is None:
            self.traits = {}
        self.traits[trait_name] = value

    def has_trait(self, trait_name: str) -> bool:
        """Check if a trait exists."""
        return self.traits is not None and trait_name in self.traits

    def list_trait_names(self) -> List[str]:
        """Get list of all trait names."""
        return list(self.traits.keys()) if self.traits else []

    # Convenience methods
    def is_active(self) -> bool:
        """Check if flexible asset is active."""
        return self.status == FlexibleAssetStatus.ACTIVE.value

    def is_archived(self) -> bool:
        """Check if flexible asset is archived."""
        return self.status == FlexibleAssetStatus.ARCHIVED.value

    def add_tag(self, tag: str) -> None:
        """Add a tag to the flexible asset."""
        if self.tag_list is None:
            self.tag_list = []
        if tag not in self.tag_list:
            self.tag_list.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the flexible asset."""
        if self.tag_list and tag in self.tag_list:
            self.tag_list.remove(tag)

    def has_tag(self, tag: str) -> bool:
        """Check if flexible asset has a specific tag."""
        return self.tag_list is not None and tag in self.tag_list

    def __str__(self) -> str:
        """String representation."""
        return f"FlexibleAsset(id={self.id}, name='{self.name}', type='{self.flexible_asset_type_name}')"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"FlexibleAsset(id={self.id}, name='{self.name}', "
            f"type='{self.flexible_asset_type_name}', status={self.status})"
        )


class FlexibleAssetType(ITGlueResource):
    """
    ITGlue Flexible Asset Type resource.

    Defines the structure and fields for flexible assets.
    """

    def __init__(self, **data):
        if "type" not in data:
            data["type"] = ResourceType.FLEXIBLE_ASSET_TYPES
        super().__init__(**data)

    @property
    def name(self) -> Optional[str]:
        """Flexible asset type name."""
        return self.get_attribute("name")

    @property
    def description(self) -> Optional[str]:
        """Flexible asset type description."""
        return self.get_attribute("description")

    @property
    def icon(self) -> Optional[str]:
        """Icon for the flexible asset type."""
        return self.get_attribute("icon")

    @property
    def enabled(self) -> Optional[bool]:
        """Whether this flexible asset type is enabled."""
        return self.get_attribute("enabled")

    @property
    def builtin(self) -> Optional[bool]:
        """Whether this is a built-in flexible asset type."""
        return self.get_attribute("builtin")

    def __str__(self) -> str:
        """String representation."""
        return f"FlexibleAssetType(id={self.id}, name='{self.name}')"


class FlexibleAssetField(ITGlueResource):
    """
    ITGlue Flexible Asset Field resource.

    Defines individual fields within a flexible asset type.
    """

    def __init__(self, **data):
        if "type" not in data:
            data["type"] = ResourceType.FLEXIBLE_ASSET_FIELDS

        # Convert snake_case attribute names to hyphen-case for API compatibility
        attribute_mappings = {
            "tag_type": "tag-type",
            "show_in_list": "show-in-list",
            "sort_order": "sort-order",
            "created_at": "created-at",
            "updated_at": "updated-at",
        }

        for snake_case, hyphen_case in attribute_mappings.items():
            if snake_case in data:
                data[hyphen_case] = data.pop(snake_case)

        super().__init__(**data)

    @property
    def name(self) -> Optional[str]:
        """Field name."""
        return self.get_attribute("name")

    @property
    def kind(self) -> Optional[str]:
        """Field type (Text, Number, Date, etc.)."""
        return self.get_attribute("kind")

    @property
    def hint(self) -> Optional[str]:
        """Field hint/description."""
        return self.get_attribute("hint")

    @property
    def tag_type(self) -> Optional[str]:
        """Tag type for the field."""
        return self.get_attribute("tag-type")

    @property
    def required(self) -> Optional[bool]:
        """Whether this field is required."""
        return self.get_attribute("required")

    @property
    def show_in_list(self) -> Optional[bool]:
        """Whether to show this field in list views."""
        return self.get_attribute("show-in-list")

    @property
    def sort_order(self) -> Optional[int]:
        """Sort order for displaying this field."""
        return self.get_attribute("sort-order")

    def __str__(self) -> str:
        """String representation."""
        return (
            f"FlexibleAssetField(id={self.id}, name='{self.name}', kind='{self.kind}')"
        )


class FlexibleAssetCollection(ITGlueResourceCollection[FlexibleAsset]):
    """Collection of Flexible Asset resources."""

    @classmethod
    def from_api_dict(
        cls, data: Dict[str, Any], resource_class: Optional[Type[FlexibleAsset]] = None
    ) -> "FlexibleAssetCollection":
        """Create FlexibleAssetCollection from API response."""
        if resource_class is None:
            resource_class = FlexibleAsset
        
        base_collection = super().from_api_dict(data, resource_class)
        return cls(
            data=base_collection.data,
            meta=base_collection.meta,
            links=base_collection.links,
            included=base_collection.included,
        )

    def get_by_name(self, name: str) -> Optional[FlexibleAsset]:
        """Find flexible asset by name."""
        for asset in self.data:
            if asset.name and asset.name.lower() == name.lower():
                return asset
        return None

    def get_by_type(self, type_name: str) -> List[FlexibleAsset]:
        """Get all flexible assets of a specific type."""
        return [
            asset
            for asset in self.data
            if asset.flexible_asset_type_name
            and asset.flexible_asset_type_name.lower() == type_name.lower()
        ]

    def get_active_assets(self) -> List[FlexibleAsset]:
        """Get all active flexible assets."""
        return [asset for asset in self.data if asset.is_active()]

    def get_by_tag(self, tag: str) -> List[FlexibleAsset]:
        """Get all flexible assets with a specific tag."""
        return [asset for asset in self.data if asset.has_tag(tag)]

    def get_by_trait(
        self, trait_name: str, trait_value: Any = None
    ) -> List[FlexibleAsset]:
        """Get all flexible assets with a specific trait (optionally matching a value)."""
        if trait_value is None:
            return [asset for asset in self.data if asset.has_trait(trait_name)]
        else:
            return [
                asset
                for asset in self.data
                if asset.get_trait(trait_name) == trait_value
            ]


class FlexibleAssetTypeCollection(ITGlueResourceCollection[FlexibleAssetType]):
    """Collection of Flexible Asset Type resources."""

    @classmethod
    def from_api_dict(
        cls, data: Dict[str, Any], resource_class: Optional[Type[FlexibleAssetType]] = None
    ) -> "FlexibleAssetTypeCollection":
        """Create FlexibleAssetTypeCollection from API response."""
        if resource_class is None:
            resource_class = FlexibleAssetType
        
        base_collection = super().from_api_dict(data, resource_class)
        return cls(
            data=base_collection.data,
            meta=base_collection.meta,
            links=base_collection.links,
            included=base_collection.included,
        )

    def get_by_name(self, name: str) -> Optional[FlexibleAssetType]:
        """Find flexible asset type by name."""
        for asset_type in self.data:
            if asset_type.name and asset_type.name.lower() == name.lower():
                return asset_type
        return None

    def get_enabled_types(self) -> List[FlexibleAssetType]:
        """Get all enabled flexible asset types."""
        return [asset_type for asset_type in self.data if asset_type.enabled]


class FlexibleAssetFieldCollection(ITGlueResourceCollection[FlexibleAssetField]):
    """Collection of Flexible Asset Field resources."""

    @classmethod
    def from_api_dict(
        cls, data: Dict[str, Any], resource_class: Optional[Type[FlexibleAssetField]] = None
    ) -> "FlexibleAssetFieldCollection":
        """Create FlexibleAssetFieldCollection from API response."""
        if resource_class is None:
            resource_class = FlexibleAssetField
        
        base_collection = super().from_api_dict(data, resource_class)
        return cls(
            data=base_collection.data,
            meta=base_collection.meta,
            links=base_collection.links,
            included=base_collection.included,
        )

    def get_by_name(self, name: str) -> Optional[FlexibleAssetField]:
        """Find field by name."""
        for field in self.data:
            if field.name and field.name.lower() == name.lower():
                return field
        return None

    def get_required_fields(self) -> List[FlexibleAssetField]:
        """Get all required fields."""
        return [field for field in self.data if field.required]

    def get_by_kind(self, kind: str) -> List[FlexibleAssetField]:
        """Get all fields of a specific kind."""
        return [
            field
            for field in self.data
            if field.kind and field.kind.lower() == kind.lower()
        ]
