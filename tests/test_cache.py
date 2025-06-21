"""
Tests for ITGlue Cache System
"""

import time
from unittest.mock import Mock, patch, MagicMock
import pytest

from itglue.config import ITGlueConfig, ITGlueRegion
from itglue.cache import (
    MemoryCache,
    RedisCache,
    CacheManager,
)
from itglue.exceptions import ITGlueCacheError


class TestMemoryCache:
    """Test memory cache backend."""
    
    def test_memory_cache_initialization(self):
        """Test memory cache initialization."""
        cache = MemoryCache(max_size=100)
        
        assert cache.max_size == 100
        assert cache.cache == {}
        assert cache.access_times == {}
    
    def test_set_and_get(self):
        """Test setting and getting values."""
        cache = MemoryCache()
        data = {'key': 'value', 'number': 42}
        
        cache.set('test_key', data)
        result = cache.get('test_key')
        
        assert result == data
    
    def test_get_nonexistent_key(self):
        """Test getting non-existent key returns None."""
        cache = MemoryCache()
        
        result = cache.get('nonexistent')
        
        assert result is None
    
    def test_set_with_ttl(self):
        """Test setting value with TTL."""
        cache = MemoryCache()
        data = {'key': 'value'}
        
        cache.set('test_key', data, ttl=1)  # 1 second TTL
        
        # Should be available immediately
        assert cache.get('test_key') == data
        
        # Should expire after TTL
        time.sleep(1.1)
        assert cache.get('test_key') is None
    
    def test_delete(self):
        """Test deleting values."""
        cache = MemoryCache()
        data = {'key': 'value'}
        
        cache.set('test_key', data)
        assert cache.get('test_key') == data
        
        cache.delete('test_key')
        assert cache.get('test_key') is None
    
    def test_delete_nonexistent_key(self):
        """Test deleting non-existent key doesn't raise error."""
        cache = MemoryCache()
        
        # Should not raise any error
        cache.delete('nonexistent')
    
    def test_clear(self):
        """Test clearing all cache entries."""
        cache = MemoryCache()
        
        cache.set('key1', {'value': 1})
        cache.set('key2', {'value': 2})
        
        assert len(cache.cache) == 2
        
        cache.clear()
        
        assert len(cache.cache) == 0
        assert len(cache.access_times) == 0
    
    def test_exists(self):
        """Test checking if key exists."""
        cache = MemoryCache()
        data = {'key': 'value'}
        
        assert cache.exists('test_key') is False
        
        cache.set('test_key', data)
        assert cache.exists('test_key') is True
        
        cache.delete('test_key')
        assert cache.exists('test_key') is False
    
    def test_exists_expired_key(self):
        """Test exists with expired key."""
        cache = MemoryCache()
        data = {'key': 'value'}
        
        cache.set('test_key', data, ttl=1)
        assert cache.exists('test_key') is True
        
        time.sleep(1.1)
        assert cache.exists('test_key') is False
    
    def test_cleanup_when_full(self):
        """Test cleanup when cache reaches max size."""
        cache = MemoryCache(max_size=3)
        
        # Fill cache to max capacity
        cache.set('key1', {'value': 1})
        time.sleep(0.01)  # Ensure different access times
        cache.set('key2', {'value': 2})
        time.sleep(0.01)
        cache.set('key3', {'value': 3})
        
        assert len(cache.cache) == 3
        
        # Adding one more should trigger cleanup
        cache.set('key4', {'value': 4})
        
        # Should have removed oldest entry (20% = 1 entry)
        assert len(cache.cache) == 3
        assert cache.get('key1') is None  # Oldest should be removed
        assert cache.get('key4') is not None  # New entry should exist
    
    def test_access_time_update(self):
        """Test that access times are updated on get."""
        cache = MemoryCache()
        data = {'key': 'value'}
        
        cache.set('test_key', data)
        initial_time = cache.access_times['test_key']
        
        time.sleep(0.01)
        cache.get('test_key')
        
        updated_time = cache.access_times['test_key']
        assert updated_time > initial_time


class TestRedisCache:
    """Test Redis cache backend."""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        mock_redis = Mock()
        return mock_redis
    
    @pytest.fixture
    def redis_cache(self, mock_redis):
        """Create Redis cache instance."""
        return RedisCache(mock_redis, key_prefix="test:")
    
    def test_redis_cache_initialization(self, mock_redis):
        """Test Redis cache initialization."""
        cache = RedisCache(mock_redis, key_prefix="itglue:")
        
        assert cache.redis == mock_redis
        assert cache.key_prefix == "itglue:"
    
    def test_get_full_key(self, redis_cache):
        """Test key prefix handling."""
        full_key = redis_cache._get_full_key("test_key")
        assert full_key == "test:test_key"
    
    def test_set_and_get(self, redis_cache, mock_redis):
        """Test setting and getting values."""
        data = {'key': 'value', 'number': 42}
        mock_redis.get.return_value = '{"key": "value", "number": 42}'
        
        redis_cache.set('test_key', data)
        result = redis_cache.get('test_key')
        
        assert result == data
        mock_redis.set.assert_called_once_with('test:test_key', '{"key": "value", "number": 42}')
        mock_redis.get.assert_called_once_with('test:test_key')
    
    def test_set_with_ttl(self, redis_cache, mock_redis):
        """Test setting value with TTL."""
        data = {'key': 'value'}
        
        redis_cache.set('test_key', data, ttl=300)
        
        mock_redis.setex.assert_called_once_with('test:test_key', 300, '{"key": "value"}')
    
    def test_get_nonexistent_key(self, redis_cache, mock_redis):
        """Test getting non-existent key returns None."""
        mock_redis.get.return_value = None
        
        result = redis_cache.get('test_key')
        
        assert result is None
    
    def test_delete(self, redis_cache, mock_redis):
        """Test deleting values."""
        redis_cache.delete('test_key')
        
        mock_redis.delete.assert_called_once_with('test:test_key')
    
    def test_clear(self, redis_cache, mock_redis):
        """Test clearing all cache entries."""
        mock_redis.keys.return_value = ['test:key1', 'test:key2']
        
        redis_cache.clear()
        
        mock_redis.keys.assert_called_once_with('test:*')
        mock_redis.delete.assert_called_once_with('test:key1', 'test:key2')
    
    def test_clear_no_keys(self, redis_cache, mock_redis):
        """Test clearing when no keys exist."""
        mock_redis.keys.return_value = []
        
        redis_cache.clear()
        
        mock_redis.keys.assert_called_once_with('test:*')
        mock_redis.delete.assert_not_called()
    
    def test_exists(self, redis_cache, mock_redis):
        """Test checking if key exists."""
        mock_redis.exists.return_value = 1
        
        result = redis_cache.exists('test_key')
        
        assert result is True
        mock_redis.exists.assert_called_once_with('test:test_key')
    
    def test_redis_error_handling(self, redis_cache, mock_redis):
        """Test error handling for Redis operations."""
        mock_redis.get.side_effect = Exception("Redis connection failed")
        
        with pytest.raises(ITGlueCacheError, match="Failed to get from Redis cache"):
            redis_cache.get('test_key')


class TestCacheManager:
    """Test cache manager functionality."""
    
    @pytest.fixture
    def config_memory(self):
        """Create config for memory cache."""
        return ITGlueConfig(
            api_key="test-key",
            base_url=ITGlueRegion.US.value,
            enable_caching=True,
            cache_type="memory",
            cache_ttl=300
        )
    
    @pytest.fixture
    def config_redis(self):
        """Create config for Redis cache."""
        return ITGlueConfig(
            api_key="test-key",
            base_url=ITGlueRegion.US.value,
            enable_caching=True,
            cache_type="redis",
            redis_url="redis://localhost:6379",
            cache_ttl=300
        )
    
    @pytest.fixture
    def config_disabled(self):
        """Create config with caching disabled."""
        return ITGlueConfig(
            api_key="test-key",
            base_url=ITGlueRegion.US.value,
            enable_caching=False
        )
    
    def test_cache_manager_memory_backend(self, config_memory):
        """Test cache manager with memory backend."""
        manager = CacheManager(config_memory)
        
        assert manager.backend is not None
        assert isinstance(manager.backend, MemoryCache)
    
    def test_cache_manager_disabled(self, config_disabled):
        """Test cache manager with caching disabled."""
        manager = CacheManager(config_disabled)
        
        assert manager.backend is None
    
    @patch('redis.from_url')
    def test_cache_manager_redis_backend(self, mock_redis_from_url, config_redis):
        """Test cache manager with Redis backend."""
        mock_redis_client = Mock()
        mock_redis_from_url.return_value = mock_redis_client
        
        manager = CacheManager(config_redis)
        
        assert manager.backend is not None
        assert isinstance(manager.backend, RedisCache)
        mock_redis_from_url.assert_called_once_with("redis://localhost:6379")
    
    @patch('redis.from_url')
    def test_cache_manager_redis_import_error(self, mock_redis_from_url, config_redis):
        """Test fallback to memory cache when Redis import fails."""
        mock_redis_from_url.side_effect = ImportError("Redis not available")
        
        manager = CacheManager(config_redis)
        
        # Should fallback to memory cache
        assert manager.backend is not None
        assert isinstance(manager.backend, MemoryCache)
    
    @patch('redis.from_url')
    def test_cache_manager_redis_connection_error(self, mock_redis_from_url, config_redis):
        """Test fallback to memory cache when Redis connection fails."""
        mock_redis_from_url.side_effect = Exception("Connection failed")
        
        manager = CacheManager(config_redis)
        
        # Should fallback to memory cache
        assert manager.backend is not None
        assert isinstance(manager.backend, MemoryCache)
    
    def test_generate_cache_key(self, config_memory):
        """Test cache key generation."""
        manager = CacheManager(config_memory)
        
        key1 = manager._generate_cache_key('/organizations', {'page': 1}, 'GET')
        key2 = manager._generate_cache_key('/organizations', {'page': 1}, 'GET')
        key3 = manager._generate_cache_key('/organizations', {'page': 2}, 'GET')
        
        # Same parameters should generate same key
        assert key1 == key2
        
        # Different parameters should generate different key
        assert key1 != key3
    
    def test_cache_key_parameter_order(self, config_memory):
        """Test that parameter order doesn't affect cache key."""
        manager = CacheManager(config_memory)
        
        key1 = manager._generate_cache_key('/test', {'a': 1, 'b': 2})
        key2 = manager._generate_cache_key('/test', {'b': 2, 'a': 1})
        
        # Should be the same regardless of parameter order
        assert key1 == key2
    
    def test_get_and_set_with_backend(self, config_memory):
        """Test get and set operations."""
        manager = CacheManager(config_memory)
        endpoint = '/organizations'
        params = {'page': 1}
        data = {'data': [{'id': '1', 'type': 'organizations'}]}
        
        # Should return None initially
        result = manager.get(endpoint, params)
        assert result is None
        
        # Set data
        manager.set(endpoint, data, params)
        
        # Should return cached data
        result = manager.get(endpoint, params)
        assert result == data
    
    def test_get_and_set_without_backend(self, config_disabled):
        """Test get and set operations when caching is disabled."""
        manager = CacheManager(config_disabled)
        endpoint = '/organizations'
        data = {'data': []}
        
        # Should always return None
        result = manager.get(endpoint)
        assert result is None
        
        # Set should do nothing (no error)
        manager.set(endpoint, data)
        
        # Should still return None
        result = manager.get(endpoint)
        assert result is None
    
    def test_delete_with_backend(self, config_memory):
        """Test delete operation."""
        manager = CacheManager(config_memory)
        endpoint = '/organizations'
        data = {'data': []}
        
        # Set and verify
        manager.set(endpoint, data)
        assert manager.get(endpoint) == data
        
        # Delete and verify
        manager.delete(endpoint)
        assert manager.get(endpoint) is None
    
    def test_clear_with_backend(self, config_memory):
        """Test clear operation."""
        manager = CacheManager(config_memory)
        
        # Set multiple items
        manager.set('/organizations', {'data': []})
        manager.set('/configurations', {'data': []})
        
        # Clear all
        manager.clear()
        
        # Verify all cleared
        assert manager.get('/organizations') is None
        assert manager.get('/configurations') is None
    
    def test_invalidate_endpoint(self, config_memory):
        """Test endpoint invalidation."""
        manager = CacheManager(config_memory)
        
        # Set some data
        manager.set('/organizations', {'data': []})
        
        # Invalidate (currently just clears all)
        manager.invalidate_endpoint('/organizations')
        
        # Should be cleared
        assert manager.get('/organizations') is None
    
    def test_cache_error_handling(self, config_memory):
        """Test error handling in cache operations."""
        manager = CacheManager(config_memory)
        
        # Mock backend to raise errors
        manager.backend.get = Mock(side_effect=Exception("Cache error"))
        manager.backend.set = Mock(side_effect=Exception("Cache error"))
        
        # Get should return None on error
        result = manager.get('/test')
        assert result is None
        
        # Set should not raise error
        manager.set('/test', {'data': []})  # Should not raise 