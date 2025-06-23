"""
Passwords API for ITGlue.

This module provides the PasswordsAPI class for managing password resources
with security-focused operations, comprehensive filtering, and audit capabilities.
"""

from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from .base import BaseAPI
from ..models.password import (
    Password,
    PasswordCollection,
    PasswordCategory,
    PasswordVisibility,
    PasswordType,
)
from ..models.base import ResourceType


class PasswordsAPI(BaseAPI[Password]):
    """
    API client for ITGlue Passwords.

    Provides comprehensive password management including creation, updates,
    security filtering, sharing controls, and audit capabilities.
    """

    def __init__(self, http_client):
        """Initialize PasswordsAPI with HTTP client."""
        super().__init__(
            client=http_client,
            resource_type=ResourceType.PASSWORDS,
            model_class=Password,
            endpoint_path="passwords",
        )

    # Core CRUD operations (inherited from BaseAPI)
    # - create(data)
    # - get(password_id)
    # - update(password_id, data)
    # - delete(password_id)
    # - list(params)

    # Password-specific search and filter methods

    async def search_passwords(
        self, query: str, organization_id: Optional[str] = None, **params
    ) -> List[Password]:
        """
        Search passwords by name, username, or URL.

        Args:
            query: Search query string
            organization_id: Optional organization filter
            **params: Additional query parameters

        Returns:
            List of matching passwords
        """
        search_params = {"filter[name]": query, **params}

        if organization_id:
            search_params["filter[organization-id]"] = organization_id

        result = await self.list(params=search_params)
        if isinstance(result, PasswordCollection):
            return result.to_list()
        return result if isinstance(result, list) else []

    async def get_by_name(
        self, name: str, organization_id: Optional[str] = None
    ) -> Optional[Password]:
        """
        Get password by exact name match.

        Args:
            name: Exact password name
            organization_id: Optional organization filter

        Returns:
            Password if found, None otherwise
        """
        params = {"filter[name]": name}

        if organization_id:
            params["filter[organization-id]"] = organization_id

        result = await self.list(params=params)

        # Convert to list if needed
        if isinstance(result, PasswordCollection):
            passwords = result.to_list()
        else:
            passwords = result if isinstance(result, list) else []

        # Find exact match (case-insensitive)
        name_lower = name.lower()
        for password in passwords:
            if password.name and password.name.lower() == name_lower:
                return password

        return None

    async def search_by_username(
        self, username: str, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Search passwords by username.

        Args:
            username: Username to search for
            organization_id: Optional organization filter

        Returns:
            List of matching passwords
        """
        params = {"filter[username]": username}

        if organization_id:
            params["filter[organization-id]"] = organization_id

        return await self.list(params=params)

    async def search_by_url(
        self, url: str, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Search passwords by URL.

        Args:
            url: URL to search for
            organization_id: Optional organization filter

        Returns:
            List of matching passwords
        """
        params = {"filter[url]": url}

        if organization_id:
            params["filter[organization-id]"] = organization_id

        return await self.list(params=params)

    # Organization-based filtering

    async def get_organization_passwords(
        self, organization_id: str, include_archived: bool = False, **params
    ) -> List[Password]:
        """
        Get all passwords for a specific organization.

        Args:
            organization_id: Organization ID
            include_archived: Whether to include archived passwords
            **params: Additional query parameters

        Returns:
            List of organization passwords
        """
        filter_params = {"filter[organization-id]": organization_id, **params}

        if not include_archived:
            filter_params["filter[archived]"] = "false"

        return await self.list(params=filter_params)

    # Security and visibility filtering

    async def filter_by_category(
        self,
        category: Union[PasswordCategory, str],
        organization_id: Optional[str] = None,
        **params
    ) -> List[Password]:
        """
        Filter passwords by security category.

        Args:
            category: Password security category
            organization_id: Optional organization filter
            **params: Additional query parameters

        Returns:
            List of passwords with specified category
        """
        if isinstance(category, PasswordCategory):
            category = category.value

        filter_params = {"filter[password-category-name]": category, **params}

        if organization_id:
            filter_params["filter[organization-id]"] = organization_id

        return await self.list(params=filter_params)

    async def filter_by_visibility(
        self,
        visibility: Union[PasswordVisibility, str],
        organization_id: Optional[str] = None,
        **params
    ) -> List[Password]:
        """
        Filter passwords by visibility level.

        Args:
            visibility: Password visibility level
            organization_id: Optional organization filter
            **params: Additional query parameters

        Returns:
            List of passwords with specified visibility
        """
        if isinstance(visibility, PasswordVisibility):
            visibility = visibility.value

        filter_params = {"filter[visibility]": visibility, **params}

        if organization_id:
            filter_params["filter[organization-id]"] = organization_id

        return await self.list(params=filter_params)

    async def filter_by_type(
        self,
        password_type: Union[PasswordType, str],
        organization_id: Optional[str] = None,
        **params
    ) -> List[Password]:
        """
        Filter passwords by type.

        Args:
            password_type: Password type (embedded/linked)
            organization_id: Optional organization filter
            **params: Additional query parameters

        Returns:
            List of passwords with specified type
        """
        if isinstance(password_type, PasswordType):
            password_type = password_type.value

        filter_params = {"filter[password-type]": password_type, **params}

        if organization_id:
            filter_params["filter[organization-id]"] = organization_id

        return await self.list(params=filter_params)

    # Security-focused methods

    async def get_critical_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get passwords with critical security category.

        Args:
            organization_id: Optional organization filter

        Returns:
            List of critical passwords
        """
        return await self.filter_by_category(PasswordCategory.CRITICAL, organization_id)

    async def get_high_security_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get passwords with high or critical security categories.

        Args:
            organization_id: Optional organization filter

        Returns:
            List of high security passwords
        """
        high_passwords = await self.filter_by_category(
            PasswordCategory.HIGH, organization_id
        )
        critical_passwords = await self.filter_by_category(
            PasswordCategory.CRITICAL, organization_id
        )

        # Combine and deduplicate
        all_passwords = high_passwords + critical_passwords
        seen_ids = set()
        unique_passwords = []

        for password in all_passwords:
            if password.id not in seen_ids:
                unique_passwords.append(password)
                seen_ids.add(password.id)

        return unique_passwords

    async def get_shared_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get passwords that are shared (not private).

        Args:
            organization_id: Optional organization filter

        Returns:
            List of shared passwords
        """
        # Get passwords with different visibility levels
        shared_passwords = await self.filter_by_visibility(
            PasswordVisibility.SHARED, organization_id
        )
        org_passwords = await self.filter_by_visibility(
            PasswordVisibility.ORGANIZATION, organization_id
        )
        everyone_passwords = await self.filter_by_visibility(
            PasswordVisibility.EVERYONE, organization_id
        )

        # Combine and deduplicate
        all_passwords = shared_passwords + org_passwords + everyone_passwords
        seen_ids = set()
        unique_passwords = []

        for password in all_passwords:
            if password.id not in seen_ids:
                unique_passwords.append(password)
                seen_ids.add(password.id)

        return unique_passwords

    async def get_private_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get private passwords.

        Args:
            organization_id: Optional organization filter

        Returns:
            List of private passwords
        """
        return await self.filter_by_visibility(
            PasswordVisibility.PRIVATE, organization_id
        )

    async def get_embedded_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get embedded passwords.

        Args:
            organization_id: Optional organization filter

        Returns:
            List of embedded passwords
        """
        return await self.filter_by_type(PasswordType.EMBEDDED, organization_id)

    async def get_linked_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get linked passwords.

        Args:
            organization_id: Optional organization filter

        Returns:
            List of linked passwords
        """
        return await self.filter_by_type(PasswordType.LINKED, organization_id)

    # Special state filtering

    async def get_favorite_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get favorite passwords.

        Args:
            organization_id: Optional organization filter

        Returns:
            List of favorite passwords
        """
        params = {"filter[favorite]": "true"}

        if organization_id:
            params["filter[organization-id]"] = organization_id

        return await self.list(params=params)

    async def get_archived_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get archived passwords.

        Args:
            organization_id: Optional organization filter

        Returns:
            List of archived passwords
        """
        params = {"filter[archived]": "true"}

        if organization_id:
            params["filter[organization-id]"] = organization_id

        return await self.list(params=params)

    async def get_active_passwords(
        self, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get active (non-archived) passwords.

        Args:
            organization_id: Optional organization filter

        Returns:
            List of active passwords
        """
        params = {"filter[archived]": "false"}

        if organization_id:
            params["filter[organization-id]"] = organization_id

        return await self.list(params=params)

    # Time-based filtering

    async def get_recently_updated_passwords(
        self, days: int = 30, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get passwords updated within specified days.

        Args:
            days: Number of days to look back
            organization_id: Optional organization filter

        Returns:
            List of recently updated passwords
        """
        from datetime import datetime, timedelta, timezone

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()

        params = {"filter[updated-at][gt]": cutoff_str}

        if organization_id:
            params["filter[organization-id]"] = organization_id

        return await self.list(params=params)

    async def get_stale_passwords(
        self, days: int = 90, organization_id: Optional[str] = None
    ) -> List[Password]:
        """
        Get passwords not updated for specified days.

        Args:
            days: Number of days threshold
            organization_id: Optional organization filter

        Returns:
            List of stale passwords
        """
        from datetime import datetime, timedelta, timezone

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()

        params = {"filter[password-updated-at][lt]": cutoff_str}

        if organization_id:
            params["filter[organization-id]"] = organization_id

        return await self.list(params=params)

    # Password management operations

    async def create_password(
        self,
        name: str,
        username: str,
        password: str,
        organization_id: str,
        url: Optional[str] = None,
        notes: Optional[str] = None,
        password_type: Union[PasswordType, str] = PasswordType.EMBEDDED,
        password_category: Union[PasswordCategory, str] = PasswordCategory.LOW,
        visibility: Union[PasswordVisibility, str] = PasswordVisibility.PRIVATE,
        favorite: bool = False,
        **additional_fields
    ) -> Password:
        """
        Create a new password.

        Args:
            name: Password name/title
            username: Username
            password: Password value
            organization_id: Organization ID
            url: Optional URL
            notes: Optional notes
            password_type: Password type
            password_category: Security category
            visibility: Visibility level
            favorite: Whether to mark as favorite
            **additional_fields: Additional fields

        Returns:
            Created password
        """
        # Convert enums to strings
        if isinstance(password_type, PasswordType):
            password_type = password_type.value
        if isinstance(password_category, PasswordCategory):
            password_category = password_category.value
        if isinstance(visibility, PasswordVisibility):
            visibility = visibility.value

        data = {
            "type": ResourceType.PASSWORDS.value,
            "attributes": {
                "name": name,
                "username": username,
                "password": password,
                "password-type": password_type,
                "password-category-name": password_category,
                "visibility": visibility,
                "favorite": favorite,
                **additional_fields,
            },
            "relationships": {
                "organization": {
                    "data": {
                        "type": ResourceType.ORGANIZATIONS.value,
                        "id": organization_id,
                    }
                }
            },
        }

        if url:
            data["attributes"]["url"] = url
        if notes:
            data["attributes"]["notes"] = notes

        return await self.create(data)

    async def update_password_value(
        self, password_id: str, new_password: str
    ) -> Password:
        """
        Update password value.

        Args:
            password_id: Password ID
            new_password: New password value

        Returns:
            Updated password
        """
        data = {
            "type": ResourceType.PASSWORDS.value,
            "attributes": {"password": new_password},
        }

        return await self.update(password_id, data)

    async def update_password_visibility(
        self, password_id: str, visibility: Union[PasswordVisibility, str]
    ) -> Password:
        """
        Update password visibility.

        Args:
            password_id: Password ID
            visibility: New visibility level

        Returns:
            Updated password
        """
        if isinstance(visibility, PasswordVisibility):
            visibility = visibility.value

        data = {
            "type": ResourceType.PASSWORDS.value,
            "attributes": {"visibility": visibility},
        }

        return await self.update(password_id, data)

    async def update_password_category(
        self, password_id: str, category: Union[PasswordCategory, str]
    ) -> Password:
        """
        Update password security category.

        Args:
            password_id: Password ID
            category: New security category

        Returns:
            Updated password
        """
        if isinstance(category, PasswordCategory):
            category = category.value

        data = {
            "type": ResourceType.PASSWORDS.value,
            "attributes": {"password-category-name": category},
        }

        return await self.update(password_id, data)

    async def toggle_favorite(self, password_id: str) -> Password:
        """
        Toggle password favorite status.

        Args:
            password_id: Password ID

        Returns:
            Updated password
        """
        # Get current password to check favorite status
        password = await self.get(password_id)
        new_favorite = not password.favorite

        data = {
            "type": ResourceType.PASSWORDS.value,
            "attributes": {"favorite": new_favorite},
        }

        return await self.update(password_id, data)

    async def archive_password(self, password_id: str) -> Password:
        """
        Archive a password.

        Args:
            password_id: Password ID

        Returns:
            Updated password
        """
        data = {"type": ResourceType.PASSWORDS.value, "attributes": {"archived": True}}

        return await self.update(password_id, data)

    async def unarchive_password(self, password_id: str) -> Password:
        """
        Unarchive a password.

        Args:
            password_id: Password ID

        Returns:
            Updated password
        """
        data = {"type": ResourceType.PASSWORDS.value, "attributes": {"archived": False}}

        return await self.update(password_id, data)

    # Analytics and reporting

    async def get_password_statistics(
        self, organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive password statistics.

        Args:
            organization_id: Optional organization filter

        Returns:
            Dictionary with password statistics
        """
        # Get all active passwords
        all_passwords = await self.get_active_passwords(organization_id)

        if not all_passwords:
            return {
                "total_passwords": 0,
                "active_passwords": 0,
                "archived_passwords": 0,
                "critical_passwords": 0,
                "high_security_passwords": 0,
                "shared_passwords": 0,
                "private_passwords": 0,
                "favorite_passwords": 0,
                "linked_passwords": 0,
                "embedded_passwords": 0,
                "security_distribution": {},
                "visibility_distribution": {},
                "type_distribution": {},
            }

        # Convert to collection for analysis
        collection = PasswordCollection.from_api_dict(
            {"data": [p.model_dump_api() for p in all_passwords]}
        )

        # Get archived count separately
        archived_passwords = await self.get_archived_passwords(organization_id)

        # Calculate statistics
        stats = collection.get_security_statistics()
        stats["archived_passwords"] = len(archived_passwords)
        stats["total_passwords"] = (
            stats["active_passwords"] + stats["archived_passwords"]
        )

        return stats

    async def get_organization_password_report(
        self, organization_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive password report for an organization.

        Args:
            organization_id: Organization ID

        Returns:
            Comprehensive password report
        """
        stats = await self.get_password_statistics(organization_id)
        stale_passwords = await self.get_stale_passwords(90, organization_id)
        recent_passwords = await self.get_recently_updated_passwords(
            30, organization_id
        )

        return {
            **stats,
            "stale_passwords_90d": len(stale_passwords),
            "recently_updated_30d": len(recent_passwords),
            "security_recommendations": {
                "critical_review_needed": stats["critical_passwords"] > 0,
                "stale_passwords_need_update": len(stale_passwords) > 0,
                "consider_upgrading_low_security": stats["security_distribution"].get(
                    "low", 0
                )
                > 0,
                "review_shared_passwords": stats["shared_passwords"]
                > stats["private_passwords"],
            },
        }
