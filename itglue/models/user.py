"""
User model for ITGlue API.

This module contains the User model and related functionality for managing
ITGlue user accounts, including profile information, authentication details,
reputation scoring, and MyGlue integration support.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from enum import Enum

from .base import BaseModel, ITGlueResource, ResourceType, ITGlueResourceCollection


class UserRole(Enum):
    """User role types in ITGlue."""

    ADMIN = "Admin"
    CREATOR = "Creator"
    EDITOR = "Editor"
    LITE = "Lite"
    VIEWER = "Viewer"


class UserStatus(Enum):
    """User account status types."""

    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class User(ITGlueResource):
    """
    Represents a User in ITGlue.

    A user refers to anyone who can authenticate to IT Glue.
    This model provides access to user profile information, authentication details,
    reputation scoring, and MyGlue integration capabilities.
    """

    def __init__(self, **data):
        """Initialize a User instance."""
        if "type" not in data:
            data["type"] = ResourceType.USERS
        super().__init__(**data)

    def __setattr__(self, name: str, value: Any) -> None:
        """Override setattr to handle property setters for hyphenated attributes."""
        # Define mapping of Python property names to API attribute names
        property_mappings = {
            "first_name": "first-name",
            "last_name": "last-name",
            "role_name": "role-name",
            "email": "email",
            "avatar": "avatar",
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

    # Core profile properties
    @property
    def first_name(self) -> Optional[str]:
        """Get the user's first name."""
        return self.get_attribute("first-name")

    @first_name.setter
    def first_name(self, value: Optional[str]) -> None:
        """Set the user's first name."""
        self.set_attribute("first-name", value)

    @property
    def last_name(self) -> Optional[str]:
        """Get the user's last name."""
        return self.get_attribute("last-name")

    @last_name.setter
    def last_name(self, value: Optional[str]) -> None:
        """Set the user's last name."""
        self.set_attribute("last-name", value)

    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else ""

    @property
    def email(self) -> Optional[str]:
        """Get the user's email address."""
        return self.get_attribute("email")

    @email.setter
    def email(self, value: Optional[str]) -> None:
        """Set the user's email address."""
        self.set_attribute("email", value)

    @property
    def role_name(self) -> Optional[str]:
        """Get the user's role name."""
        return self.get_attribute("role-name")

    @role_name.setter
    def role_name(self, value: Optional[str]) -> None:
        """Set the user's role name."""
        self.set_attribute("role-name", value)

    @property
    def avatar(self) -> Optional[str]:
        """Get the user's avatar URL or data."""
        return self.get_attribute("avatar")

    @avatar.setter
    def avatar(self, value: Optional[str]) -> None:
        """Set the user's avatar."""
        self.set_attribute("avatar", value)

    # Authentication & activity properties
    @property
    def invitation_sent_at(self) -> Optional[datetime]:
        """Get when the invitation was sent."""
        value = self.get_attribute("invitation-sent-at")
        if value and isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    @property
    def invitation_accepted_at(self) -> Optional[datetime]:
        """Get when the invitation was accepted."""
        value = self.get_attribute("invitation-accepted-at")
        if value and isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    @property
    def current_sign_in_at(self) -> Optional[datetime]:
        """Get the current sign-in timestamp."""
        value = self.get_attribute("current-sign-in-at")
        if value and isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    @property
    def current_sign_in_ip(self) -> Optional[str]:
        """Get the current sign-in IP address."""
        return self.get_attribute("current-sign-in-ip")

    @property
    def last_sign_in_at(self) -> Optional[datetime]:
        """Get when the user last signed in."""
        value = self.get_attribute("last-sign-in-at")
        if value and isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    @property
    def last_sign_in_ip(self) -> Optional[str]:
        """Get the last sign-in IP address."""
        return self.get_attribute("last-sign-in-ip")

    # Reputation & engagement properties
    @property
    def reputation(self) -> Optional[int]:
        """Get the user's reputation score."""
        return self.get_attribute("reputation")

    # MyGlue integration properties
    @property
    def my_glue(self) -> Optional[bool]:
        """Get whether the user has MyGlue access."""
        return self.get_attribute("my-glue")

    @property
    def my_glue_account_id(self) -> Optional[int]:
        """Get the MyGlue account ID."""
        return self.get_attribute("my-glue-account-id")

    # Status and configuration
    @property
    def status(self) -> Optional[str]:
        """Get the user's account status."""
        return self.get_attribute("status")

    @property
    def salesforce_id(self) -> Optional[int]:
        """Get the Salesforce integration ID."""
        return self.get_attribute("salesforce-id")

    # Helper methods
    def is_admin(self) -> bool:
        """Check if the user has admin role."""
        return self.role_name == UserRole.ADMIN.value

    def is_creator(self) -> bool:
        """Check if the user has creator role."""
        return self.role_name == UserRole.CREATOR.value

    def is_editor(self) -> bool:
        """Check if the user has editor role."""
        return self.role_name == UserRole.EDITOR.value

    def is_lite(self) -> bool:
        """Check if the user has lite role."""
        return self.role_name == UserRole.LITE.value

    def is_viewer(self) -> bool:
        """Check if the user has viewer role."""
        return self.role_name == UserRole.VIEWER.value

    def has_my_glue_access(self) -> bool:
        """Check if the user has MyGlue access."""
        return bool(self.my_glue)

    def is_invited(self) -> bool:
        """Check if the user has been invited but not yet accepted."""
        return (
            self.invitation_sent_at is not None and self.invitation_accepted_at is None
        )

    def is_active(self) -> bool:
        """Check if the user has accepted their invitation."""
        return self.invitation_accepted_at is not None

    def get_reputation_level(self) -> str:
        """Get a descriptive reputation level based on score."""
        if not self.reputation:
            return "No Activity"

        if self.reputation >= 10000:
            return "Expert"
        elif self.reputation >= 5000:
            return "Advanced"
        elif self.reputation >= 1000:
            return "Intermediate"
        elif self.reputation >= 100:
            return "Beginner"
        else:
            return "Novice"

    def calculate_activity_days(self) -> Optional[int]:
        """Calculate days since last sign-in."""
        if not self.last_sign_in_at:
            return None

        from datetime import timezone

        now = datetime.now(timezone.utc)
        if self.last_sign_in_at.tzinfo is None:
            last_sign_in = self.last_sign_in_at.replace(tzinfo=timezone.utc)
        else:
            last_sign_in = self.last_sign_in_at

        delta = now - last_sign_in
        return delta.days

    def __str__(self) -> str:
        """Return string representation of the user."""
        name = self.full_name
        if name:
            return f"User: {name} ({self.email})"
        return f"User: {self.email}" if self.email else f"User: {self.id}"


class UserCollection(ITGlueResourceCollection[User]):
    """Collection class for managing multiple User objects."""

    @classmethod
    def from_api_dict(cls, data: dict) -> "UserCollection":
        """Create collection from API response."""
        return super().from_api_dict(data, User)

    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by email address."""
        for user in self.data:
            if user.email and user.email.lower() == email.lower():
                return user
        return None

    def find_by_name(self, name: str) -> List[User]:
        """Find users by name (partial match)."""
        name_lower = name.lower()
        matches = []

        for user in self.data:
            if (
                user.full_name.lower().find(name_lower) != -1
                or (user.first_name and user.first_name.lower().find(name_lower) != -1)
                or (user.last_name and user.last_name.lower().find(name_lower) != -1)
            ):
                matches.append(user)

        return matches

    def filter_by_role(self, role: Union[str, UserRole]) -> List[User]:
        """Filter users by role."""
        role_name = role.value if isinstance(role, UserRole) else role
        return [user for user in self.data if user.role_name == role_name]

    def filter_by_my_glue_access(self, has_access: bool = True) -> List[User]:
        """Filter users by MyGlue access."""
        return [user for user in self.data if user.has_my_glue_access() == has_access]

    def filter_active_users(self) -> List[User]:
        """Filter to only active users."""
        return [user for user in self.data if user.is_active()]

    def filter_invited_users(self) -> List[User]:
        """Filter to only invited but not yet active users."""
        return [user for user in self.data if user.is_invited()]

    def get_top_reputation_users(self, limit: int = 10) -> List[User]:
        """Get users with highest reputation scores."""
        sorted_users = sorted(
            [user for user in self.data if user.reputation is not None],
            key=lambda u: u.reputation or 0,
            reverse=True,
        )
        return sorted_users[:limit]

    def get_recently_active_users(self, days: int = 30) -> List[User]:
        """Get users who have been active within the specified days."""
        active_users = []
        for user in self.data:
            activity_days = user.calculate_activity_days()
            if activity_days is not None and activity_days <= days:
                active_users.append(user)
        return active_users

    def get_role_distribution(self) -> Dict[str, int]:
        """Get distribution of users by role."""
        distribution = {}
        for user in self.data:
            role = user.role_name or "Unknown"
            distribution[role] = distribution.get(role, 0) + 1
        return distribution

    def get_my_glue_statistics(self) -> Dict[str, int]:
        """Get MyGlue access statistics."""
        total = len(self.data)
        with_access = len(self.filter_by_my_glue_access(True))
        without_access = total - with_access

        return {
            "total_users": total,
            "with_my_glue_access": with_access,
            "without_my_glue_access": without_access,
            "my_glue_adoption_percentage": round(
                (with_access / total * 100) if total > 0 else 0, 2
            ),
        }

    def to_list(self) -> List[User]:
        """Convert collection to list."""
        return self.data.copy()
