"""
Users API for ITGlue.

This module provides the API interface for managing ITGlue users,
including user account management, role assignments, authentication details,
and MyGlue integration capabilities.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from .base import BaseAPI
from ..models.base import ResourceType
from ..models.user import User, UserCollection, UserRole
from ..exceptions import ITGlueAPIError


class UsersAPI(BaseAPI[User]):
    """
    API class for managing ITGlue users.

    Provides methods for user account management, authentication tracking,
    role assignments, and MyGlue integration.
    """

    def __init__(self, client):
        """Initialize the Users API."""
        super().__init__(client, ResourceType.USERS, User, "users")

    async def get_by_email(self, email: str, **kwargs) -> Optional[User]:
        """
        Get a user by email address.

        Args:
            email: The email address to search for
            **kwargs: Additional query parameters

        Returns:
            User object if found, None otherwise

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            params = {"filter[email]": email}
            params.update(kwargs)

            result = await self.list(params=params, page_size=1)
            if isinstance(result, UserCollection) and len(result) > 0:
                return result[0]
            elif isinstance(result, list) and len(result) > 0:
                return result[0]
            return None

        except Exception as e:
            raise ITGlueAPIError(f"Failed to get user by email: {str(e)}") from e

    async def search_by_name(self, name: str, **kwargs) -> List[User]:
        """
        Search users by name (first name, last name, or full name).

        Args:
            name: The name to search for (partial matches supported)
            **kwargs: Additional query parameters

        Returns:
            List of matching User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            # Search by first name, last name, or combined
            params = {"filter[first-name]": name, "filter[last-name]": name}
            params.update(kwargs)

            result = await self.list(params=params)
            if isinstance(result, UserCollection):
                return result.to_list()
            return result if isinstance(result, list) else []

        except Exception as e:
            raise ITGlueAPIError(f"Failed to search users by name: {str(e)}") from e

    async def filter_by_role(self, role: Union[str, UserRole], **kwargs) -> List[User]:
        """
        Get users by role.

        Args:
            role: User role (Admin, Creator, Editor, Lite, Viewer)
            **kwargs: Additional query parameters

        Returns:
            List of User objects with the specified role

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            role_name = role.value if isinstance(role, UserRole) else role
            params = {"filter[role-name]": role_name}
            params.update(kwargs)

            result = await self.list(params=params)
            if isinstance(result, UserCollection):
                return result.to_list()
            return result if isinstance(result, list) else []

        except Exception as e:
            raise ITGlueAPIError(f"Failed to filter users by role: {str(e)}") from e

    async def get_active_users(self, **kwargs) -> List[User]:
        """
        Get all active users (users who have accepted their invitation).

        Args:
            **kwargs: Additional query parameters

        Returns:
            List of active User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            # Filter for users with invitation-accepted-at not null
            params = {"filter[invitation-accepted-at]": "!null"}
            params.update(kwargs)

            result = await self.list(params=params)
            if isinstance(result, UserCollection):
                return result.filter_active_users()
            return (
                [user for user in result if user.is_active()]
                if isinstance(result, list)
                else []
            )

        except Exception as e:
            raise ITGlueAPIError(f"Failed to get active users: {str(e)}") from e

    async def get_invited_users(self, **kwargs) -> List[User]:
        """
        Get users who have been invited but haven't accepted yet.

        Args:
            **kwargs: Additional query parameters

        Returns:
            List of invited User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            # Filter for users with invitation-sent-at not null and invitation-accepted-at null
            params = {
                "filter[invitation-sent-at]": "!null",
                "filter[invitation-accepted-at]": "null",
            }
            params.update(kwargs)

            result = await self.list(params=params)
            if isinstance(result, UserCollection):
                return result.filter_invited_users()
            return (
                [user for user in result if user.is_invited()]
                if isinstance(result, list)
                else []
            )

        except Exception as e:
            raise ITGlueAPIError(f"Failed to get invited users: {str(e)}") from e

    async def get_my_glue_users(self, **kwargs) -> List[User]:
        """
        Get users with MyGlue access.

        Args:
            **kwargs: Additional query parameters

        Returns:
            List of User objects with MyGlue access

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            params = {"filter[my-glue]": "true"}
            params.update(kwargs)

            result = await self.list(params=params)
            if isinstance(result, UserCollection):
                return result.filter_by_my_glue_access(True)
            return (
                [user for user in result if user.has_my_glue_access()]
                if isinstance(result, list)
                else []
            )

        except Exception as e:
            raise ITGlueAPIError(f"Failed to get MyGlue users: {str(e)}") from e

    async def get_recently_active_users(self, days: int = 30, **kwargs) -> List[User]:
        """
        Get users who have been active within the specified number of days.

        Args:
            days: Number of days to look back for activity (default: 30)
            **kwargs: Additional query parameters

        Returns:
            List of recently active User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            from datetime import datetime, timedelta, timezone

            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            cutoff_str = cutoff_date.strftime("%Y-%m-%d")

            params = {"filter[last-sign-in-at]": f">={cutoff_str}"}
            params.update(kwargs)

            result = await self.list(params=params)
            if isinstance(result, UserCollection):
                return result.get_recently_active_users(days)

            # Manual filtering if needed
            if isinstance(result, list):
                active_users = []
                for user in result:
                    activity_days = user.calculate_activity_days()
                    if activity_days is not None and activity_days <= days:
                        active_users.append(user)
                return active_users

            return []

        except Exception as e:
            raise ITGlueAPIError(
                f"Failed to get recently active users: {str(e)}"
            ) from e

    async def get_top_reputation_users(self, limit: int = 10, **kwargs) -> List[User]:
        """
        Get users with the highest reputation scores.

        Args:
            limit: Maximum number of users to return (default: 10)
            **kwargs: Additional query parameters

        Returns:
            List of User objects sorted by reputation (highest first)

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            params = {"sort": "-reputation", "page[size]": str(limit)}
            params.update(kwargs)

            result = await self.list(params=params)
            if isinstance(result, UserCollection):
                return result.get_top_reputation_users(limit)

            # Manual sorting if needed
            if isinstance(result, list):
                sorted_users = sorted(
                    [user for user in result if user.reputation is not None],
                    key=lambda u: u.reputation or 0,
                    reverse=True,
                )
                return sorted_users[:limit]

            return []

        except Exception as e:
            raise ITGlueAPIError(f"Failed to get top reputation users: {str(e)}") from e

    async def create_user(self, user_data: Dict[str, Any], **kwargs) -> User:
        """
        Create a new user account.

        Args:
            user_data: Dictionary containing user information
            **kwargs: Additional parameters

        Returns:
            Created User object

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            return await self.create(user_data, **kwargs)

        except Exception as e:
            raise ITGlueAPIError(f"Failed to create user: {str(e)}") from e

    async def update_user_role(
        self, user_id: str, role: Union[str, UserRole], **kwargs
    ) -> User:
        """
        Update a user's role.

        Args:
            user_id: ID of the user to update
            role: New role for the user
            **kwargs: Additional parameters

        Returns:
            Updated User object

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            role_name = role.value if isinstance(role, UserRole) else role
            update_data = {"role-name": role_name}

            return await self.update(user_id, update_data, **kwargs)

        except Exception as e:
            raise ITGlueAPIError(f"Failed to update user role: {str(e)}") from e

    async def update_user_profile(
        self, user_id: str, profile_data: Dict[str, Any], **kwargs
    ) -> User:
        """
        Update user profile information.

        Args:
            user_id: ID of the user to update
            profile_data: Dictionary containing profile updates
            **kwargs: Additional parameters

        Returns:
            Updated User object

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            return await self.update(user_id, profile_data, **kwargs)

        except Exception as e:
            raise ITGlueAPIError(f"Failed to update user profile: {str(e)}") from e

    async def resend_invitation(self, user_id: str, **kwargs) -> bool:
        """
        Resend invitation to a user.

        Args:
            user_id: ID of the user to resend invitation to
            **kwargs: Additional parameters

        Returns:
            True if successful

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            # This would typically be a POST to a specific endpoint
            endpoint = f"{self.endpoint_path}/{user_id}/resend_invitation"
            await self.client.post(endpoint, **kwargs)
            return True

        except Exception as e:
            raise ITGlueAPIError(f"Failed to resend invitation: {str(e)}") from e

    async def get_user_statistics(self, **kwargs) -> Dict[str, Any]:
        """
        Get statistics about users in the system.

        Args:
            **kwargs: Additional query parameters

        Returns:
            Dictionary containing user statistics

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            # Get all users for statistics calculation
            all_users = await self.list(**kwargs)

            if isinstance(all_users, UserCollection):
                collection = all_users
            else:
                collection = UserCollection(
                    all_users if isinstance(all_users, list) else []
                )

            # Calculate various statistics
            role_distribution = collection.get_role_distribution()
            my_glue_stats = collection.get_my_glue_statistics()

            active_users = collection.filter_active_users()
            invited_users = collection.filter_invited_users()
            recent_users = collection.get_recently_active_users(30)
            top_users = collection.get_top_reputation_users(5)

            return {
                "total_users": len(collection),
                "active_users": len(active_users),
                "invited_users": len(invited_users),
                "recently_active_users": len(recent_users),
                "role_distribution": role_distribution,
                "my_glue_statistics": my_glue_stats,
                "top_reputation_users": [
                    {
                        "id": user.id,
                        "name": user.full_name,
                        "email": user.email,
                        "reputation": user.reputation,
                    }
                    for user in top_users
                ],
                "average_reputation": round(
                    (
                        sum(user.reputation or 0 for user in collection)
                        / len(collection)
                        if len(collection) > 0
                        else 0
                    ),
                    2,
                ),
            }

        except Exception as e:
            raise ITGlueAPIError(f"Failed to get user statistics: {str(e)}") from e

    async def search_users(self, query: str, **kwargs) -> List[User]:
        """
        Search users by multiple criteria (name, email, etc.).

        Args:
            query: Search query string
            **kwargs: Additional query parameters

        Returns:
            List of matching User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        try:
            # Try multiple search approaches
            results = []

            # Search by email
            if "@" in query:
                email_result = await self.get_by_email(query, **kwargs)
                if email_result:
                    results.append(email_result)

            # Search by name
            name_results = await self.search_by_name(query, **kwargs)
            results.extend(name_results)

            # Remove duplicates while preserving order
            seen = set()
            unique_results = []
            for user in results:
                if user.id not in seen:
                    seen.add(user.id)
                    unique_results.append(user)

            return unique_results

        except Exception as e:
            raise ITGlueAPIError(f"Failed to search users: {str(e)}") from e

    async def get_admin_users(self, **kwargs) -> List[User]:
        """
        Get all users with admin role.

        Args:
            **kwargs: Additional query parameters

        Returns:
            List of admin User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        return await self.filter_by_role(UserRole.ADMIN, **kwargs)

    async def get_creator_users(self, **kwargs) -> List[User]:
        """
        Get all users with creator role.

        Args:
            **kwargs: Additional query parameters

        Returns:
            List of creator User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        return await self.filter_by_role(UserRole.CREATOR, **kwargs)

    async def get_editor_users(self, **kwargs) -> List[User]:
        """
        Get all users with editor role.

        Args:
            **kwargs: Additional query parameters

        Returns:
            List of editor User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        return await self.filter_by_role(UserRole.EDITOR, **kwargs)

    async def get_lite_users(self, **kwargs) -> List[User]:
        """
        Get all users with lite role.

        Args:
            **kwargs: Additional query parameters

        Returns:
            List of lite User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        return await self.filter_by_role(UserRole.LITE, **kwargs)

    async def get_viewer_users(self, **kwargs) -> List[User]:
        """
        Get all users with viewer role.

        Args:
            **kwargs: Additional query parameters

        Returns:
            List of viewer User objects

        Raises:
            ITGlueAPIError: If the API request fails
        """
        return await self.filter_by_role(UserRole.VIEWER, **kwargs)
