"""Tests for the Configurations API resource class."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import Dict, Any

from itglue.api.configurations import ConfigurationsAPI
from itglue.models.configuration import Configuration, ConfigurationStatus
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
def configurations_api(mock_http_client):
    """Configurations API instance."""
    return ConfigurationsAPI(mock_http_client)


@pytest.fixture
def sample_configuration_data():
    """Sample configuration data for testing."""
    return {
        "type": "configurations",
        "id": "123",
        "attributes": {
            "name": "Test Server",
            "hostname": "server.example.com",
            "primary-ip": "192.168.1.100",
            "operating-system-notes": "Ubuntu 20.04",
            "contact-name": "John Doe",
            "configuration-status-name": "Active",
            "notes": "Test notes",
            "created-at": "2023-01-01T00:00:00Z",
            "updated-at": "2023-01-01T00:00:00Z",
        },
        "relationships": {
            "organization": {"data": {"type": "organizations", "id": "456"}}
        },
    }


class TestConfigurationsAPIInitialization:
    """Test ConfigurationsAPI initialization."""

    def test_init_with_valid_params(self, mock_http_client):
        """Test successful initialization."""
        api = ConfigurationsAPI(mock_http_client)

        assert api.client == mock_http_client
        assert api.resource_type == ResourceType.CONFIGURATIONS
        assert api.model_class == Configuration
        assert api.endpoint_path == "configurations"
        assert api.base_url == "/configurations"


@pytest.mark.asyncio
class TestConfigurationsAPISpecializedMethods:
    """Test specialized methods for configurations."""

    async def test_get_by_organization(self, configurations_api, mock_http_client):
        """Test getting configurations by organization ID."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            result = await configurations_api.list_by_organization("456")

            assert result == mock_collection
            expected_params = {"filter[organization-id]": "456"}
            mock_http_client.get.assert_called_once_with(
                "/configurations", params=expected_params
            )

    async def test_search_by_hostname(self, configurations_api, mock_http_client):
        """Test searching configurations by hostname."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            result = await configurations_api.search_by_hostname("server.example.com")

            assert result == mock_collection
            expected_params = {"filter[hostname]": "server.example.com"}
            mock_http_client.get.assert_called_once_with(
                "/configurations", params=expected_params
            )

    async def test_search_by_ip(self, configurations_api, mock_http_client):
        """Test searching configurations by IP address."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            result = await configurations_api.search_by_ip_address("192.168.1.100")

            assert result == mock_collection
            expected_params = {"filter[primary-ip]": "192.168.1.100"}
            mock_http_client.get.assert_called_once_with(
                "/configurations", params=expected_params
            )

    async def test_list_by_status(self, configurations_api, mock_http_client):
        """Test listing configurations by status."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            result = await configurations_api.list_by_status(ConfigurationStatus.ACTIVE)

            assert result == mock_collection
            expected_params = {"filter[configuration-status-name]": "Active"}
            mock_http_client.get.assert_called_once_with(
                "/configurations", params=expected_params
            )

    async def test_list_by_status_string(self, configurations_api, mock_http_client):
        """Test listing configurations by status using string."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            result = await configurations_api.list_by_status("Active")

            assert result == mock_collection
            expected_params = {"filter[configuration-status-name]": "Active"}
            mock_http_client.get.assert_called_once_with(
                "/configurations", params=expected_params
            )

    async def test_list_by_type(self, configurations_api, mock_http_client):
        """Test listing configurations by type."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            result = await configurations_api.list_by_type("123")

            assert result == mock_collection
            expected_params = {"filter[configuration-type-id]": "123"}
            mock_http_client.get.assert_called_once_with(
                "/configurations", params=expected_params
            )

    async def test_get_organization_servers(self, configurations_api, mock_http_client):
        """Test getting server configurations for an organization using list with filters."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            # Use list method with multiple filters instead of a specialized method
            result = await configurations_api.list(
                filter_params={"organization-id": "456", "configuration-type-id": "789"}
            )

            assert result == mock_collection
            expected_params = {
                "filter[organization-id]": "456",
                "filter[configuration-type-id]": "789",
            }
            mock_http_client.get.assert_called_once_with(
                "/configurations", params=expected_params
            )

    async def test_update_status_with_enum(
        self, configurations_api, mock_http_client, sample_configuration_data
    ):
        """Test updating configuration status with enum."""
        response_data = {"data": sample_configuration_data}
        mock_http_client.patch = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_config = Configuration.from_api_dict(sample_configuration_data)
            mock_process.return_value = mock_config

            result = await configurations_api.update_status(
                "123", ConfigurationStatus.INACTIVE
            )

            assert result == mock_config
            mock_http_client.patch.assert_called_once()

    async def test_update_status_invalid(self, configurations_api):
        """Test updating configuration status with invalid value."""
        with pytest.raises(ITGlueValidationError, match="Invalid configuration status"):
            await configurations_api.update_status("123", "InvalidStatus")

    async def test_create_configuration_basic(
        self, configurations_api, mock_http_client, sample_configuration_data
    ):
        """Test creating a basic configuration."""
        response_data = {"data": sample_configuration_data}
        mock_http_client.post = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_config = Configuration.from_api_dict(sample_configuration_data)
            mock_process.return_value = mock_config

            result = await configurations_api.create_configuration(
                organization_id="456", name="Test Server", configuration_type_id="789"
            )

            assert result == mock_config
            mock_http_client.post.assert_called_once()

    async def test_create_configuration_full(
        self, configurations_api, mock_http_client, sample_configuration_data
    ):
        """Test creating a configuration with all fields."""
        response_data = {"data": sample_configuration_data}
        mock_http_client.post = AsyncMock(return_value=response_data)

        with patch.object(configurations_api, "_process_response") as mock_process:
            mock_config = Configuration.from_api_dict(sample_configuration_data)
            mock_process.return_value = mock_config

            result = await configurations_api.create_configuration(
                organization_id="456",
                name="Test Server",
                configuration_type_id="789",
                hostname="server.example.com",
                primary_ip="192.168.1.100",
                operating_system_notes="Ubuntu 20.04",
                notes="Test configuration",
            )

            assert result == mock_config
            mock_http_client.post.assert_called_once()
