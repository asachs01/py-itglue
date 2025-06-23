"""
Tests for Users API.

This module tests the Users API functionality including user management,
role assignments, search capabilities, and user statistics.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone, timedelta

from itglue.api.users import UsersAPI
from itglue.models.user import User, UserCollection, UserRole
from itglue.exceptions import ITGlueAPIError


class TestUsersAPI:
    """Test cases for the UsersAPI class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client for testing."""
        client = Mock()
        client.get = AsyncMock()
        client.post = AsyncMock()
        client.put = AsyncMock()
        client.delete = AsyncMock()
        return client

    @pytest.fixture
    def users_api(self, mock_client):
        """Create a UsersAPI instance with mocked client."""
        return UsersAPI(mock_client)

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "data": {
                "id": "123",
                "type": "users",
                "attributes": {
                    "first-name": "John",
                    "last-name": "Doe",
                    "email": "john.doe@example.com",
                    "role-name": "Admin",
                    "reputation": 5000,
                    "my-glue": True,
                    "invitation-accepted-at": "2023-01-01T00:00:00Z",
                },
            }
        }

    @pytest.fixture
    def sample_users_list_data(self):
        """Sample users list data for testing."""
        return {
            "data": [
                {
                    "id": "1",
                    "type": "users",
                    "attributes": {
                        "first-name": "John",
                        "last-name": "Doe",
                        "email": "john@example.com",
                        "role-name": "Admin",
                        "reputation": 5000,
                    },
                },
                {
                    "id": "2",
                    "type": "users",
                    "attributes": {
                        "first-name": "Jane",
                        "last-name": "Smith",
                        "email": "jane@example.com",
                        "role-name": "Editor",
                        "reputation": 2500,
                    },
                },
            ]
        }

    @pytest.mark.asyncio
    async def test_get_by_email_found(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test getting user by email when user exists."""
        mock_client.get.return_value = sample_users_list_data

        # Mock the list method to return the user
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_user = User.from_api_dict(sample_users_list_data["data"][0])
            mock_list.return_value = [mock_user]

            result = await users_api.get_by_email("john@example.com")

            assert result is not None
            assert result.email == "john@example.com"
            mock_list.assert_called_once_with(
                params={"filter[email]": "john@example.com"}, page_size=1
            )

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, users_api, mock_client):
        """Test getting user by email when user doesn't exist."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_list.return_value = []

            result = await users_api.get_by_email("nonexistent@example.com")

            assert result is None
            mock_list.assert_called_once_with(
                params={"filter[email]": "nonexistent@example.com"}, page_size=1
            )

    @pytest.mark.asyncio
    async def test_get_by_email_error(self, users_api, mock_client):
        """Test error handling in get_by_email."""
        with patch.object(users_api, "list", side_effect=Exception("Network error")):
            with pytest.raises(ITGlueAPIError, match="Failed to get user by email"):
                await users_api.get_by_email("test@example.com")

    @pytest.mark.asyncio
    async def test_search_by_name(self, users_api, mock_client, sample_users_list_data):
        """Test searching users by name."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_users = [
                User.from_api_dict(data) for data in sample_users_list_data["data"]
            ]
            mock_list.return_value = mock_users

            result = await users_api.search_by_name("John")

            assert len(result) == 2
            expected_params = {
                "filter[first-name]": "John",
                "filter[last-name]": "John",
            }
            mock_list.assert_called_once_with(params=expected_params)

    @pytest.mark.asyncio
    async def test_search_by_name_with_collection(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test searching users by name with UserCollection return."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_collection = UserCollection.from_api_dict(sample_users_list_data)
            mock_list.return_value = mock_collection

            result = await users_api.search_by_name("John")

            assert isinstance(result, list)
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_filter_by_role_string(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test filtering users by role using string."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_users = [
                User.from_api_dict(sample_users_list_data["data"][0])
            ]  # Admin user only
            mock_list.return_value = mock_users

            result = await users_api.filter_by_role("Admin")

            assert len(result) == 1
            assert result[0].role_name == "Admin"
            mock_list.assert_called_once_with(params={"filter[role-name]": "Admin"})

    @pytest.mark.asyncio
    async def test_filter_by_role_enum(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test filtering users by role using enum."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_users = [
                User.from_api_dict(sample_users_list_data["data"][1])
            ]  # Editor user only
            mock_list.return_value = mock_users

            result = await users_api.filter_by_role(UserRole.EDITOR)

            assert len(result) == 1
            assert result[0].role_name == "Editor"
            mock_list.assert_called_once_with(params={"filter[role-name]": "Editor"})

    @pytest.mark.asyncio
    async def test_get_active_users(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test getting active users."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_users = [
                User.from_api_dict(data) for data in sample_users_list_data["data"]
            ]
            mock_list.return_value = mock_users

            result = await users_api.get_active_users()

            expected_params = {"filter[invitation-accepted-at]": "!null"}
            mock_list.assert_called_once_with(params=expected_params)

    @pytest.mark.asyncio
    async def test_get_invited_users(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test getting invited users."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_users = [
                User.from_api_dict(data) for data in sample_users_list_data["data"]
            ]
            mock_list.return_value = mock_users

            result = await users_api.get_invited_users()

            expected_params = {
                "filter[invitation-sent-at]": "!null",
                "filter[invitation-accepted-at]": "null",
            }
            mock_list.assert_called_once_with(params=expected_params)

    @pytest.mark.asyncio
    async def test_get_my_glue_users(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test getting MyGlue users."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_users = [
                User.from_api_dict(data) for data in sample_users_list_data["data"]
            ]
            mock_list.return_value = mock_users

            result = await users_api.get_my_glue_users()

            expected_params = {"filter[my-glue]": "true"}
            mock_list.assert_called_once_with(params=expected_params)

    @pytest.mark.asyncio
    async def test_get_recently_active_users(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test getting recently active users."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_users = [
                User.from_api_dict(data) for data in sample_users_list_data["data"]
            ]
            mock_list.return_value = mock_users

            result = await users_api.get_recently_active_users(days=30)

            # Should filter by last-sign-in-at
            mock_list.assert_called_once()
            call_args = mock_list.call_args[1]["params"]
            assert "filter[last-sign-in-at]" in call_args
            assert ">=" in call_args["filter[last-sign-in-at]"]

    @pytest.mark.asyncio
    async def test_get_top_reputation_users(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test getting top reputation users."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_users = [
                User.from_api_dict(data) for data in sample_users_list_data["data"]
            ]
            mock_list.return_value = mock_users

            result = await users_api.get_top_reputation_users(limit=5)

            expected_params = {"sort": "-reputation", "page[size]": "5"}
            mock_list.assert_called_once_with(params=expected_params)

    @pytest.mark.asyncio
    async def test_create_user(self, users_api, mock_client, sample_user_data):
        """Test creating a new user."""
        with patch.object(users_api, "create", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = User.from_api_dict(sample_user_data["data"])

            user_data = {
                "first-name": "New",
                "last-name": "User",
                "email": "new@example.com",
                "role-name": "Editor",
            }

            result = await users_api.create_user(user_data)

            assert isinstance(result, User)
            mock_create.assert_called_once_with(user_data)

    @pytest.mark.asyncio
    async def test_update_user_role(self, users_api, mock_client, sample_user_data):
        """Test updating user role."""
        with patch.object(users_api, "update", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = User.from_api_dict(sample_user_data["data"])

            result = await users_api.update_user_role("123", UserRole.CREATOR)

            assert isinstance(result, User)
            mock_update.assert_called_once_with("123", {"role-name": "Creator"})

    @pytest.mark.asyncio
    async def test_update_user_profile(self, users_api, mock_client, sample_user_data):
        """Test updating user profile."""
        with patch.object(users_api, "update", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = User.from_api_dict(sample_user_data["data"])

            profile_data = {
                "first-name": "Updated",
                "last-name": "Name",
                "email": "updated@example.com",
            }

            result = await users_api.update_user_profile("123", profile_data)

            assert isinstance(result, User)
            mock_update.assert_called_once_with("123", profile_data)

    @pytest.mark.asyncio
    async def test_resend_invitation(self, users_api, mock_client):
        """Test resending invitation to user."""
        mock_client.post.return_value = {"success": True}

        result = await users_api.resend_invitation("123")

        assert result is True
        mock_client.post.assert_called_once_with("users/123/resend_invitation")

    @pytest.mark.asyncio
    async def test_resend_invitation_error(self, users_api, mock_client):
        """Test error handling in resend_invitation."""
        mock_client.post.side_effect = Exception("Network error")

        with pytest.raises(ITGlueAPIError, match="Failed to resend invitation"):
            await users_api.resend_invitation("123")

    @pytest.mark.asyncio
    async def test_get_user_statistics(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test getting user statistics."""
        with patch.object(users_api, "list", new_callable=AsyncMock) as mock_list:
            mock_collection = UserCollection.from_api_dict(sample_users_list_data)
            mock_list.return_value = mock_collection

            result = await users_api.get_user_statistics()

            assert "total_users" in result
            assert "active_users" in result
            assert "invited_users" in result
            assert "role_distribution" in result
            assert "my_glue_statistics" in result
            assert "top_reputation_users" in result
            assert "average_reputation" in result

            assert result["total_users"] == 2
            assert isinstance(result["role_distribution"], dict)
            assert isinstance(result["my_glue_statistics"], dict)
            assert isinstance(result["top_reputation_users"], list)

    @pytest.mark.asyncio
    async def test_search_users_with_email(
        self, users_api, mock_client, sample_user_data
    ):
        """Test searching users with email query."""
        with patch.object(
            users_api, "get_by_email", new_callable=AsyncMock
        ) as mock_get_by_email:
            with patch.object(
                users_api, "search_by_name", new_callable=AsyncMock
            ) as mock_search_by_name:
                mock_user = User.from_api_dict(sample_user_data["data"])
                mock_get_by_email.return_value = mock_user
                mock_search_by_name.return_value = []

                result = await users_api.search_users("john@example.com")

                assert len(result) == 1
                assert result[0].email == "john.doe@example.com"
                mock_get_by_email.assert_called_once_with("john@example.com")
                mock_search_by_name.assert_called_once_with("john@example.com")

    @pytest.mark.asyncio
    async def test_search_users_without_email(
        self, users_api, mock_client, sample_users_list_data
    ):
        """Test searching users without email query."""
        with patch.object(
            users_api, "get_by_email", new_callable=AsyncMock
        ) as mock_get_by_email:
            with patch.object(
                users_api, "search_by_name", new_callable=AsyncMock
            ) as mock_search_by_name:
                mock_users = [
                    User.from_api_dict(data) for data in sample_users_list_data["data"]
                ]
                mock_search_by_name.return_value = mock_users

                result = await users_api.search_users("John")

                assert len(result) == 2
                mock_get_by_email.assert_not_called()  # No @ in query
                mock_search_by_name.assert_called_once_with("John")

    @pytest.mark.asyncio
    async def test_search_users_duplicate_removal(
        self, users_api, mock_client, sample_user_data
    ):
        """Test duplicate removal in search results."""
        with patch.object(
            users_api, "get_by_email", new_callable=AsyncMock
        ) as mock_get_by_email:
            with patch.object(
                users_api, "search_by_name", new_callable=AsyncMock
            ) as mock_search_by_name:
                mock_user = User.from_api_dict(sample_user_data["data"])
                mock_get_by_email.return_value = mock_user
                mock_search_by_name.return_value = [mock_user]  # Same user returned

                result = await users_api.search_users("john@example.com")

                assert len(result) == 1  # Duplicate removed
                assert result[0].id == "123"

    @pytest.mark.asyncio
    async def test_get_admin_users(self, users_api, mock_client):
        """Test getting admin users."""
        with patch.object(
            users_api, "filter_by_role", new_callable=AsyncMock
        ) as mock_filter:
            mock_filter.return_value = []

            await users_api.get_admin_users()

            mock_filter.assert_called_once_with(UserRole.ADMIN)

    @pytest.mark.asyncio
    async def test_get_creator_users(self, users_api, mock_client):
        """Test getting creator users."""
        with patch.object(
            users_api, "filter_by_role", new_callable=AsyncMock
        ) as mock_filter:
            mock_filter.return_value = []

            await users_api.get_creator_users()

            mock_filter.assert_called_once_with(UserRole.CREATOR)

    @pytest.mark.asyncio
    async def test_get_editor_users(self, users_api, mock_client):
        """Test getting editor users."""
        with patch.object(
            users_api, "filter_by_role", new_callable=AsyncMock
        ) as mock_filter:
            mock_filter.return_value = []

            await users_api.get_editor_users()

            mock_filter.assert_called_once_with(UserRole.EDITOR)

    @pytest.mark.asyncio
    async def test_get_lite_users(self, users_api, mock_client):
        """Test getting lite users."""
        with patch.object(
            users_api, "filter_by_role", new_callable=AsyncMock
        ) as mock_filter:
            mock_filter.return_value = []

            await users_api.get_lite_users()

            mock_filter.assert_called_once_with(UserRole.LITE)

    @pytest.mark.asyncio
    async def test_get_viewer_users(self, users_api, mock_client):
        """Test getting viewer users."""
        with patch.object(
            users_api, "filter_by_role", new_callable=AsyncMock
        ) as mock_filter:
            mock_filter.return_value = []

            await users_api.get_viewer_users()

            mock_filter.assert_called_once_with(UserRole.VIEWER)

    @pytest.mark.asyncio
    async def test_api_initialization(self, mock_client):
        """Test API initialization with correct parameters."""
        api = UsersAPI(mock_client)

        assert api.endpoint_path == "users"
        assert api.client == mock_client
