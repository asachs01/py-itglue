"""
Tests for Flexible Assets API classes.

Tests the FlexibleAssetsAPI, FlexibleAssetTypesAPI, and FlexibleAssetFieldsAPI
classes and their methods.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from itglue.api.flexible_assets import (
    FlexibleAssetsAPI,
    FlexibleAssetTypesAPI,
    FlexibleAssetFieldsAPI,
)
from itglue.models.flexible_asset import (
    FlexibleAsset,
    FlexibleAssetCollection,
    FlexibleAssetType,
    FlexibleAssetTypeCollection,
    FlexibleAssetField,
    FlexibleAssetFieldCollection,
    FlexibleAssetStatus,
)
from itglue.exceptions import ITGlueValidationError



class TestFlexibleAssetsAPI:
    """Test FlexibleAssetsAPI class."""

    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client."""
        client = MagicMock()
        client.get = Mock()
        client.post = Mock()
        client.patch = Mock()
        client.delete = Mock()
        return client

    @pytest.fixture
    def flexible_assets_api(self, mock_http_client):
        """Create FlexibleAssetsAPI instance."""
        return FlexibleAssetsAPI(mock_http_client)

    @pytest.fixture
    def sample_asset_data(self):
        """Sample flexible asset data."""
        return {
            "data": {
                "id": "123",
                "type": "flexible_assets",
                "attributes": {
                    "name": "Web Server",
                    "flexible-asset-type-name": "Servers",
                    "status": "Active",
                    "traits": {"hostname": "web01", "ip_address": "192.168.1.100"},
                    "tag-list": ["production", "web"],
                },
            }
        }

    @pytest.fixture
    def sample_collection_data(self):
        """Sample flexible asset collection data."""
        return {
            "data": [
                {
                    "id": "1",
                    "type": "flexible_assets",
                    "attributes": {
                        "name": "Asset 1",
                        "flexible-asset-type-name": "Servers",
                        "status": "Active",
                    },
                },
                {
                    "id": "2",
                    "type": "flexible_assets",
                    "attributes": {
                        "name": "Asset 2",
                        "flexible-asset-type-name": "Workstations",
                        "status": "Inactive",
                    },
                },
            ],
            "meta": {"total-count": 2},
        }

    def test_get_by_organization(
        self, flexible_assets_api, mock_http_client, sample_collection_data
    ):
        """Test getting flexible assets by organization."""
        mock_http_client.get.return_value = sample_collection_data

        result = flexible_assets_api.get_by_organization(
            organization_id="456",
            page=1,
            per_page=25,
            include=["organization", "flexible-asset-type"],
        )

        expected_params = {
            "filter[organization_id]": "456",
            "page[number]": 1,
            "page[size]": 25,
            "include": "organization,flexible-asset-type",
        }

        mock_http_client.get.assert_called_once_with(
            "/flexible_assets", params=expected_params
        )

        assert isinstance(result, FlexibleAssetCollection)
        assert len(result) == 2

    def test_get_by_type(
        self, flexible_assets_api, mock_http_client, sample_collection_data
    ):
        """Test getting flexible assets by type."""
        mock_http_client.get.return_value = sample_collection_data

        result = flexible_assets_api.get_by_type(
            flexible_asset_type_id="789", organization_id="456"
        )

        expected_params = {
            "filter[flexible_asset_type_id]": "789",
            "filter[organization_id]": "456",
            "page[number]": 1,
            "page[size]": 50,
        }

        mock_http_client.get.assert_called_once_with(
            "/flexible_assets", params=expected_params
        )

        assert isinstance(result, FlexibleAssetCollection)

    def test_search_by_name(
        self, flexible_assets_api, mock_http_client, sample_collection_data
    ):
        """Test searching flexible assets by name."""
        mock_http_client.get.return_value = sample_collection_data

        # Test partial match
        flexible_assets_api.search_by_name("Web Server", organization_id="456")

        expected_params = {
            "filter[name]": "*Web Server*",
            "filter[organization_id]": "456",
        }

        mock_http_client.get.assert_called_with(
            "/flexible_assets", params=expected_params
        )

        # Test exact match
        flexible_assets_api.search_by_name("Web Server", exact_match=True)

        expected_params = {"filter[name]": "Web Server"}

        mock_http_client.get.assert_called_with(
            "/flexible_assets", params=expected_params
        )

    def test_search_by_trait(
        self, flexible_assets_api, mock_http_client, sample_collection_data
    ):
        """Test searching flexible assets by trait."""
        mock_http_client.get.return_value = sample_collection_data

        # Test with value
        flexible_assets_api.search_by_trait(
            trait_name="environment", trait_value="production", organization_id="456"
        )

        expected_params = {
            "filter[traits][environment]": "production",
            "filter[organization_id]": "456",
        }

        mock_http_client.get.assert_called_with(
            "/flexible_assets", params=expected_params
        )

        # Test without value (existence check)
        flexible_assets_api.search_by_trait(trait_name="hostname")

        expected_params = {"filter[traits][hostname]": "*"}

        mock_http_client.get.assert_called_with(
            "/flexible_assets", params=expected_params
        )

    def test_search_by_tag(
        self, flexible_assets_api, mock_http_client, sample_collection_data
    ):
        """Test searching flexible assets by tag."""
        mock_http_client.get.return_value = sample_collection_data

        flexible_assets_api.search_by_tag("production", organization_id="456")

        expected_params = {
            "filter[tag_list]": "production",
            "filter[organization_id]": "456",
        }

        mock_http_client.get.assert_called_once_with(
            "/flexible_assets", params=expected_params
        )

    def test_list_by_status(
        self, flexible_assets_api, mock_http_client, sample_collection_data
    ):
        """Test listing flexible assets by status."""
        mock_http_client.get.return_value = sample_collection_data

        # Test with enum
        flexible_assets_api.list_by_status(
            FlexibleAssetStatus.ACTIVE, organization_id="456"
        )

        expected_params = {
            "filter[status]": "Active",
            "filter[organization_id]": "456",
            "page[number]": 1,
            "page[size]": 50,
        }

        mock_http_client.get.assert_called_with(
            "/flexible_assets", params=expected_params
        )

        # Test with string
        flexible_assets_api.list_by_status("Archived")

        expected_params = {
            "filter[status]": "Archived",
            "page[number]": 1,
            "page[size]": 50,
        }

        mock_http_client.get.assert_called_with(
            "/flexible_assets", params=expected_params
        )

    def test_get_active_assets(
        self, flexible_assets_api, mock_http_client, sample_collection_data
    ):
        """Test getting active flexible assets."""
        mock_http_client.get.return_value = sample_collection_data

        result = flexible_assets_api.get_active_assets(organization_id="456")

        expected_params = {
            "filter[status]": "Active",
            "filter[organization_id]": "456",
            "page[number]": 1,
            "page[size]": 50,
        }

        mock_http_client.get.assert_called_once_with(
            "/flexible_assets", params=expected_params
        )
        assert isinstance(result, FlexibleAssetCollection)

    def test_create_flexible_asset(
        self, flexible_assets_api, mock_http_client, sample_asset_data
    ):
        """Test creating a flexible asset."""
        mock_http_client.post.return_value = sample_asset_data

        traits = {"hostname": "web01", "ip_address": "192.168.1.100"}
        tags = ["production", "web"]

        result = flexible_assets_api.create_flexible_asset(
            organization_id="456",
            flexible_asset_type_id="789",
            name="Web Server",
            traits=traits,
            tags=tags,
            description="Production web server",
        )

        expected_data = {
            "data": {
                "type": "flexible_assets",
                "attributes": {
                    "name": "Web Server",
                    "organization_id": "456",
                    "flexible_asset_type_id": "789",
                    "description": "Production web server",
                    "traits": traits,
                    "tag_list": tags,
                },
            }
        }

        mock_http_client.post.assert_called_once_with("/flexible_assets", expected_data)
        assert isinstance(result, FlexibleAsset)
        assert result.name == "Web Server"

    def test_create_flexible_asset_validation(self, flexible_assets_api):
        """Test flexible asset creation validation."""
        with pytest.raises(ITGlueValidationError, match="Name is required"):
            flexible_assets_api.create_flexible_asset(
                organization_id="456",
                flexible_asset_type_id="789",
                name="",  # Empty name should fail
            )

        with pytest.raises(ITGlueValidationError, match="Name is required"):
            flexible_assets_api.create_flexible_asset(
                organization_id="456",
                flexible_asset_type_id="789",
                name="   ",  # Whitespace only should fail
            )

    def test_update_traits(
        self, flexible_assets_api, mock_http_client, sample_asset_data
    ):
        """Test updating flexible asset traits."""
        # Mock get call for current asset
        current_asset_data = {
            "data": {
                "id": "123",
                "type": "flexible_assets",
                "attributes": {
                    "name": "Web Server",
                    "traits": {"hostname": "web01", "environment": "dev"},
                },
            }
        }
        mock_http_client.get.return_value = current_asset_data
        mock_http_client.patch.return_value = sample_asset_data

        new_traits = {"environment": "production", "cpu_cores": "8"}

        result = flexible_assets_api.update_traits(
            flexible_asset_id="123", traits=new_traits, merge=True
        )

        expected_data = {
            "data": {
                "type": "flexible_assets",
                "attributes": {
                    "traits": {
                        "hostname": "web01",
                        "environment": "production",
                        "cpu_cores": "8",
                    }
                },
            }
        }

        mock_http_client.patch.assert_called_once_with(
            "/flexible_assets/123", expected_data
        )
        assert isinstance(result, FlexibleAsset)

    def test_add_tags(
        self, flexible_assets_api, mock_http_client, sample_asset_data
    ):
        """Test adding tags to flexible asset."""
        # Mock get call for current asset
        current_asset_data = {
            "data": {
                "id": "123",
                "type": "flexible_assets",
                "attributes": {"name": "Web Server", "tag-list": ["production"]},
            }
        }
        mock_http_client.get.return_value = current_asset_data
        mock_http_client.patch.return_value = sample_asset_data

        result = flexible_assets_api.add_tags("123", ["web", "critical"])

        expected_data = {
            "data": {
                "type": "flexible_assets",
                "attributes": {"tag_list": ["production", "web", "critical"]},
            }
        }

        mock_http_client.patch.assert_called_once_with(
            "/flexible_assets/123", expected_data
        )
        assert isinstance(result, FlexibleAsset)

    def test_remove_tags(
        self, flexible_assets_api, mock_http_client, sample_asset_data
    ):
        """Test removing tags from flexible asset."""
        # Mock get call for current asset
        current_asset_data = {
            "data": {
                "id": "123",
                "type": "flexible_assets",
                "attributes": {
                    "name": "Web Server",
                    "tag-list": ["production", "web", "critical"],
                },
            }
        }
        mock_http_client.get.return_value = current_asset_data
        mock_http_client.patch.return_value = sample_asset_data

        result = flexible_assets_api.remove_tags("123", ["critical"])

        expected_data = {
            "data": {
                "type": "flexible_assets",
                "attributes": {"tag_list": ["production", "web"]},
            }
        }

        mock_http_client.patch.assert_called_once_with(
            "/flexible_assets/123", expected_data
        )
        assert isinstance(result, FlexibleAsset)

    def test_update_status(
        self, flexible_assets_api, mock_http_client, sample_asset_data
    ):
        """Test updating flexible asset status."""
        mock_http_client.patch.return_value = sample_asset_data

        # Test with enum
        result = flexible_assets_api.update_status(
            "123", FlexibleAssetStatus.ARCHIVED
        )

        expected_data = {
            "data": {"type": "flexible_assets", "attributes": {"status": "Archived"}}
        }

        mock_http_client.patch.assert_called_once_with(
            "/flexible_assets/123", expected_data
        )
        assert isinstance(result, FlexibleAsset)

    def test_get_asset_statistics(self, flexible_assets_api, mock_http_client):
        """Test getting asset statistics."""
        # Mock multiple API calls for different statuses
        active_response = {"data": [], "meta": {"total-count": 50}}
        inactive_response = {"data": [], "meta": {"total-count": 10}}
        archived_response = {"data": [], "meta": {"total-count": 5}}

        mock_http_client.get.side_effect = [
            active_response,
            inactive_response,
            archived_response,
        ]

        result = flexible_assets_api.get_asset_statistics(organization_id="456")

        assert result["total_count"] == 65
        assert result["active_count"] == 50
        assert result["inactive_count"] == 10
        assert result["archived_count"] == 5
        assert result["organization_id"] == "456"

        # Verify correct API calls were made
        assert mock_http_client.get.call_count == 3



class TestFlexibleAssetTypesAPI:
    """Test FlexibleAssetTypesAPI class."""

    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client."""
        client = MagicMock()
        client.get = Mock()
        return client

    @pytest.fixture
    def flexible_asset_types_api(self, mock_http_client):
        """Create FlexibleAssetTypesAPI instance."""
        return FlexibleAssetTypesAPI(mock_http_client)

    @pytest.fixture
    def sample_types_data(self):
        """Sample flexible asset types data."""
        return {
            "data": [
                {
                    "id": "1",
                    "type": "flexible_asset_types",
                    "attributes": {
                        "name": "Servers",
                        "enabled": True,
                        "builtin": False,
                    },
                },
                {
                    "id": "2",
                    "type": "flexible_asset_types",
                    "attributes": {
                        "name": "Workstations",
                        "enabled": True,
                        "builtin": True,
                    },
                },
            ]
        }

    def test_get_enabled_types(
        self, flexible_asset_types_api, mock_http_client, sample_types_data
    ):
        """Test getting enabled asset types."""
        mock_http_client.get.return_value = sample_types_data

        result = flexible_asset_types_api.get_enabled_types()

        expected_params = {"filter[enabled]": "true"}

        mock_http_client.get.assert_called_once_with(
            "/flexible_asset_types", params=expected_params
        )

        assert isinstance(result, FlexibleAssetTypeCollection)

    def test_get_builtin_types(
        self, flexible_asset_types_api, mock_http_client, sample_types_data
    ):
        """Test getting builtin asset types."""
        mock_http_client.get.return_value = sample_types_data

        result = flexible_asset_types_api.get_builtin_types()

        expected_params = {"filter[builtin]": "true"}

        mock_http_client.get.assert_called_once_with(
            "/flexible_asset_types", params=expected_params
        )

        assert isinstance(result, FlexibleAssetTypeCollection)

    def test_search_by_name(
        self, flexible_asset_types_api, mock_http_client, sample_types_data
    ):
        """Test searching asset types by name."""
        mock_http_client.get.return_value = sample_types_data

        # Test partial match
        flexible_asset_types_api.search_by_name("Server")

        expected_params = {"filter[name]": "*Server*"}
        mock_http_client.get.assert_called_with(
            "/flexible_asset_types", params=expected_params
        )

        # Test exact match
        flexible_asset_types_api.search_by_name("Servers", exact_match=True)

        expected_params = {"filter[name]": "Servers"}
        mock_http_client.get.assert_called_with(
            "/flexible_asset_types", params=expected_params
        )

    def test_get_fields(self, flexible_asset_types_api, mock_http_client):
        """Test getting fields for asset type."""
        fields_data = {
            "data": [
                {
                    "id": "1",
                    "type": "flexible_asset_fields",
                    "attributes": {
                        "name": "Hostname",
                        "kind": "Text",
                        "required": True,
                    },
                }
            ]
        }
        mock_http_client.get.return_value = fields_data

        result = flexible_asset_types_api.get_fields("123")

        expected_url = "/flexible_asset_types/123/relationships/flexible_asset_fields"

        mock_http_client.get.assert_called_once_with(expected_url)
        assert isinstance(result, FlexibleAssetFieldCollection)



class TestFlexibleAssetFieldsAPI:
    """Test FlexibleAssetFieldsAPI class."""

    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client."""
        client = MagicMock()
        client.get = Mock()
        return client

    @pytest.fixture
    def flexible_asset_fields_api(self, mock_http_client):
        """Create FlexibleAssetFieldsAPI instance."""
        return FlexibleAssetFieldsAPI(mock_http_client)

    @pytest.fixture
    def sample_fields_data(self):
        """Sample flexible asset fields data."""
        return {
            "data": [
                {
                    "id": "1",
                    "type": "flexible_asset_fields",
                    "attributes": {
                        "name": "Hostname",
                        "kind": "Text",
                        "required": True,
                    },
                },
                {
                    "id": "2",
                    "type": "flexible_asset_fields",
                    "attributes": {
                        "name": "CPU Cores",
                        "kind": "Number",
                        "required": False,
                    },
                },
            ]
        }

    def test_get_by_type(
        self, flexible_asset_fields_api, mock_http_client, sample_fields_data
    ):
        """Test getting fields by asset type."""
        mock_http_client.get.return_value = sample_fields_data

        result = flexible_asset_fields_api.get_by_type("123")

        expected_params = {"filter[flexible_asset_type_id]": "123"}

        mock_http_client.get.assert_called_once_with(
            "/flexible_asset_fields", params=expected_params
        )

        assert isinstance(result, FlexibleAssetFieldCollection)

    def test_get_required_fields(
        self, flexible_asset_fields_api, mock_http_client, sample_fields_data
    ):
        """Test getting required fields."""
        mock_http_client.get.return_value = sample_fields_data

        result = flexible_asset_fields_api.get_required_fields("123")

        expected_params = {
            "filter[flexible_asset_type_id]": "123",
            "filter[required]": "true",
        }

        mock_http_client.get.assert_called_once_with(
            "/flexible_asset_fields", params=expected_params
        )

        assert isinstance(result, FlexibleAssetFieldCollection)

    def test_get_by_kind(
        self, flexible_asset_fields_api, mock_http_client, sample_fields_data
    ):
        """Test getting fields by kind."""
        mock_http_client.get.return_value = sample_fields_data

        # Test without asset type filter
        flexible_asset_fields_api.get_by_kind("Text")

        expected_params = {"filter[kind]": "Text"}
        mock_http_client.get.assert_called_with(
            "/flexible_asset_fields", params=expected_params
        )

        # Test with asset type filter
        flexible_asset_fields_api.get_by_kind(
            "Number", flexible_asset_type_id="123"
        )

        expected_params = {
            "filter[kind]": "Number",
            "filter[flexible_asset_type_id]": "123",
        }
        mock_http_client.get.assert_called_with(
            "/flexible_asset_fields", params=expected_params
        )
