"""
Organization model for ITGlue API.

Organizations represent companies/clients in ITGlue and are the primary
organizational unit for most other resources.
"""

from enum import Enum
from typing import Optional, List, Any

from pydantic import Field, field_validator

from .base import ITGlueResource, ResourceType, ITGlueResourceCollection
from .common import (
    ITGlueDateTime,
    ITGlueURL,
    required_string,
    optional_string,
    optional_int
)


class OrganizationStatus(str, Enum):
    """Organization status enumeration."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class OrganizationTypeEnum(str, Enum):
    """Organization type enumeration."""
    INTERNAL = "Internal"
    CLIENT = "Client"
    VENDOR = "Vendor"
    PARTNER = "Partner"


class Organization(ITGlueResource):
    """
    ITGlue Organization resource.
    
    Organizations represent companies/clients and serve as the primary
    organizational structure for configurations, passwords, and other resources.
    """
    
    def __init__(self, **data):
        if 'type' not in data:
            data['type'] = ResourceType.ORGANIZATIONS
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
        """Organization name."""
        return self.get_attribute('name')
    
    @name.setter
    def name(self, value: str) -> None:
        self.set_attribute('name', value)
    
    @property
    def description(self) -> Optional[str]:
        """Organization description."""
        return self.get_attribute('description')
    
    @description.setter
    def description(self, value: Optional[str]) -> None:
        self.set_attribute('description', value)
    
    @property
    def organization_type_name(self) -> Optional[str]:
        """Organization type (Internal, Client, Vendor, Partner)."""
        return self.get_attribute('organization-type-name')
    
    @organization_type_name.setter
    def organization_type_name(self, value: Optional[str]) -> None:
        self.set_attribute('organization-type-name', value)
    
    @property
    def organization_status_name(self) -> Optional[str]:
        """Organization status (Active, Inactive)."""
        return self.get_attribute('organization-status-name')
    
    @organization_status_name.setter
    def organization_status_name(self, value: Optional[str]) -> None:
        self.set_attribute('organization-status-name', value)
    
    @property
    def primary_domain(self) -> Optional[str]:
        """Primary domain for the organization."""
        # Try both API field name and direct attribute
        return self.get_attribute('primary-domain') or self.get_attribute('primary_domain')
    
    @primary_domain.setter
    def primary_domain(self, value: Optional[str]) -> None:
        self.set_attribute('primary-domain', value)
    
    @property
    def logo(self) -> Optional[str]:
        """Logo URL."""
        return self.get_attribute('logo')
    
    @logo.setter
    def logo(self, value: Optional[str]) -> None:
        self.set_attribute('logo', value)
    
    @property
    def quick_notes(self) -> Optional[str]:
        """Quick notes about the organization."""
        return self.get_attribute('quick-notes')
    
    @quick_notes.setter
    def quick_notes(self, value: Optional[str]) -> None:
        self.set_attribute('quick-notes', value)
    
    # Timestamps
    @property
    def created_at(self) -> Optional[ITGlueDateTime]:
        """Creation timestamp."""
        value = self.get_attribute('created-at')
        return ITGlueDateTime.validate(value) if value else None
    
    @property
    def updated_at(self) -> Optional[ITGlueDateTime]:
        """Last update timestamp."""
        value = self.get_attribute('updated-at')
        return ITGlueDateTime.validate(value) if value else None
    
    # Relationship helpers
    @property
    def organization_type_id(self) -> Optional[str]:
        """ID of the organization type."""
        return self.get_related_id('organization-type')
    
    @property
    def organization_status_id(self) -> Optional[str]:
        """ID of the organization status."""
        return self.get_related_id('organization-status')
    
    @property
    def group_id(self) -> Optional[str]:
        """ID of the parent group."""
        return self.get_related_id('group')
    
    # Convenience methods
    def is_active(self) -> bool:
        """Check if organization is active."""
        return self.organization_status_name == OrganizationStatus.ACTIVE.value
    
    def is_client(self) -> bool:
        """Check if organization is a client."""
        return self.organization_type_name == OrganizationTypeEnum.CLIENT.value
    
    def is_internal(self) -> bool:
        """Check if organization is internal."""
        return self.organization_type_name == OrganizationTypeEnum.INTERNAL.value
    
    def __str__(self) -> str:
        """String representation."""
        return f"Organization(id={self.id}, name='{self.name}')"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Organization(id={self.id}, name='{self.name}', "
            f"type={self.organization_type_name}, status={self.organization_status_name})"
        )


class OrganizationCollection(ITGlueResourceCollection[Organization]):
    """Collection of Organization resources."""
    
    @classmethod
    def from_api_dict(cls, data: dict) -> 'OrganizationCollection':
        """Create collection from API response."""
        return super().from_api_dict(data, Organization)
    
    def get_by_name(self, name: str) -> Optional[Organization]:
        """Find organization by name."""
        for org in self.data:
            if org.name and org.name.lower() == name.lower():
                return org
        return None
    
    def get_active_organizations(self) -> List[Organization]:
        """Get all active organizations."""
        return [org for org in self.data if org.is_active()]
    
    def get_clients(self) -> List[Organization]:
        """Get all client organizations."""
        return [org for org in self.data if org.is_client()]
    
    def get_internal_organizations(self) -> List[Organization]:
        """Get all internal organizations.""" 
        return [org for org in self.data if org.is_internal()] 