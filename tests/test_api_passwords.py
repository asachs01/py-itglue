"""
Tests for PasswordsAPI.

This module tests all password management operations including CRUD, security filtering,
sharing controls, time-based operations, and analytics.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone, timedelta

from itglue.api.passwords import PasswordsAPI
from itglue.models.password import (
    Password,
    PasswordCollection,
    PasswordType,
    PasswordCategory,
    PasswordVisibility,
)
from itglue.models.base import ResourceType


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client."""
    return Mock()


@pytest.fixture
def passwords_api(mock_http_client):
    """Create PasswordsAPI instance with mock HTTP client."""
    return PasswordsAPI(mock_http_client)


@pytest.fixture
def sample_password_data():
    """Sample password data for testing."""
    return {
        "id": "123",
        "type": "passwords",
        "attributes": {
            "name": "Gmail Account",
            "username": "user@example.com",
            "password": "secure123",
            "url": "https://gmail.com",
            "notes": "Primary email account",
            "password-type": "embedded",
            "password-category-name": "high",
            "visibility": "private",
            "favorite": True,
            "archived": False,
            "created-at": "2023-01-01T00:00:00Z",
            "updated-at": "2023-01-02T00:00:00Z",
            "password-updated-at": "2023-01-03T00:00:00Z",
        },
        "relationships": {
            "organization": {"data": {"type": "organizations", "id": "456"}}
        },
    }


@pytest.fixture
def sample_password_collection_data():
    """Sample password collection data for testing."""
    return {
        "data": [
            {
                "id": "1",
                "type": "passwords",
                "attributes": {
                    "name": "Gmail",
                    "username": "user1@example.com",
                    "password": "pass123",
                    "password-type": "embedded",
                    "password-category-name": "high",
                    "visibility": "private",
                    "favorite": True,
                    "archived": False,
                },
            },
            {
                "id": "2",
                "type": "passwords",
                "attributes": {
                    "name": "Office 365",
                    "username": "user2@company.com",
                    "password": "pass456",
                    "password-type": "linked",
                    "password-category-name": "critical",
                    "visibility": "organization",
                    "favorite": False,
                    "archived": False,
                },
            },
        ]
    }


class TestPasswordsAPIInitialization:
    """Test PasswordsAPI initialization."""

    def test_api_initialization(self, mock_http_client):
        """Test PasswordsAPI initialization."""
        api = PasswordsAPI(mock_http_client)

        assert api.client == mock_http_client
        assert api.resource_type == ResourceType.PASSWORDS
        assert api.model_class == Password
        assert api.endpoint_path == "passwords"


class TestPasswordsAPISearch:
    """Test search and filtering operations."""

    @pytest.mark.asyncio
    async def test_search_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test searching passwords by query."""
        passwords_api.list = AsyncMock(
            return_value=[
                Password.from_api_dict(sample_password_collection_data["data"][0])
            ]
        )

        results = await passwords_api.search_passwords("Gmail", organization_id="456")

        passwords_api.list.assert_called_once_with(
            params={"filter[name]": "Gmail", "filter[organization-id]": "456"}
        )
        assert len(results) == 1
        assert results[0].name == "Gmail"

    @pytest.mark.asyncio
    async def test_get_by_name_exact_match(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting password by exact name match."""
        password_data = sample_password_collection_data["data"][0]
        passwords_api.list = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        result = await passwords_api.get_by_name("Gmail", organization_id="456")

        passwords_api.list.assert_called_once_with(
            params={"filter[name]": "Gmail", "filter[organization-id]": "456"}
        )
        assert result is not None
        assert result.name == "Gmail"

    @pytest.mark.asyncio
    async def test_get_by_name_case_insensitive(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting password by name with case insensitive matching."""
        password_data = sample_password_collection_data["data"][0]
        passwords_api.list = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        result = await passwords_api.get_by_name("gmail")  # lowercase

        assert result is not None
        assert result.name == "Gmail"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, passwords_api):
        """Test getting password by name when not found."""
        passwords_api.list = AsyncMock(return_value=[])

        result = await passwords_api.get_by_name("NonExistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_search_by_username(
        self, passwords_api, sample_password_collection_data
    ):
        """Test searching passwords by username."""
        password_data = sample_password_collection_data["data"][0]
        passwords_api.list = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        results = await passwords_api.search_by_username(
            "user1@example.com", organization_id="456"
        )

        passwords_api.list.assert_called_once_with(
            params={
                "filter[username]": "user1@example.com",
                "filter[organization-id]": "456",
            }
        )
        assert len(results) == 1
        assert results[0].username == "user1@example.com"

    @pytest.mark.asyncio
    async def test_search_by_url(self, passwords_api, sample_password_collection_data):
        """Test searching passwords by URL."""
        password_data = sample_password_collection_data["data"][0]
        password_data["attributes"]["url"] = "https://gmail.com"
        passwords_api.list = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        results = await passwords_api.search_by_url("gmail.com", organization_id="456")

        passwords_api.list.assert_called_once_with(
            params={"filter[url]": "gmail.com", "filter[organization-id]": "456"}
        )
        assert len(results) == 1


class TestPasswordsAPIOrganizationFiltering:
    """Test organization-based filtering."""

    @pytest.mark.asyncio
    async def test_get_organization_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting passwords for an organization."""
        passwords_api.list = AsyncMock(
            return_value=[
                Password.from_api_dict(data)
                for data in sample_password_collection_data["data"]
            ]
        )

        results = await passwords_api.get_organization_passwords(
            "456", include_archived=False
        )

        passwords_api.list.assert_called_once_with(
            params={"filter[organization-id]": "456", "filter[archived]": "false"}
        )
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_get_organization_passwords_include_archived(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting organization passwords including archived."""
        passwords_api.list = AsyncMock(
            return_value=[
                Password.from_api_dict(data)
                for data in sample_password_collection_data["data"]
            ]
        )

        results = await passwords_api.get_organization_passwords(
            "456", include_archived=True
        )

        passwords_api.list.assert_called_once_with(
            params={"filter[organization-id]": "456"}
        )
        assert len(results) == 2


class TestPasswordsAPISecurityFiltering:
    """Test security and visibility filtering."""

    @pytest.mark.asyncio
    async def test_filter_by_category_enum(
        self, passwords_api, sample_password_collection_data
    ):
        """Test filtering by password category using enum."""
        password_data = sample_password_collection_data["data"][1]  # critical password
        passwords_api.list = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        results = await passwords_api.filter_by_category(
            PasswordCategory.CRITICAL, organization_id="456"
        )

        passwords_api.list.assert_called_once_with(
            params={
                "filter[password-category-name]": "critical",
                "filter[organization-id]": "456",
            }
        )
        assert len(results) == 1
        assert results[0].password_category == PasswordCategory.CRITICAL

    @pytest.mark.asyncio
    async def test_filter_by_category_string(
        self, passwords_api, sample_password_collection_data
    ):
        """Test filtering by password category using string."""
        password_data = sample_password_collection_data["data"][0]  # high password
        passwords_api.list = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        results = await passwords_api.filter_by_category("high")

        passwords_api.list.assert_called_once_with(
            params={"filter[password-category-name]": "high"}
        )
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_filter_by_visibility_enum(
        self, passwords_api, sample_password_collection_data
    ):
        """Test filtering by visibility using enum."""
        password_data = sample_password_collection_data["data"][0]  # private password
        passwords_api.list = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        results = await passwords_api.filter_by_visibility(
            PasswordVisibility.PRIVATE, organization_id="456"
        )

        passwords_api.list.assert_called_once_with(
            params={"filter[visibility]": "private", "filter[organization-id]": "456"}
        )
        assert len(results) == 1
        assert results[0].visibility == PasswordVisibility.PRIVATE

    @pytest.mark.asyncio
    async def test_filter_by_type_enum(
        self, passwords_api, sample_password_collection_data
    ):
        """Test filtering by password type using enum."""
        password_data = sample_password_collection_data["data"][0]  # embedded password
        passwords_api.list = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        results = await passwords_api.filter_by_type(PasswordType.EMBEDDED)

        passwords_api.list.assert_called_once_with(
            params={"filter[password-type]": "embedded"}
        )
        assert len(results) == 1
        assert results[0].password_type == PasswordType.EMBEDDED


class TestPasswordsAPISecurityMethods:
    """Test security-focused methods."""

    @pytest.mark.asyncio
    async def test_get_critical_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting critical passwords."""
        password_data = sample_password_collection_data["data"][1]  # critical password
        passwords_api.filter_by_category = AsyncMock(
            return_value=[Password.from_api_dict(password_data)]
        )

        results = await passwords_api.get_critical_passwords(organization_id="456")

        passwords_api.filter_by_category.assert_called_once_with(
            PasswordCategory.CRITICAL, "456"
        )
        assert len(results) == 1
        assert results[0].password_category == PasswordCategory.CRITICAL

    @pytest.mark.asyncio
    async def test_get_high_security_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting high security passwords."""
        high_password = Password.from_api_dict(
            sample_password_collection_data["data"][0]
        )
        critical_password = Password.from_api_dict(
            sample_password_collection_data["data"][1]
        )

        passwords_api.filter_by_category = AsyncMock(
            side_effect=[
                [high_password],  # high category call
                [critical_password],  # critical category call
            ]
        )

        results = await passwords_api.get_high_security_passwords(organization_id="456")

        assert passwords_api.filter_by_category.call_count == 2
        assert len(results) == 2  # Should include both high and critical

    @pytest.mark.asyncio
    async def test_get_high_security_passwords_deduplication(
        self, passwords_api, sample_password_collection_data
    ):
        """Test deduplication in high security passwords."""
        # Same password returned from both calls (shouldn't happen in practice, but test deduplication)
        same_password = Password.from_api_dict(
            sample_password_collection_data["data"][0]
        )

        passwords_api.filter_by_category = AsyncMock(
            side_effect=[
                [same_password],  # high category call
                [same_password],  # critical category call (same password)
            ]
        )

        results = await passwords_api.get_high_security_passwords()

        assert len(results) == 1  # Should be deduplicated

    @pytest.mark.asyncio
    async def test_get_shared_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting shared passwords."""
        shared_password = Password.from_api_dict(
            sample_password_collection_data["data"][1]
        )  # organization visibility

        passwords_api.filter_by_visibility = AsyncMock(
            side_effect=[
                [],  # shared visibility
                [shared_password],  # organization visibility
                [],  # everyone visibility
            ]
        )

        results = await passwords_api.get_shared_passwords(organization_id="456")

        assert passwords_api.filter_by_visibility.call_count == 3
        assert len(results) == 1
        assert results[0].visibility == PasswordVisibility.ORGANIZATION

    @pytest.mark.asyncio
    async def test_get_private_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting private passwords."""
        private_password = Password.from_api_dict(
            sample_password_collection_data["data"][0]
        )
        passwords_api.filter_by_visibility = AsyncMock(return_value=[private_password])

        results = await passwords_api.get_private_passwords(organization_id="456")

        passwords_api.filter_by_visibility.assert_called_once_with(
            PasswordVisibility.PRIVATE, "456"
        )
        assert len(results) == 1
        assert results[0].visibility == PasswordVisibility.PRIVATE

    @pytest.mark.asyncio
    async def test_get_embedded_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting embedded passwords."""
        embedded_password = Password.from_api_dict(
            sample_password_collection_data["data"][0]
        )
        passwords_api.filter_by_type = AsyncMock(return_value=[embedded_password])

        results = await passwords_api.get_embedded_passwords(organization_id="456")

        passwords_api.filter_by_type.assert_called_once_with(
            PasswordType.EMBEDDED, "456"
        )
        assert len(results) == 1
        assert results[0].password_type == PasswordType.EMBEDDED

    @pytest.mark.asyncio
    async def test_get_linked_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting linked passwords."""
        linked_password = Password.from_api_dict(
            sample_password_collection_data["data"][1]
        )
        passwords_api.filter_by_type = AsyncMock(return_value=[linked_password])

        results = await passwords_api.get_linked_passwords(organization_id="456")

        passwords_api.filter_by_type.assert_called_once_with(PasswordType.LINKED, "456")
        assert len(results) == 1
        assert results[0].password_type == PasswordType.LINKED


class TestPasswordsAPISpecialStates:
    """Test special state filtering methods."""

    @pytest.mark.asyncio
    async def test_get_favorite_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting favorite passwords."""
        favorite_password = Password.from_api_dict(
            sample_password_collection_data["data"][0]
        )
        passwords_api.list = AsyncMock(return_value=[favorite_password])

        results = await passwords_api.get_favorite_passwords(organization_id="456")

        passwords_api.list.assert_called_once_with(
            params={"filter[favorite]": "true", "filter[organization-id]": "456"}
        )
        assert len(results) == 1
        assert results[0].favorite is True

    @pytest.mark.asyncio
    async def test_get_archived_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting archived passwords."""
        archived_data = sample_password_collection_data["data"][0].copy()
        archived_data["attributes"]["archived"] = True
        archived_password = Password.from_api_dict(archived_data)
        passwords_api.list = AsyncMock(return_value=[archived_password])

        results = await passwords_api.get_archived_passwords(organization_id="456")

        passwords_api.list.assert_called_once_with(
            params={"filter[archived]": "true", "filter[organization-id]": "456"}
        )
        assert len(results) == 1
        assert results[0].archived is True

    @pytest.mark.asyncio
    async def test_get_active_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting active passwords."""
        active_password = Password.from_api_dict(
            sample_password_collection_data["data"][0]
        )
        passwords_api.list = AsyncMock(return_value=[active_password])

        results = await passwords_api.get_active_passwords(organization_id="456")

        passwords_api.list.assert_called_once_with(
            params={"filter[archived]": "false", "filter[organization-id]": "456"}
        )
        assert len(results) == 1
        assert results[0].archived is False


class TestPasswordsAPITimeFiltering:
    """Test time-based filtering methods."""

    @pytest.mark.asyncio
    async def test_get_recently_updated_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting recently updated passwords."""
        recent_password = Password.from_api_dict(
            sample_password_collection_data["data"][0]
        )
        passwords_api.list = AsyncMock(return_value=[recent_password])

        results = await passwords_api.get_recently_updated_passwords(
            30, organization_id="456"
        )

        # Check that the filter was called with the right parameters
        call_args = passwords_api.list.call_args.kwargs["params"]
        assert "filter[updated-at][gt]" in call_args
        assert "filter[organization-id]" in call_args
        assert call_args["filter[organization-id]"] == "456"
        # Verify that the date filter contains an ISO date string
        assert "T" in call_args["filter[updated-at][gt]"]  # ISO format check

    @pytest.mark.asyncio
    async def test_get_stale_passwords(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting stale passwords."""
        stale_password = Password.from_api_dict(
            sample_password_collection_data["data"][0]
        )
        passwords_api.list = AsyncMock(return_value=[stale_password])

        results = await passwords_api.get_stale_passwords(90, organization_id="456")

        # Check that the filter was called with the right parameters
        call_args = passwords_api.list.call_args.kwargs["params"]
        assert "filter[password-updated-at][lt]" in call_args
        assert "filter[organization-id]" in call_args
        assert call_args["filter[organization-id]"] == "456"
        # Verify that the date filter contains an ISO date string
        assert "T" in call_args["filter[password-updated-at][lt]"]  # ISO format check


class TestPasswordsAPIManagement:
    """Test password management operations."""

    @pytest.mark.asyncio
    async def test_create_password(self, passwords_api, sample_password_data):
        """Test creating a new password."""
        passwords_api.create = AsyncMock(
            return_value=Password.from_api_dict(sample_password_data)
        )

        result = await passwords_api.create_password(
            name="Gmail Account",
            username="user@example.com",
            password="secure123",
            organization_id="456",
            url="https://gmail.com",
            notes="Primary email account",
            password_type=PasswordType.EMBEDDED,
            password_category=PasswordCategory.HIGH,
            visibility=PasswordVisibility.PRIVATE,
            favorite=True,
        )

        # Verify the create call
        call_args = passwords_api.create.call_args[0][0]
        assert call_args["type"] == ResourceType.PASSWORDS.value
        assert call_args["attributes"]["name"] == "Gmail Account"
        assert call_args["attributes"]["username"] == "user@example.com"
        assert call_args["attributes"]["password"] == "secure123"
        assert call_args["attributes"]["url"] == "https://gmail.com"
        assert call_args["attributes"]["notes"] == "Primary email account"
        assert call_args["attributes"]["password-type"] == "embedded"
        assert call_args["attributes"]["password-category-name"] == "high"
        assert call_args["attributes"]["visibility"] == "private"
        assert call_args["attributes"]["favorite"] is True

        # Verify organization relationship
        org_rel = call_args["relationships"]["organization"]["data"]
        assert org_rel["type"] == ResourceType.ORGANIZATIONS.value
        assert org_rel["id"] == "456"

        assert result.name == "Gmail Account"

    @pytest.mark.asyncio
    async def test_create_password_with_string_enums(
        self, passwords_api, sample_password_data
    ):
        """Test creating password with string enum values."""
        passwords_api.create = AsyncMock(
            return_value=Password.from_api_dict(sample_password_data)
        )

        result = await passwords_api.create_password(
            name="Test Password",
            username="test@example.com",
            password="test123",
            organization_id="456",
            password_type="linked",
            password_category="critical",
            visibility="everyone",
        )

        call_args = passwords_api.create.call_args[0][0]
        assert call_args["attributes"]["password-type"] == "linked"
        assert call_args["attributes"]["password-category-name"] == "critical"
        assert call_args["attributes"]["visibility"] == "everyone"

    @pytest.mark.asyncio
    async def test_update_password_value(self, passwords_api, sample_password_data):
        """Test updating password value."""
        passwords_api.update = AsyncMock(
            return_value=Password.from_api_dict(sample_password_data)
        )

        result = await passwords_api.update_password_value("123", "newpassword")

        call_args = passwords_api.update.call_args
        assert call_args[0][0] == "123"  # password_id

        update_data = call_args[0][1]
        assert update_data["type"] == ResourceType.PASSWORDS.value
        assert update_data["attributes"]["password"] == "newpassword"

    @pytest.mark.asyncio
    async def test_update_password_visibility(
        self, passwords_api, sample_password_data
    ):
        """Test updating password visibility."""
        passwords_api.update = AsyncMock(
            return_value=Password.from_api_dict(sample_password_data)
        )

        result = await passwords_api.update_password_visibility(
            "123", PasswordVisibility.EVERYONE
        )

        call_args = passwords_api.update.call_args
        assert call_args[0][0] == "123"

        update_data = call_args[0][1]
        assert update_data["attributes"]["visibility"] == "everyone"

    @pytest.mark.asyncio
    async def test_update_password_category(self, passwords_api, sample_password_data):
        """Test updating password security category."""
        passwords_api.update = AsyncMock(
            return_value=Password.from_api_dict(sample_password_data)
        )

        result = await passwords_api.update_password_category("123", "critical")

        call_args = passwords_api.update.call_args
        assert call_args[0][0] == "123"

        update_data = call_args[0][1]
        assert update_data["attributes"]["password-category-name"] == "critical"

    @pytest.mark.asyncio
    async def test_toggle_favorite(self, passwords_api, sample_password_data):
        """Test toggling password favorite status."""
        # Mock current password state
        current_password = Password.from_api_dict(sample_password_data)
        current_password.favorite = True

        updated_data = sample_password_data.copy()
        updated_data["attributes"]["favorite"] = False
        updated_password = Password.from_api_dict(updated_data)

        passwords_api.get = AsyncMock(return_value=current_password)
        passwords_api.update = AsyncMock(return_value=updated_password)

        result = await passwords_api.toggle_favorite("123")

        # Should have called get to check current state
        passwords_api.get.assert_called_once_with("123")

        # Should have called update with toggled value
        call_args = passwords_api.update.call_args
        update_data = call_args[0][1]
        assert update_data["attributes"]["favorite"] is False  # Toggled from True

    @pytest.mark.asyncio
    async def test_archive_password(self, passwords_api, sample_password_data):
        """Test archiving a password."""
        passwords_api.update = AsyncMock(
            return_value=Password.from_api_dict(sample_password_data)
        )

        result = await passwords_api.archive_password("123")

        call_args = passwords_api.update.call_args
        update_data = call_args[0][1]
        assert update_data["attributes"]["archived"] is True

    @pytest.mark.asyncio
    async def test_unarchive_password(self, passwords_api, sample_password_data):
        """Test unarchiving a password."""
        passwords_api.update = AsyncMock(
            return_value=Password.from_api_dict(sample_password_data)
        )

        result = await passwords_api.unarchive_password("123")

        call_args = passwords_api.update.call_args
        update_data = call_args[0][1]
        assert update_data["attributes"]["archived"] is False


class TestPasswordsAPIAnalytics:
    """Test analytics and reporting methods."""

    @pytest.mark.asyncio
    async def test_get_password_statistics_empty(self, passwords_api):
        """Test getting statistics for empty password collection."""
        passwords_api.get_active_passwords = AsyncMock(return_value=[])

        stats = await passwords_api.get_password_statistics(organization_id="456")

        assert stats["total_passwords"] == 0
        assert stats["active_passwords"] == 0
        assert stats["archived_passwords"] == 0
        assert stats["critical_passwords"] == 0

    @pytest.mark.asyncio
    async def test_get_password_statistics(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting comprehensive password statistics."""
        active_passwords = [
            Password.from_api_dict(data)
            for data in sample_password_collection_data["data"]
        ]
        archived_passwords = []

        passwords_api.get_active_passwords = AsyncMock(return_value=active_passwords)
        passwords_api.get_archived_passwords = AsyncMock(
            return_value=archived_passwords
        )

        stats = await passwords_api.get_password_statistics(organization_id="456")

        assert stats["total_passwords"] == 2  # active + archived
        assert stats["active_passwords"] == 2
        assert stats["archived_passwords"] == 0
        assert stats["favorite_passwords"] == 1  # Gmail is favorite
        assert stats["critical_passwords"] == 1  # Office 365 is critical
        assert stats["high_security_passwords"] == 2  # both high and critical
        assert stats["shared_passwords"] == 1  # Office 365 is organization visible
        assert stats["private_passwords"] == 1  # Gmail is private
        assert stats["linked_passwords"] == 1  # Office 365 is linked
        assert stats["embedded_passwords"] == 1  # Gmail is embedded

        # Check distributions are included
        assert "security_distribution" in stats
        assert "visibility_distribution" in stats
        assert "type_distribution" in stats

    @pytest.mark.asyncio
    async def test_get_organization_password_report(
        self, passwords_api, sample_password_collection_data
    ):
        """Test getting comprehensive organization password report."""
        active_passwords = [
            Password.from_api_dict(data)
            for data in sample_password_collection_data["data"]
        ]

        # Mock all the required method calls
        passwords_api.get_password_statistics = AsyncMock(
            return_value={
                "total_passwords": 2,
                "active_passwords": 2,
                "critical_passwords": 1,
                "shared_passwords": 1,
                "private_passwords": 1,
                "security_distribution": {
                    "low": 0,
                    "medium": 0,
                    "high": 1,
                    "critical": 1,
                },
            }
        )
        passwords_api.get_stale_passwords = AsyncMock(return_value=[])
        passwords_api.get_recently_updated_passwords = AsyncMock(
            return_value=active_passwords
        )

        report = await passwords_api.get_organization_password_report("456")

        # Verify method calls
        passwords_api.get_password_statistics.assert_called_once_with("456")
        passwords_api.get_stale_passwords.assert_called_once_with(90, "456")
        passwords_api.get_recently_updated_passwords.assert_called_once_with(30, "456")

        # Check report contents
        assert report["total_passwords"] == 2
        assert report["stale_passwords_90d"] == 0
        assert report["recently_updated_30d"] == 2

        # Check security recommendations
        recommendations = report["security_recommendations"]
        assert (
            recommendations["critical_review_needed"] is True
        )  # Has critical passwords
        assert (
            recommendations["stale_passwords_need_update"] is False
        )  # No stale passwords
        assert (
            recommendations["consider_upgrading_low_security"] is False
        )  # No low security passwords
        assert (
            recommendations["review_shared_passwords"] is False
        )  # More private than shared
