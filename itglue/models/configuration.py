"""
Configuration model for ITGlue API.

Configurations represent IT assets/devices within organizations, such as
servers, workstations, network devices, and other infrastructure components.
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


class ConfigurationStatus(str, Enum):
    """Configuration status enumeration."""

    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PLANNED = "Planned"
    RETIRED = "Retired"


class Configuration(ITGlueResource):
    """
    ITGlue Configuration resource.

    Configurations represent IT assets and devices within organizations,
    including servers, workstations, network equipment, and other infrastructure.
    """

    def __init__(self, **data):
        if "type" not in data:
            data["type"] = ResourceType.CONFIGURATIONS
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
        """Configuration name."""
        return self.get_attribute("name")

    @name.setter
    def name(self, value: str) -> None:
        if not value or len(value.strip()) < 1:
            raise ValueError("Configuration name cannot be empty")
        self.set_attribute("name", value.strip())

    @property
    def description(self) -> Optional[str]:
        """Configuration description."""
        return self.get_attribute("description")

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self.set_attribute("description", value)

    @property
    def hostname(self) -> Optional[str]:
        """Configuration hostname."""
        return self.get_attribute("hostname")

    @hostname.setter
    def hostname(self, value: Optional[str]) -> None:
        self.set_attribute("hostname", value)

    @property
    def primary_ip(self) -> Optional[str]:
        """Primary IP address."""
        return self.get_attribute("primary-ip")

    @primary_ip.setter
    def primary_ip(self, value: Optional[str]) -> None:
        if value:
            # Basic IP validation (could be IPv4 or IPv6)
            import ipaddress

            try:
                ipaddress.ip_address(value)
            except ValueError:
                raise ValueError(f"Invalid IP address: {value}")
        self.set_attribute("primary-ip", value)

    @property
    def mac_address(self) -> Optional[str]:
        """MAC address."""
        return self.get_attribute("mac-address")

    @mac_address.setter
    def mac_address(self, value: Optional[str]) -> None:
        if value:
            # Basic MAC address validation
            import re

            mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
            if not mac_pattern.match(value):
                raise ValueError(f"Invalid MAC address format: {value}")
        self.set_attribute("mac-address", value)

    @property
    def serial_number(self) -> Optional[str]:
        """Serial number."""
        return self.get_attribute("serial-number")

    @serial_number.setter
    def serial_number(self, value: Optional[str]) -> None:
        self.set_attribute("serial-number", value)

    @property
    def asset_tag(self) -> Optional[str]:
        """Asset tag."""
        return self.get_attribute("asset-tag")

    @asset_tag.setter
    def asset_tag(self, value: Optional[str]) -> None:
        self.set_attribute("asset-tag", value)

    @property
    def position(self) -> Optional[int]:
        """Position in rack or sorting order."""
        return self.get_attribute("position")

    @position.setter
    def position(self, value: Optional[int]) -> None:
        self.set_attribute("position", value)

    @property
    def notes(self) -> Optional[str]:
        """Notes about the configuration."""
        return self.get_attribute("notes")

    @notes.setter
    def notes(self, value: Optional[str]) -> None:
        self.set_attribute("notes", value)

    @property
    def installed_by(self) -> Optional[str]:
        """Who installed this configuration."""
        return self.get_attribute("installed-by")

    @installed_by.setter
    def installed_by(self, value: Optional[str]) -> None:
        self.set_attribute("installed-by", value)

    @property
    def created_at(self) -> Optional[datetime]:
        """Get created timestamp."""
        return self._parse_datetime(self.get_attribute("created-at"))

    @property
    def updated_at(self) -> Optional[datetime]:
        """Get updated timestamp."""
        return self._parse_datetime(self.get_attribute("updated-at"))

    @property
    def warranty_expires_at(self) -> Optional[datetime]:
        """Get warranty expiration timestamp."""
        return self._parse_datetime(self.get_attribute("warranty-expires-at"))

    @property
    def installed_at(self) -> Optional[datetime]:
        """Get installation timestamp."""
        return self._parse_datetime(self.get_attribute("installed-at"))

    @property
    def purchased_at(self) -> Optional[datetime]:
        """Get purchase timestamp."""
        return self._parse_datetime(self.get_attribute("purchased-at"))

    # Status and type information
    @property
    def configuration_status_name(self) -> Optional[str]:
        """Configuration status name."""
        return self.get_attribute("configuration-status-name")

    @configuration_status_name.setter
    def configuration_status_name(self, value: Optional[str]) -> None:
        self.set_attribute("configuration-status-name", value)

    @property
    def configuration_type_name(self) -> Optional[str]:
        """Configuration type name."""
        return self.get_attribute("configuration-type-name")

    @configuration_type_name.setter
    def configuration_type_name(self, value: Optional[str]) -> None:
        self.set_attribute("configuration-type-name", value)

    @property
    def operating_system_name(self) -> Optional[str]:
        """Operating system name."""
        return self.get_attribute("operating-system-name")

    @operating_system_name.setter
    def operating_system_name(self, value: Optional[str]) -> None:
        self.set_attribute("operating-system-name", value)

    # Relationship helpers
    @property
    def organization_id(self) -> Optional[str]:
        """ID of the organization this configuration belongs to."""
        return self.get_related_id("organization")

    @property
    def configuration_type_id(self) -> Optional[str]:
        """ID of the configuration type."""
        return self.get_related_id("configuration-type")

    @property
    def configuration_status_id(self) -> Optional[str]:
        """ID of the configuration status."""
        return self.get_related_id("configuration-status")

    @property
    def contact_id(self) -> Optional[str]:
        """ID of the primary contact."""
        return self.get_related_id("contact")

    @property
    def location_id(self) -> Optional[str]:
        """ID of the location."""
        return self.get_related_id("location")

    @property
    def manufacturer_id(self) -> Optional[str]:
        """ID of the manufacturer."""
        return self.get_related_id("manufacturer")

    @property
    def model_id(self) -> Optional[str]:
        """ID of the model."""
        return self.get_related_id("model")

    @property
    def operating_system_id(self) -> Optional[str]:
        """ID of the operating system."""
        return self.get_related_id("operating-system")

    # Convenience methods
    def is_active(self) -> bool:
        """Check if configuration is active."""
        return self.configuration_status_name == ConfigurationStatus.ACTIVE.value

    def is_retired(self) -> bool:
        """Check if configuration is retired."""
        return self.configuration_status_name == ConfigurationStatus.RETIRED.value

    def is_warranty_expired(self) -> bool:
        """Check if warranty has expired."""
        if not self.warranty_expires_at:
            return False
        from datetime import datetime, timezone

        return self.warranty_expires_at < datetime.now(timezone.utc)

    def __str__(self) -> str:
        """String representation."""
        return f"Configuration(id={self.id}, name='{self.name}')"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Configuration(id={self.id}, name='{self.name}', "
            f"hostname='{self.hostname}', ip='{self.primary_ip}', "
            f"status={self.configuration_status_name})"
        )


class ConfigurationCollection(ITGlueResourceCollection[Configuration]):
    """Collection of Configuration resources."""

    @classmethod
    def from_api_dict(
        cls, data: Dict[str, Any], resource_class: Optional[Type[Configuration]] = None
    ) -> "ConfigurationCollection":
        """Create ConfigurationCollection from API response."""
        if resource_class is None:
            resource_class = Configuration
        
        base_collection = super().from_api_dict(data, resource_class)
        return cls(
            data=base_collection.data,
            meta=base_collection.meta,
            links=base_collection.links,
            included=base_collection.included,
        )

    def get_by_name(self, name: str) -> Optional[Configuration]:
        """Find configuration by name."""
        for config in self.data:
            if config.name and config.name.lower() == name.lower():
                return config
        return None

    def get_by_hostname(self, hostname: str) -> Optional[Configuration]:
        """Find configuration by hostname."""
        for config in self.data:
            if config.hostname and config.hostname.lower() == hostname.lower():
                return config
        return None

    def get_by_ip(self, ip_address: str) -> Optional[Configuration]:
        """Find configuration by IP address."""
        for config in self.data:
            if config.primary_ip == ip_address:
                return config
        return None

    def get_active_configurations(self) -> List[Configuration]:
        """Get all active configurations."""
        return [config for config in self.data if config.is_active()]

    def get_retired_configurations(self) -> List[Configuration]:
        """Get all retired configurations."""
        return [config for config in self.data if config.is_retired()]

    def get_by_organization(self, organization_id: str) -> List[Configuration]:
        """Get all configurations for a specific organization."""
        return [
            config for config in self.data if config.organization_id == organization_id
        ]

    def get_warranty_expiring_soon(self, days: int = 30) -> List[Configuration]:
        """Get configurations with warranty expiring within specified days."""
        from datetime import datetime, timezone, timedelta

        cutoff_date = datetime.now(timezone.utc) + timedelta(days=days)

        return [
            config
            for config in self.data
            if config.warranty_expires_at and config.warranty_expires_at <= cutoff_date
        ]
