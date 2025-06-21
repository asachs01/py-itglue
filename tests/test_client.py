"""
Tests for ITGlue Main Client
"""

from unittest.mock import Mock, patch
import pytest

from itglue.config import ITGlueConfig, ITGlueRegion
from itglue.client import ITGlueClient
from itglue.pagination import PaginatedResponse, PaginationInfo
from itglue.exceptions import ITGlueAPIError


class TestITGlueClient:
    """Test main ITGlue client functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ITGlueConfig(
            api_key="test-api-key",
            base_url=ITGlueRegion.US.value,
            enable_caching=True,
            cache_type="memory",
            timeout=30,
            max_retries=2,
            requests_per_minute=60
        )
    
    @pytest.fixture
    def mock_components(self):
        """Create mock components."""
        with patch('itglue.client.ITGlueHTTPClient') as mock_http, \
             patch('itglue.client.PaginationHandler') as mock_pagination, \
             patch('itglue.client.CacheManager') as mock_cache:
            
            # Configure mocks
            mock_http_instance = Mock()
            mock_pagination_instance = Mock()
            mock_cache_instance = Mock()
            
            mock_http.return_value = mock_http_instance
            mock_pagination.return_value = mock_pagination_instance
            mock_cache.return_value = mock_cache_instance
            
            yield {
                'http_client': mock_http_instance,
                'pagination': mock_pagination_instance,
                'cache': mock_cache_instance
            }
    
    def test_client_initialization(self, config, mock_components):
        """Test client initialization."""
        client = ITGlueClient(config)
        
        assert client.config == config
        assert client.http_client is not None
        assert client.pagination is not None
        assert client.cache is not None
    
    def test_client_from_environment(self, mock_components):
        """Test client creation from environment."""
        with patch.dict('os.environ', {
            'ITGLUE_API_KEY': 'test-key',
            'ITGLUE_BASE_URL': 'https://api.itglue.com'
        }):
            client = ITGlueClient.from_environment()
        
            assert client.config.api_key == 'test-key'
            assert client.config.base_url == 'https://api.itglue.com'
    
    def test_get_resource_single(self, config, mock_components):
        """Test getting a single resource."""
        mock_data = {'data': {'id': '1', 'type': 'organizations'}}
        mock_components['cache'].get.return_value = None
        mock_components['http_client'].get.return_value = mock_data
        
        client = ITGlueClient(config)
        result = client.get_resource('/organizations', resource_id='1')
        
        assert result == mock_data
        mock_components['http_client'].get.assert_called_once_with('/organizations/1', None)
        mock_components['cache'].set.assert_called_once_with('/organizations/1', mock_data, None)
    
    def test_get_resource_list(self, config, mock_components):
        """Test getting a list of resources."""
        mock_data = {'data': [{'id': '1', 'type': 'organizations'}]}
        mock_components['cache'].get.return_value = None
        mock_components['http_client'].get.return_value = mock_data
        
        client = ITGlueClient(config)
        params = {'filter[name]': 'test'}
        result = client.get_resource('/organizations', params=params)
        
        assert result == mock_data
        mock_components['http_client'].get.assert_called_once_with('/organizations', params)
        mock_components['cache'].set.assert_called_once_with('/organizations', mock_data, params)
    
    def test_get_resource_from_cache(self, config, mock_components):
        """Test getting resource from cache."""
        cached_data = {'data': [{'id': '1', 'type': 'organizations'}]}
        mock_components['cache'].get.return_value = cached_data
        
        client = ITGlueClient(config)
        result = client.get_resource('/organizations')
        
        assert result == cached_data
        mock_components['http_client'].get.assert_not_called()
    
    def test_get_resource_force_refresh(self, config, mock_components):
        """Test force refresh bypasses cache."""
        cached_data = {'data': [{'id': '1', 'type': 'organizations'}]}
        fresh_data = {'data': [{'id': '2', 'type': 'organizations'}]}
        
        mock_components['cache'].get.return_value = cached_data
        mock_components['http_client'].get.return_value = fresh_data
        
        client = ITGlueClient(config)
        result = client.get_resource('/organizations', force_refresh=True)
        
        assert result == fresh_data
        mock_components['http_client'].get.assert_called_once()
    
    def test_get_resource_page(self, config, mock_components):
        """Test getting a specific page."""
        mock_data = {
            'data': [{'id': '1'}],
            'meta': {'current-page': 2, 'total-pages': 5}
        }
        mock_response = PaginatedResponse(
            mock_data['data'], 
            mock_data['meta']
        )
        
        mock_components['cache'].get.return_value = None
        mock_components['pagination'].get_page.return_value = mock_response
        
        client = ITGlueClient(config)
        result = client.get_resource_page('/organizations', page=2, page_size=10)
        
        assert result == mock_response
        mock_components['pagination'].get_page.assert_called_once_with(
            '/organizations', 2, 10, None
        )
    
    def test_get_resource_page_from_cache(self, config, mock_components):
        """Test getting page from cache."""
        mock_data = {
            'data': [{'id': '1'}],
            'meta': {'current-page': 1}
        }
        
        mock_components['cache'].get.return_value = mock_data
        mock_components['pagination'].parse_response.return_value = PaginatedResponse(
            mock_data['data'], mock_data['meta']
        )
        
        client = ITGlueClient(config)
        result = client.get_resource_page('/organizations', page=1)
        
        assert isinstance(result, PaginatedResponse)
        mock_components['pagination'].get_page.assert_not_called()
    
    def test_get_all_resources(self, config, mock_components):
        """Test getting all resources across pages."""
        mock_data = [
            {'id': '1', 'type': 'organizations'},
            {'id': '2', 'type': 'organizations'}
        ]
        
        mock_components['pagination'].get_all_pages.return_value = mock_data
        
        client = ITGlueClient(config)
        result = client.get_all_resources('/organizations', page_size=10, max_pages=5)
        
        assert result == mock_data
        mock_components['pagination'].get_all_pages.assert_called_once_with(
            '/organizations', 10, None, 5
        )
    
    def test_iterate_resources(self, config, mock_components):
        """Test iterating over resources."""
        mock_generator = (item for item in [{'id': '1'}, {'id': '2'}])
        mock_components['pagination'].iterate_items.return_value = mock_generator
        
        client = ITGlueClient(config)
        result = client.iterate_resources('/organizations')
        
        # Should return a generator
        items = list(result)
        assert len(items) == 2
        assert items[0]['id'] == '1'
        
        mock_components['pagination'].iterate_items.assert_called_once_with(
            '/organizations', None, None, None
        )
    
    def test_iterate_pages(self, config, mock_components):
        """Test iterating over pages."""
        mock_pages = [
            PaginatedResponse([{'id': '1'}], {'current-page': 1}),
            PaginatedResponse([{'id': '2'}], {'current-page': 2})
        ]
        mock_generator = (page for page in mock_pages)
        mock_components['pagination'].iterate_pages.return_value = mock_generator
        
        client = ITGlueClient(config)
        result = client.iterate_pages('/organizations')
        
        pages = list(result)
        assert len(pages) == 2
        assert all(isinstance(page, PaginatedResponse) for page in pages)
    
    def test_create_resource(self, config, mock_components):
        """Test creating a resource."""
        request_data = {'data': {'type': 'organizations', 'attributes': {'name': 'Test'}}}
        response_data = {'data': {'id': '1', 'type': 'organizations'}}
        
        mock_components['http_client'].post.return_value = response_data
        
        client = ITGlueClient(config)
        result = client.create_resource('/organizations', request_data)
        
        assert result == response_data
        mock_components['http_client'].post.assert_called_once_with(
            '/organizations', json_data=request_data
        )
        mock_components['cache'].invalidate_endpoint.assert_called_once_with('/organizations')
    
    def test_update_resource(self, config, mock_components):
        """Test updating a resource."""
        request_data = {'data': {'type': 'organizations', 'attributes': {'name': 'Updated'}}}
        response_data = {'data': {'id': '1', 'type': 'organizations'}}
        
        mock_components['http_client'].patch.return_value = response_data
        
        client = ITGlueClient(config)
        result = client.update_resource('/organizations', '1', request_data)
        
        assert result == response_data
        mock_components['http_client'].patch.assert_called_once_with(
            '/organizations/1', json_data=request_data
        )
        mock_components['cache'].invalidate_endpoint.assert_called_once_with('/organizations')
        mock_components['cache'].delete.assert_called_once_with('/organizations/1')
    
    def test_delete_resource(self, config, mock_components):
        """Test deleting a resource."""
        mock_components['http_client'].delete.return_value = {}
        
        client = ITGlueClient(config)
        result = client.delete_resource('/organizations', '1')
        
        assert result == {}
        mock_components['http_client'].delete.assert_called_once_with('/organizations/1')
        mock_components['cache'].invalidate_endpoint.assert_called_once_with('/organizations')
        mock_components['cache'].delete.assert_called_once_with('/organizations/1')
    
    def test_clear_cache(self, config, mock_components):
        """Test clearing cache."""
        client = ITGlueClient(config)
        client.clear_cache()
        
        mock_components['cache'].clear.assert_called_once()
    
    def test_get_cache_stats_with_memory_backend(self, config, mock_components):
        """Test getting cache stats with memory backend."""
        mock_backend = Mock()
        mock_backend.cache = {'key1': 'value1', 'key2': 'value2'}
        mock_backend.max_size = 100
        mock_components['cache'].backend = mock_backend
        
        client = ITGlueClient(config)
        stats = client.get_cache_stats()
        
        assert stats['cache_enabled'] == True
        assert stats['cache_size'] == 2
        assert stats['cache_max_size'] == 100
    
    def test_get_cache_stats_without_memory_backend(self, config, mock_components):
        """Test getting cache stats without memory backend."""
        # Create a mock backend that doesn't have a 'cache' attribute
        mock_backend = Mock()
        if hasattr(mock_backend, 'cache'):
            del mock_backend.cache
        mock_components['cache'].backend = mock_backend
        
        client = ITGlueClient(config)
        stats = client.get_cache_stats()
        
        assert stats['cache_enabled'] == True
        assert 'cache_backend' in stats
        assert 'cache_size' not in stats
    
    def test_test_connection_success(self, config, mock_components):
        """Test successful connection test."""
        mock_components['cache'].get.return_value = None
        mock_components['http_client'].get.return_value = {'data': []}
        
        client = ITGlueClient(config)
        result = client.test_connection()
        
        assert result is True
    
    def test_test_connection_failure(self, config, mock_components):
        """Test failed connection test."""
        mock_components['cache'].get.return_value = None
        mock_components['http_client'].get.side_effect = ITGlueAPIError("Connection failed")
        
        client = ITGlueClient(config)
        result = client.test_connection()
        
        assert result is False
    
    def test_context_manager(self, config, mock_components):
        """Test client as context manager."""
        with ITGlueClient(config) as client:
            assert client is not None
        
        mock_components['http_client'].close.assert_called_once()
    
    def test_close(self, config, mock_components):
        """Test closing client."""
        client = ITGlueClient(config)
        client.close()
        
        mock_components['http_client'].close.assert_called_once()
    
    def test_repr(self, config, mock_components):
        """Test string representation."""
        client = ITGlueClient(config)
        repr_str = repr(client)
        
        assert 'ITGlueClient' in repr_str
        assert config.base_url in repr_str
    
    def test_post_method(self, config, mock_components):
        """Test POST method through _get_cached_or_fetch."""
        request_data = {'data': {'type': 'test'}}
        response_data = {'data': {'id': '1'}}
        
        # For POST requests, cache should not be used at all
        mock_components['cache'].get.return_value = None
        mock_components['http_client'].post.return_value = response_data
        
        client = ITGlueClient(config)
        result = client._get_cached_or_fetch('/test', request_data, 'POST')
        
        assert result == response_data
        mock_components['http_client'].post.assert_called_once_with('/test', json_data=request_data)
        # Cache should not be checked for POST
        mock_components['cache'].get.assert_not_called()
    
    def test_patch_method(self, config, mock_components):
        """Test PATCH method through _get_cached_or_fetch."""
        request_data = {'data': {'type': 'test'}}
        response_data = {'data': {'id': '1'}}
        
        # For PATCH requests, cache should not be used at all
        mock_components['cache'].get.return_value = None
        mock_components['http_client'].patch.return_value = response_data
        
        client = ITGlueClient(config)
        result = client._get_cached_or_fetch('/test', request_data, 'PATCH')
        
        assert result == response_data
        mock_components['http_client'].patch.assert_called_once_with('/test', json_data=request_data)
        # Cache should not be checked for PATCH
        mock_components['cache'].get.assert_not_called()
    
    def test_delete_method(self, config, mock_components):
        """Test DELETE method through _get_cached_or_fetch."""
        response_data = {}
        
        # For DELETE requests, cache should not be used at all
        mock_components['cache'].get.return_value = None
        mock_components['http_client'].delete.return_value = response_data
        
        client = ITGlueClient(config)
        result = client._get_cached_or_fetch('/test', method='DELETE')
        
        assert result == response_data
        mock_components['http_client'].delete.assert_called_once_with('/test')
        # Cache should not be checked for DELETE
        mock_components['cache'].get.assert_not_called()
    
    def test_unsupported_http_method(self, config, mock_components):
        """Test unsupported HTTP method raises error."""
        # Set cache to return None so it doesn't short-circuit the method check
        mock_components['cache'].get.return_value = None
        
        client = ITGlueClient(config)
        
        with pytest.raises(ValueError, match="Unsupported HTTP method: PUT"):
            client._get_cached_or_fetch('/test', method='PUT') 