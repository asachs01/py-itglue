"""Tests for the base API resource class."""

import pytest
from unittest.mock import Mock, Mock, patch
from typing import Dict, Any

from itglue.api.base import BaseAPI
from itglue.models.base import ITGlueResource, ITGlueResourceCollection, ResourceType
from itglue.http_client import ITGlueHTTPClient
from itglue.exceptions import ITGlueValidationError, ITGlueNotFoundError, ITGlueAPIError
from itglue.config import ITGlueConfig


# Test model for base API tests
class MockTestResource(ITGlueResource):
    """Mock resource model for testing."""

    def __init__(self, **data):
        if "type" not in data:
            data["type"] = ResourceType.ORGANIZATIONS
        super().__init__(**data)

    @property
    def name(self) -> str:
        return self.get_attribute("name", "")

    @name.setter
    def name(self, value: str):
        self.set_attribute("name", value)


class MockTestAPI(BaseAPI[MockTestResource]):
    """Mock API class for testing base functionality."""

    def __init__(self, client: ITGlueHTTPClient):
        super().__init__(
            client=client,
            resource_type=ResourceType.ORGANIZATIONS,
            model_class=MockTestResource,
            endpoint_path="test-resources",
        )


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing."""
    config = ITGlueConfig(api_key="test-key")
    client = Mock(spec=ITGlueHTTPClient)
    client.config = config
    return client


@pytest.fixture
def test_api(mock_http_client):
    """Test API instance."""
    return MockTestAPI(mock_http_client)


class TestBaseAPIInitialization:
    """Test BaseAPI initialization."""

    def test_init_with_valid_params(self, mock_http_client):
        """Test successful initialization."""
        api = MockTestAPI(mock_http_client)

        assert api.client == mock_http_client
        assert api.resource_type == ResourceType.ORGANIZATIONS
        assert api.model_class == MockTestResource
        assert api.endpoint_path == "test-resources"
        assert api.base_url == "/test-resources"


class TestURLBuilding:
    """Test URL building methods."""

    def test_build_url_base(self, test_api):
        """Test building base URL."""
        url = test_api._build_url()
        assert url == "/test-resources"

    def test_build_url_with_resource_id(self, test_api):
        """Test building URL with resource ID."""
        url = test_api._build_url("123")
        assert url == "/test-resources/123"

    def test_build_url_with_subpath(self, test_api):
        """Test building URL with subpath."""
        url = test_api._build_url(subpath="relationships")
        assert url == "/test-resources/relationships"

    def test_build_url_with_resource_id_and_subpath(self, test_api):
        """Test building URL with resource ID and subpath."""
        url = test_api._build_url("123", "relationships")
        assert url == "/test-resources/123/relationships"

    def test_build_url_subpath_leading_slash(self, test_api):
        """Test subpath with leading slash is handled correctly."""
        url = test_api._build_url(subpath="/relationships")
        assert url == "/test-resources/relationships"


class TestQueryParamsBuilding:
    """Test query parameter building."""

    def test_build_query_params_empty(self, test_api):
        """Test building empty query params."""
        params = test_api._build_query_params()
        assert params == {}

    def test_build_query_params_pagination(self, test_api):
        """Test building pagination params."""
        params = test_api._build_query_params(page=2, per_page=50)
        assert params == {"page[number]": "2", "page[size]": "50"}

    def test_build_query_params_sort(self, test_api):
        """Test building sort params."""
        params = test_api._build_query_params(sort="name")
        assert params == {"sort": "name"}

    def test_build_query_params_filters(self, test_api):
        """Test building filter params."""
        filter_params = {"name": "test", "status": "active"}
        params = test_api._build_query_params(filter_params=filter_params)
        assert params == {"filter[name]": "test", "filter[status]": "active"}

    def test_build_query_params_filter_list(self, test_api):
        """Test building filter params with list values."""
        filter_params = {"status": ["active", "inactive"]}
        params = test_api._build_query_params(filter_params=filter_params)
        assert params == {"filter[status]": "active,inactive"}

    def test_build_query_params_include(self, test_api):
        """Test building include params."""
        include = ["relationships", "metadata"]
        params = test_api._build_query_params(include=include)
        assert params == {"include": "relationships,metadata"}

    def test_build_query_params_additional(self, test_api):
        """Test building additional params."""
        params = test_api._build_query_params(custom_param="value")
        assert params == {"custom_param": "value"}

    def test_build_query_params_skip_none_values(self, test_api):
        """Test that None values are skipped."""
        params = test_api._build_query_params(
            page=1, per_page=None, sort="name", custom_param=None
        )
        assert params == {"page[number]": "1", "sort": "name"}


class TestResponseProcessing:
    """Test response processing."""

    def test_process_single_resource_response(self, test_api):
        """Test processing single resource response."""
        response_data = {
            "data": {
                "type": "organizations",
                "id": "123",
                "attributes": {"name": "Test Org"},
            }
        }

        with patch.object(MockTestResource, "from_api_dict") as mock_from_api:
            mock_resource = MockTestResource(id="123")
            mock_from_api.return_value = mock_resource

            result = test_api._process_response(response_data, is_collection=False)

            assert result == mock_resource
            mock_from_api.assert_called_once_with(response_data["data"])

    def test_process_collection_response(self, test_api):
        """Test processing collection response."""
        response_data = {
            "data": [
                {
                    "type": "organizations",
                    "id": "123",
                    "attributes": {"name": "Test Org 1"},
                },
                {
                    "type": "organizations",
                    "id": "124",
                    "attributes": {"name": "Test Org 2"},
                },
            ],
            "meta": {"current-page": 1},
            "links": {"self": "/test-resources"},
        }

        with patch.object(MockTestResource, "from_api_dict") as mock_from_api:
            mock_resources = [MockTestResource(id="123"), MockTestResource(id="124")]
            mock_from_api.side_effect = mock_resources

            result = test_api._process_response(response_data, is_collection=True)

            assert isinstance(result, ITGlueResourceCollection)
            assert len(result.data) == 2
            assert result.data == mock_resources
            assert mock_from_api.call_count == 2

    def test_process_response_no_data(self, test_api):
        """Test processing response with no data raises validation error."""
        response_data = {"meta": {}}

        with pytest.raises(ITGlueValidationError, match="No data in response"):
            test_api._process_response(response_data, is_collection=False)

    def test_process_response_invalid_data(self, test_api):
        """Test processing response with invalid data raises validation error."""
        response_data = {
            "data": {
                "type": "organizations",
                "id": "123",
                "attributes": {"name": "Test Org"},
            }
        }

        with patch.object(MockTestResource, "from_api_dict") as mock_from_api:
            mock_from_api.side_effect = ValueError("Invalid data")

            with pytest.raises(ITGlueValidationError, match="Invalid response format"):
                test_api._process_response(response_data, is_collection=False)


class TestAPIOperations:
    """Test CRUD operations."""

    def test_get_resource(self, test_api, mock_http_client):
        """Test getting a single resource."""
        response_data = {
            "data": {
                "type": "organizations",
                "id": "123",
                "attributes": {"name": "Test Org"},
            }
        }
        mock_http_client.get = Mock(return_value=response_data)

        with patch.object(test_api, "_process_response") as mock_process:
            mock_resource = MockTestResource(id="123")
            mock_process.return_value = mock_resource

            result = test_api.get("123")

            assert result == mock_resource
            mock_http_client.get.assert_called_once_with(
                "/test-resources/123", params={}
            )
            mock_process.assert_called_once_with(response_data, is_collection=False)

    def test_get_resource_with_include(self, test_api, mock_http_client):
        """Test getting resource with includes."""
        response_data = {"data": {"type": "organizations", "id": "123"}}
        mock_http_client.get = Mock(return_value=response_data)

        with patch.object(test_api, "_process_response") as mock_process:
            mock_resource = MockTestResource(id="123")
            mock_process.return_value = mock_resource

            test_api.get("123", include=["relationships"])

            expected_params = {"include": "relationships"}
            mock_http_client.get.assert_called_once_with(
                "/test-resources/123", params=expected_params
            )

    def test_get_resource_not_found(self, test_api, mock_http_client):
        """Test getting non-existent resource raises not found error."""
        mock_http_client.get = Mock(side_effect=ITGlueAPIError("Not found", 404))

        with pytest.raises(ITGlueNotFoundError, match="Organizations 123 not found"):
            test_api.get("123")

    def test_list_resources(self, test_api, mock_http_client):
        """Test listing resources."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = Mock(return_value=response_data)

        with patch.object(test_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            result = test_api.list(page=1, per_page=10)

            assert result == mock_collection
            expected_params = {"page[number]": "1", "page[size]": "10"}
            mock_http_client.get.assert_called_once_with(
                "/test-resources", params=expected_params
            )
            mock_process.assert_called_once_with(response_data, is_collection=True)

    def test_create_resource(self, test_api, mock_http_client):
        """Test creating a resource."""
        response_data = {
            "data": {
                "type": "organizations",
                "id": "123",
                "attributes": {"name": "New Org"},
            }
        }
        mock_http_client.post = Mock(return_value=response_data)

        with patch.object(test_api, "_process_response") as mock_process:
            # Create mock resource with the expected attributes
            mock_resource = MockTestResource(id="123", attributes={"name": "New Org"})
            mock_process.return_value = mock_resource

            data = {"name": "New Org"}
            result = test_api.create(data)

            assert result == mock_resource
            # Verify the data was converted to API format
            mock_http_client.post.assert_called_once()
            call_args = mock_http_client.post.call_args
            assert call_args[0][0] == "/test-resources"

    def test_update_resource(self, test_api, mock_http_client):
        """Test updating a resource."""
        response_data = {
            "data": {
                "type": "organizations",
                "id": "123",
                "attributes": {"name": "Updated Org"},
            }
        }
        mock_http_client.patch = Mock(return_value=response_data)

        with patch.object(test_api, "_process_response") as mock_process:
            # Create mock resource with the expected attributes
            mock_resource = MockTestResource(id="123", attributes={"name": "Updated Org"})
            mock_process.return_value = mock_resource

            data = {"name": "Updated Org"}
            result = test_api.update("123", data)

            assert result == mock_resource
            mock_http_client.patch.assert_called_once()
            call_args = mock_http_client.patch.call_args
            assert call_args[0][0] == "/test-resources/123"

    def test_delete_resource(self, test_api, mock_http_client):
        """Test deleting a resource."""
        mock_http_client.delete = Mock(return_value=None)

        test_api.delete("123")

        mock_http_client.delete.assert_called_once_with(
            "/test-resources/123", params={}
        )

    def test_delete_resource_not_found(self, test_api, mock_http_client):
        """Test deleting non-existent resource raises not found error."""
        mock_http_client.delete = Mock(
            side_effect=ITGlueAPIError("Not found", 404)
        )

        with pytest.raises(ITGlueNotFoundError, match="Organizations 123 not found"):
            test_api.delete("123")

    def test_search_resources(self, test_api, mock_http_client):
        """Test searching resources."""
        response_data = {"data": [], "meta": {}}
        mock_http_client.get = Mock(return_value=response_data)

        with patch.object(test_api, "_process_response") as mock_process:
            mock_collection = ITGlueResourceCollection(data=[])
            mock_process.return_value = mock_collection

            result = test_api.search("test query")

            assert result == mock_collection
            expected_params = {"filter[name]": "test query"}
            mock_http_client.get.assert_called_once_with(
                "/test-resources", params=expected_params
            )
