"""Tests for the Organizations API resource class."""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from itglue.api.organizations import OrganizationsAPI
from itglue.models.organization import (
    Organization,
    OrganizationStatus,
    OrganizationTypeEnum,
)
from itglue.models.base import ITGlueResourceCollection, ResourceType
from itglue.http_client import ITGlueHTTPClient
from itglue.exceptions import ITGlueValidationError
from itglue.config import ITGlueConfig


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    config = ITGlueConfig(api_key="test-key")
    client = Mock(spec=ITGlueHTTPClient)
    client.config = config
    return client


@pytest.fixture
def organizations_api(mock_http_client):
    """Organizations API instance."""
    return OrganizationsAPI(mock_http_client)


@pytest.fixture
def sample_organization_data():
    """Sample organization data for testing."""
    return {
        "type": "organizations",
        "id": "123",
        "attributes": {
            "name": "Test Organization",
            "description": "A test organization",
            "organization-type-name": "Client",
            "organization-status-name": "Active",
            "primary-domain": "example.com",
            "quick-notes": "Test notes",
            "created-at": "2023-01-01T00:00:00Z",
            "updated-at": "2023-01-01T00:00:00Z",
        },
    }


class TestOrganizationsAPIInitialization:
    """Test OrganizationsAPI initialization."""

    def test_init_with_valid_params(self, mock_http_client):
        """Test successful initialization."""
        api = OrganizationsAPI(mock_http_client)

        assert api.client == mock_http_client
        assert api.resource_type == ResourceType.ORGANIZATIONS
        assert api.model_class == Organization
        assert api.endpoint_path == "organizations"
        assert api.base_url == "/organizations"


class TestOrganizationsAPISpecializedMethods:
    """Test specialized methods for organizations."""

    def test_get_by_name_exact_match(
        self, organizations_api, mock_http_client, sample_organization_data
    ):
        """Test getting organization by exact name."""
        response_data = {"data": [sample_organization_data], "meta": {}}
        mock_http_client.get = Mock(return_value=response_data)

        with patch.object(organizations_api, "_process_response") as mock_process:
            mock_org = Organization.from_api_dict(sample_organization_data)
            mock_collection = ITGlueResourceCollection(data=[mock_org])
            mock_process.return_value = mock_collection

            result = organizations_api.get_by_name(
                "Test Organization", exact_match=True
            )

            assert result == mock_org
            expected_params = {"filter[name]": "Test Organization", "page[size]": "1"}
            mock_http_client.get.assert_called_once_with(
                "/organizations", params=expected_params
            )

    def test_update_status_with_enum(
        self, organizations_api, mock_http_client, sample_organization_data
    ):
        """Test updating organization status with enum."""
        response_data = {"data": sample_organization_data}
        mock_http_client.patch = Mock(return_value=response_data)

        with patch.object(organizations_api, "_process_response") as mock_process:
            mock_org = Organization.from_api_dict(sample_organization_data)
            mock_process.return_value = mock_org

            result = organizations_api.update_status(
                "123", OrganizationStatus.INACTIVE
            )

            assert result == mock_org
            mock_http_client.patch.assert_called_once()

    def test_update_status_invalid(self, organizations_api):
        """Test updating organization status with invalid value."""
        with pytest.raises(ITGlueValidationError, match="Invalid organization status"):
            organizations_api.update_status("123", "InvalidStatus")

    def test_create_organization_with_enum(
        self, organizations_api, mock_http_client, sample_organization_data
    ):
        """Test creating organization with enum type."""
        response_data = {"data": sample_organization_data}
        mock_http_client.post = Mock(return_value=response_data)

        with patch.object(organizations_api, "_process_response") as mock_process:
            mock_org = Organization.from_api_dict(sample_organization_data)
            mock_process.return_value = mock_org

            result = organizations_api.create_organization(
                name="Test Organization",
                organization_type=OrganizationTypeEnum.CLIENT,
                description="Test description",
            )

            assert result == mock_org
            mock_http_client.post.assert_called_once()

    def test_create_organization_invalid_type(self, organizations_api):
        """Test creating organization with invalid type."""
        with pytest.raises(ITGlueValidationError, match="Invalid organization type"):
            organizations_api.create_organization(
                name="Test Organization", organization_type="InvalidType"
            )
