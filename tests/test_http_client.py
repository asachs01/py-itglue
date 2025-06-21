"""
Tests for ITGlue HTTP Client
"""

import json
import time
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

from itglue.config import ITGlueConfig, ITGlueRegion
from itglue.http_client import ITGlueHTTPClient, RateLimiter
from itglue.exceptions import (
    ITGlueAPIError,
    ITGlueAuthError,
    ITGlueRateLimitError,
    ITGlueNotFoundError,
    ITGlueConnectionError,
    ITGlueTimeoutError,
    ITGlueValidationError,
)


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_minute=60, requests_per_5_minutes=300)
        
        assert limiter.requests_per_minute == 60
        assert limiter.requests_per_5_minutes == 300
        assert limiter.minute_requests == []
        assert limiter.five_minute_requests == []
    
    def test_rate_limiter_no_wait_when_under_limit(self):
        """Test that no waiting occurs when under rate limit."""
        limiter = RateLimiter(requests_per_minute=60)
        
        start_time = time.time()
        limiter.wait_if_needed()
        end_time = time.time()
        
        # Should not wait
        assert end_time - start_time < 0.1
        assert len(limiter.minute_requests) == 1
    
    def test_rate_limiter_cleanup_old_requests(self):
        """Test cleanup of old request timestamps."""
        limiter = RateLimiter(requests_per_minute=60)
        
        # Add old requests
        old_time = time.time() - 120  # 2 minutes ago
        limiter.minute_requests = [old_time]
        limiter.five_minute_requests = [old_time]
        
        # Should clean up old requests
        limiter.wait_if_needed()
        
        # After wait_if_needed, old minute requests should be cleaned but old 5-minute
        # requests should remain (since 2 minutes < 5 minutes), plus new request added
        assert len(limiter.minute_requests) == 1  # Only new request
        assert len(limiter.five_minute_requests) == 2  # Old request + new request


class TestITGlueHTTPClient:
    """Test HTTP client functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ITGlueConfig(
            api_key="test-api-key",
            base_url=ITGlueRegion.US.value,
            timeout=30,
            max_retries=2,
            requests_per_minute=60,
            log_requests=False,
            log_responses=False
        )
    
    @pytest.fixture
    def http_client(self, config):
        """Create HTTP client instance."""
        return ITGlueHTTPClient(config)
    
    def test_http_client_initialization(self, config):
        """Test HTTP client initialization."""
        client = ITGlueHTTPClient(config)
        
        assert client.config == config
        assert client.session is not None
        assert client.rate_limiter is not None
        assert client.logger is not None
        
        # Check headers are set correctly
        expected_headers = config.get_headers()
        for key, value in expected_headers.items():
            assert client.session.headers[key] == value
    
    @patch('requests.Session.request')
    def test_successful_get_request(self, mock_request, http_client):
        """Test successful GET request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': [{'id': '1', 'type': 'organizations'}]}
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        result = http_client.get('/organizations')
        
        assert result == {'data': [{'id': '1', 'type': 'organizations'}]}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_successful_post_request(self, mock_request, http_client):
        """Test successful POST request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'data': {'id': '1', 'type': 'organizations'}}
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        data = {'data': {'type': 'organizations', 'attributes': {'name': 'Test Org'}}}
        result = http_client.post('/organizations', json_data=data)
        
        assert result == {'data': {'id': '1', 'type': 'organizations'}}
        mock_request.assert_called_once()
    
    @patch('requests.Session.request')
    def test_auth_error_401(self, mock_request, http_client):
        """Test 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        with pytest.raises(ITGlueAuthError, match="Unauthorized - check your API key"):
            http_client.get('/organizations')
    
    @patch('requests.Session.request')
    def test_auth_error_403(self, mock_request, http_client):
        """Test 403 forbidden error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        with pytest.raises(ITGlueAuthError, match="Forbidden - insufficient permissions"):
            http_client.get('/organizations')
    
    @patch('requests.Session.request')
    def test_not_found_error_404(self, mock_request, http_client):
        """Test 404 not found error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        with pytest.raises(ITGlueNotFoundError, match="Resource not found"):
            http_client.get('/organizations/999')
    
    @patch('requests.Session.request')
    def test_validation_error_400(self, mock_request, http_client):
        """Test 400 validation error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'errors': [{'detail': 'Invalid data'}]}
        mock_response.content = b'{"errors": [{"detail": "Invalid data"}]}'
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        with pytest.raises(ITGlueValidationError, match="Bad request - validation error"):
            http_client.post('/organizations', json_data={'invalid': 'data'})
    
    @patch('requests.Session.request')
    def test_validation_error_422(self, mock_request, http_client):
        """Test 422 unprocessable entity error."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {'errors': [{'detail': 'Validation failed'}]}
        mock_response.content = b'{"errors": [{"detail": "Validation failed"}]}'
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        with pytest.raises(ITGlueValidationError, match="Unprocessable entity - validation error"):
            http_client.post('/organizations', json_data={'invalid': 'data'})
    
    @patch('requests.Session.request')
    def test_rate_limit_error_429(self, mock_request, http_client):
        """Test 429 rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_request.return_value = mock_response
        
        from tenacity import RetryError
        with pytest.raises(RetryError):
            http_client.get('/organizations')
    
    @patch('requests.Session.request')
    def test_server_error_500(self, mock_request, http_client):
        """Test 500 server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        with pytest.raises(ITGlueAPIError, match="Server error: 500"):
            http_client.get('/organizations')
    
    @patch('requests.Session.request')
    def test_connection_error(self, mock_request, http_client):
        """Test connection error handling."""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        from tenacity import RetryError
        with pytest.raises(RetryError):
            http_client.get('/organizations')
    
    @patch('requests.Session.request')
    def test_timeout_error(self, mock_request, http_client):
        """Test timeout error handling."""
        mock_request.side_effect = requests.exceptions.Timeout("Request timeout")
        
        from tenacity import RetryError
        with pytest.raises(RetryError):
            http_client.get('/organizations')
    
    @patch('requests.Session.request')
    def test_json_decode_error(self, mock_request, http_client):
        """Test JSON decode error handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Invalid JSON response"
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        with pytest.raises(ITGlueAPIError, match="Invalid JSON response"):
            http_client.get('/organizations')
    
    def test_patch_request_with_data(self, http_client):
        """Test PATCH request with data parameter."""
        with patch('requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'data': {'id': '1'}}
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            data = {'data': {'type': 'organizations', 'attributes': {'name': 'Updated'}}}
            result = http_client.patch('/organizations/1', data=data)
            
            assert result == {'data': {'id': '1'}}
            
            # Check that data was JSON encoded and content type set
            call_args = mock_request.call_args
            assert 'data' in call_args[1]
            assert call_args[1]['data'] == json.dumps(data)
            assert call_args[1]['headers']['Content-Type'] == 'application/vnd.api+json'
    
    def test_delete_request(self, http_client):
        """Test DELETE request."""
        with patch('requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            result = http_client.delete('/organizations/1')
            
            assert result == {}  # No content for 204
            mock_request.assert_called_once()
    
    def test_context_manager(self, config):
        """Test HTTP client as context manager."""
        with ITGlueHTTPClient(config) as client:
            assert client.session is not None
        
        # Session should be closed after context exit
        # Note: We can't easily test this without mocking, but the structure is correct
    
    @patch('requests.Session.request')
    def test_retry_logic_on_connection_error(self, mock_request, http_client):
        """Test retry logic on connection errors."""
        # First two calls fail, third succeeds
        mock_request.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            Mock(status_code=200, json=lambda: {'data': []}, headers={})
        ]
        
        result = http_client.get('/organizations')
        
        assert result == {'data': []}
        assert mock_request.call_count == 3  # 1 original + 2 retries
    
    def test_get_with_params(self, http_client):
        """Test GET request with parameters."""
        with patch('requests.Session.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'data': []}
            mock_response.headers = {}
            mock_request.return_value = mock_response
            
            params = {'page[size]': 10, 'filter[name]': 'test'}
            http_client.get('/organizations', params=params)
            
            # Check that URL was constructed with parameters
            call_args = mock_request.call_args
            url = call_args[0][1]  # Second positional argument is the URL
            assert 'page%5Bsize%5D=10' in url  # URL encoded
            assert 'filter%5Bname%5D=test' in url 