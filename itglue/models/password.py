"""
Password model for ITGlue API.

This module defines the Password resource model with support for secure password storage,
organization relationships, sharing controls, and comprehensive password management features.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .base import ITGlueResource, ITGlueResourceCollection, ResourceType
from .common import ITGlueDateTime


class PasswordType(str, Enum):
    """Enumeration of password types in ITGlue."""

    EMBEDDED = "embedded"
    LINKED = "linked"


class PasswordCategory(str, Enum):
    """Enumeration of password security categories."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PasswordVisibility(str, Enum):
    """Enumeration of password visibility levels."""

    PRIVATE = "private"
    SHARED = "shared"
    ORGANIZATION = "organization"
    EVERYONE = "everyone"


class Password(ITGlueResource):
    """
    Represents a Password in ITGlue.

    Passwords are secure credential storage objects that can be linked to
    organizations, configurations, and other resources. They support various
    security levels, sharing controls, and audit capabilities.
    """

    def __init__(self, **data):
        """Initialize a Password instance."""
        if "type" not in data:
            data["type"] = ResourceType.PASSWORDS
        super().__init__(**data)

    def __setattr__(self, name: str, value: Any) -> None:
        """Override setattr to handle property setters for hyphenated attributes."""
        # Define mapping of Python property names to API attribute names
        property_mappings = {
            "name": "name",
            "username": "username",
            "password": "password",
            "url": "url",
            "notes": "notes",
            "password_type": "password-type",
            "password_category": "password-category-name",
            "visibility": "visibility",
            "auto_fill_selectors": "autofill-selectors",
            "favorite": "favorite",
            "archived": "archived",
        }

        # If setting a property that maps to a hyphenated attribute, use set_attribute
        if name in property_mappings:
            if hasattr(self, "attributes"):
                self.set_attribute(property_mappings[name], value)
            else:
                # During initialization, call parent setattr
                super().__setattr__(name, value)
        else:
            # For all other attributes, use parent behavior
            super().__setattr__(name, value)

    # Core password properties
    @property
    def name(self) -> Optional[str]:
        """Get the password name/title."""
        return self.get_attribute("name")

    @name.setter
    def name(self, value: str) -> None:
        """Set the password name/title."""
        self.set_attribute("name", value)

    @property
    def username(self) -> Optional[str]:
        """Get the username."""
        return self.get_attribute("username")

    @username.setter
    def username(self, value: str) -> None:
        """Set the username."""
        self.set_attribute("username", value)

    @property
    def password(self) -> Optional[str]:
        """Get the password value."""
        return self.get_attribute("password")

    @password.setter
    def password(self, value: str) -> None:
        """Set the password value."""
        self.set_attribute("password", value)

    @property
    def url(self) -> Optional[str]:
        """Get the associated URL."""
        return self.get_attribute("url")

    @url.setter
    def url(self, value: str) -> None:
        """Set the associated URL."""
        self.set_attribute("url", value)

    @property
    def notes(self) -> Optional[str]:
        """Get the password notes."""
        return self.get_attribute("notes")

    @notes.setter
    def notes(self, value: str) -> None:
        """Set the password notes."""
        self.set_attribute("notes", value)

    # Type and categorization properties
    @property
    def password_type(self) -> Optional[PasswordType]:
        """Get the password type."""
        type_str = self.get_attribute("password-type")
        return PasswordType(type_str) if type_str else None

    @password_type.setter
    def password_type(self, value: Union[PasswordType, str]) -> None:
        """Set the password type."""
        if isinstance(value, PasswordType):
            value = value.value
        self.set_attribute("password-type", value)

    @property
    def password_category(self) -> Optional[PasswordCategory]:
        """Get the password security category."""
        category_str = self.get_attribute("password-category-name")
        if category_str:
            try:
                return PasswordCategory(category_str.lower())
            except ValueError:
                return None
        return None

    @password_category.setter
    def password_category(self, value: Union[PasswordCategory, str]) -> None:
        """Set the password security category."""
        if isinstance(value, PasswordCategory):
            value = value.value
        self.set_attribute("password-category-name", value)

    @property
    def visibility(self) -> Optional[PasswordVisibility]:
        """Get the password visibility level."""
        visibility_str = self.get_attribute("visibility")
        return PasswordVisibility(visibility_str) if visibility_str else None

    @visibility.setter
    def visibility(self, value: Union[PasswordVisibility, str]) -> None:
        """Set the password visibility level."""
        if isinstance(value, PasswordVisibility):
            value = value.value
        self.set_attribute("visibility", value)

    # Security and metadata properties
    @property
    def auto_fill_selectors(self) -> Optional[str]:
        """Get the auto-fill selectors for web forms."""
        return self.get_attribute("autofill-selectors")

    @auto_fill_selectors.setter
    def auto_fill_selectors(self, value: str) -> None:
        """Set the auto-fill selectors for web forms."""
        self.set_attribute("autofill-selectors", value)

    @property
    def favorite(self) -> bool:
        """Check if password is marked as favorite."""
        return bool(self.get_attribute("favorite", False))

    @favorite.setter
    def favorite(self, value: bool) -> None:
        """Set password as favorite."""
        self.set_attribute("favorite", value)

    @property
    def archived(self) -> bool:
        """Check if password is archived."""
        return bool(self.get_attribute("archived", False))

    @archived.setter
    def archived(self, value: bool) -> None:
        """Set password archived status."""
        self.set_attribute("archived", value)

    # Timestamp properties
    @property
    def created_at(self) -> Optional[datetime]:
        """Get password creation timestamp."""
        created_str = self.get_attribute("created-at")
        return ITGlueDateTime.validate(created_str) if created_str else None

    @property
    def updated_at(self) -> Optional[datetime]:
        """Get password last update timestamp."""
        updated_str = self.get_attribute("updated-at")
        return ITGlueDateTime.validate(updated_str) if updated_str else None

    @property
    def password_updated_at(self) -> Optional[datetime]:
        """Get password value last update timestamp."""
        updated_str = self.get_attribute("password-updated-at")
        return ITGlueDateTime.validate(updated_str) if updated_str else None

    # Relationship properties
    @property
    def organization_id(self) -> Optional[str]:
        """Get the associated organization ID."""
        return self.get_related_id("organization")

    @property
    def organization_name(self) -> Optional[str]:
        """Get the associated organization name."""
        return self.get_attribute("organization-name")

    @property
    def resource_id(self) -> Optional[str]:
        """Get the associated resource ID (if linked to a resource)."""
        return self.get_related_id("resource")

    @property
    def resource_type_name(self) -> Optional[str]:
        """Get the type of resource this password is linked to."""
        return self.get_attribute("resource-type")

    @property
    def resource_name(self) -> Optional[str]:
        """Get the name of the resource this password is linked to."""
        return self.get_attribute("resource-name")

    # Security helper methods
    def is_critical(self) -> bool:
        """Check if password has critical security category."""
        return self.password_category == PasswordCategory.CRITICAL

    def is_high_security(self) -> bool:
        """Check if password has high or critical security category."""
        return self.password_category in [
            PasswordCategory.HIGH,
            PasswordCategory.CRITICAL,
        ]

    def is_shared(self) -> bool:
        """Check if password is shared (not private)."""
        return self.visibility != PasswordVisibility.PRIVATE

    def is_organization_visible(self) -> bool:
        """Check if password is visible to organization or everyone."""
        return self.visibility in [
            PasswordVisibility.ORGANIZATION,
            PasswordVisibility.EVERYONE,
        ]

    def is_embedded(self) -> bool:
        """Check if password is embedded type."""
        return self.password_type == PasswordType.EMBEDDED

    def is_linked(self) -> bool:
        """Check if password is linked to a resource."""
        return self.password_type == PasswordType.LINKED

    def is_recently_updated(self, days: int = 30) -> bool:
        """Check if password was updated within specified days."""
        if not self.password_updated_at:
            return False

        from datetime import timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return self.password_updated_at > cutoff

    def is_stale(self, days: int = 90) -> bool:
        """Check if password is stale (not updated for specified days)."""
        if not self.password_updated_at:
            return True

        from datetime import timedelta, timezone

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return self.password_updated_at < cutoff

    def get_age_days(self) -> Optional[int]:
        """Get password age in days since last update."""
        if not self.password_updated_at:
            return None

        from datetime import timezone

        now = datetime.now(timezone.utc)
        delta = now - self.password_updated_at
        return delta.days

    # String representation
    def __str__(self) -> str:
        """String representation of password."""
        if self.name and self.username:
            return f"Password: {self.name} ({self.username})"
        elif self.name:
            return f"Password: {self.name}"
        elif self.username:
            return f"Password: {self.username}"
        elif self.id:
            return f"Password: {self.id}"
        else:
            return "Password: None"


class PasswordCollection(ITGlueResourceCollection[Password]):
    """
    Collection of Password resources with enhanced querying capabilities.

    Provides methods for filtering, searching, and analyzing password collections
    with security-focused operations.
    """

    @classmethod
    def from_api_dict(cls, data: dict) -> "PasswordCollection":
        """Create collection from API response."""
        return super().from_api_dict(data, Password)

    def find_by_name(self, name: str) -> Optional[Password]:
        """Find password by exact name match."""
        name_lower = name.lower()
        for password in self.data:
            if password.name and password.name.lower() == name_lower:
                return password
        return None

    def search_by_name(self, query: str) -> List[Password]:
        """Search passwords by name (partial match, case-insensitive)."""
        query_lower = query.lower()
        results = []
        for password in self.data:
            if password.name and query_lower in password.name.lower():
                results.append(password)
        return results

    def find_by_username(self, username: str) -> List[Password]:
        """Find passwords by username."""
        username_lower = username.lower()
        results = []
        for password in self.data:
            if password.username and password.username.lower() == username_lower:
                results.append(password)
        return results

    def search_by_url(self, url_part: str) -> List[Password]:
        """Search passwords by URL (partial match)."""
        url_lower = url_part.lower()
        results = []
        for password in self.data:
            if password.url and url_lower in password.url.lower():
                results.append(password)
        return results

    def filter_by_organization(self, organization_id: str) -> List[Password]:
        """Filter passwords by organization ID."""
        results = []
        for password in self.data:
            if password.organization_id == organization_id:
                results.append(password)
        return results

    def filter_by_category(
        self, category: Union[PasswordCategory, str]
    ) -> List[Password]:
        """Filter passwords by security category."""
        if isinstance(category, str):
            try:
                category = PasswordCategory(category.lower())
            except ValueError:
                return []

        results = []
        for password in self.data:
            if password.password_category == category:
                results.append(password)
        return results

    def filter_by_visibility(
        self, visibility: Union[PasswordVisibility, str]
    ) -> List[Password]:
        """Filter passwords by visibility level."""
        if isinstance(visibility, str):
            try:
                visibility = PasswordVisibility(visibility.lower())
            except ValueError:
                return []

        results = []
        for password in self.data:
            if password.visibility == visibility:
                results.append(password)
        return results

    def filter_by_type(self, password_type: Union[PasswordType, str]) -> List[Password]:
        """Filter passwords by type."""
        if isinstance(password_type, str):
            try:
                password_type = PasswordType(password_type.lower())
            except ValueError:
                return []

        results = []
        for password in self.data:
            if password.password_type == password_type:
                results.append(password)
        return results

    def get_favorites(self) -> List[Password]:
        """Get all favorite passwords."""
        return [p for p in self.data if p.favorite]

    def get_archived(self) -> List[Password]:
        """Get all archived passwords."""
        return [p for p in self.data if p.archived]

    def get_active(self) -> List[Password]:
        """Get all non-archived passwords."""
        return [p for p in self.data if not p.archived]

    def get_critical_passwords(self) -> List[Password]:
        """Get passwords with critical security category."""
        return self.filter_by_category(PasswordCategory.CRITICAL)

    def get_high_security_passwords(self) -> List[Password]:
        """Get passwords with high or critical security categories."""
        results = []
        for password in self.data:
            if password.is_high_security():
                results.append(password)
        return results

    def get_shared_passwords(self) -> List[Password]:
        """Get all shared passwords (not private)."""
        return [p for p in self.data if p.is_shared()]

    def get_private_passwords(self) -> List[Password]:
        """Get all private passwords."""
        return self.filter_by_visibility(PasswordVisibility.PRIVATE)

    def get_stale_passwords(self, days: int = 90) -> List[Password]:
        """Get passwords that haven't been updated for specified days."""
        return [p for p in self.data if p.is_stale(days)]

    def get_recently_updated_passwords(self, days: int = 30) -> List[Password]:
        """Get passwords updated within specified days."""
        return [p for p in self.data if p.is_recently_updated(days)]

    def get_linked_passwords(self) -> List[Password]:
        """Get passwords linked to resources."""
        return self.filter_by_type(PasswordType.LINKED)

    def get_embedded_passwords(self) -> List[Password]:
        """Get embedded passwords."""
        return self.filter_by_type(PasswordType.EMBEDDED)

    # Security analysis methods
    def get_security_distribution(self) -> Dict[str, int]:
        """Get distribution of passwords by security category."""
        distribution = {category.value: 0 for category in PasswordCategory}

        for password in self.data:
            if password.password_category:
                distribution[password.password_category.value] += 1
            else:
                distribution["unknown"] = distribution.get("unknown", 0) + 1

        return distribution

    def get_visibility_distribution(self) -> Dict[str, int]:
        """Get distribution of passwords by visibility level."""
        distribution = {visibility.value: 0 for visibility in PasswordVisibility}

        for password in self.data:
            if password.visibility:
                distribution[password.visibility.value] += 1
            else:
                distribution["unknown"] = distribution.get("unknown", 0) + 1

        return distribution

    def get_type_distribution(self) -> Dict[str, int]:
        """Get distribution of passwords by type."""
        distribution = {ptype.value: 0 for ptype in PasswordType}

        for password in self.data:
            if password.password_type:
                distribution[password.password_type.value] += 1
            else:
                distribution["unknown"] = distribution.get("unknown", 0) + 1

        return distribution

    def get_security_statistics(self) -> Dict[str, Any]:
        """Get comprehensive security statistics for password collection."""
        total_passwords = len(self.data)
        active_passwords = len(self.get_active())

        return {
            "total_passwords": total_passwords,
            "active_passwords": active_passwords,
            "archived_passwords": len(self.get_archived()),
            "favorite_passwords": len(self.get_favorites()),
            "critical_passwords": len(self.get_critical_passwords()),
            "high_security_passwords": len(self.get_high_security_passwords()),
            "shared_passwords": len(self.get_shared_passwords()),
            "private_passwords": len(self.get_private_passwords()),
            "stale_passwords_90d": len(self.get_stale_passwords(90)),
            "recently_updated_30d": len(self.get_recently_updated_passwords(30)),
            "linked_passwords": len(self.get_linked_passwords()),
            "embedded_passwords": len(self.get_embedded_passwords()),
            "security_distribution": self.get_security_distribution(),
            "visibility_distribution": self.get_visibility_distribution(),
            "type_distribution": self.get_type_distribution(),
        }

    def to_list(self) -> List[Password]:
        """Convert collection to a standard list."""
        return list(self.data)
