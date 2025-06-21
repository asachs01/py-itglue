"""
ITGlue Caching System

Provides caching capabilities for ITGlue API responses to improve performance
and reduce API usage. Supports both in-memory and Redis caching.
"""

import json
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import structlog

from .config import ITGlueConfig
from .exceptions import ITGlueCacheError


class CacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.logger = structlog.get_logger().bind(component="memory_cache")
    
    def _cleanup_if_needed(self) -> None:
        """Remove oldest entries if cache is full."""
        if len(self.cache) >= self.max_size:
            # Remove 20% of oldest entries
            num_to_remove = max(1, self.max_size // 5)
            oldest_keys = sorted(
                self.access_times.keys(),
                key=lambda k: self.access_times[k]
            )[:num_to_remove]
            
            for key in oldest_keys:
                del self.cache[key]
                del self.access_times[key]
            
            self.logger.info(
                "Cleaned up cache",
                removed_entries=num_to_remove,
                remaining_entries=len(self.cache)
            )
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        if 'expires_at' not in entry:
            return False
        
        return time.time() > entry['expires_at']
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if self._is_expired(entry):
            del self.cache[key]
            del self.access_times[key]
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        
        return entry['data']
    
    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        self._cleanup_if_needed()
        
        entry = {'data': value}
        
        if ttl:
            entry['expires_at'] = time.time() + ttl
        
        self.cache[key] = entry
        self.access_times[key] = time.time()
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
            del self.access_times[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.access_times.clear()
        self.logger.info("Cleared all cache entries")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if key not in self.cache:
            return False
        
        entry = self.cache[key]
        if self._is_expired(entry):
            del self.cache[key]
            del self.access_times[key]
            return False
        
        return True


class RedisCache(CacheBackend):
    """Redis cache backend."""
    
    def __init__(self, redis_client, key_prefix: str = "itglue:"):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.logger = structlog.get_logger().bind(component="redis_cache")
    
    def _get_full_key(self, key: str) -> str:
        """Get full key with prefix."""
        return f"{self.key_prefix}{key}"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache."""
        try:
            full_key = self._get_full_key(key)
            data = self.redis.get(full_key)
            
            if data is None:
                return None
            
            return json.loads(data)
            
        except Exception as e:
            self.logger.error("Redis get error", key=key, error=str(e))
            raise ITGlueCacheError(f"Failed to get from Redis cache: {e}")
    
    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        try:
            full_key = self._get_full_key(key)
            data = json.dumps(value)
            
            if ttl:
                self.redis.setex(full_key, ttl, data)
            else:
                self.redis.set(full_key, data)
                
        except Exception as e:
            self.logger.error("Redis set error", key=key, error=str(e))
            raise ITGlueCacheError(f"Failed to set in Redis cache: {e}")
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        try:
            full_key = self._get_full_key(key)
            self.redis.delete(full_key)
            
        except Exception as e:
            self.logger.error("Redis delete error", key=key, error=str(e))
            raise ITGlueCacheError(f"Failed to delete from Redis cache: {e}")
    
    def clear(self) -> None:
        """Clear all cache entries with our prefix."""
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis.keys(pattern)
            
            if keys:
                self.redis.delete(*keys)
                self.logger.info("Cleared Redis cache entries", count=len(keys))
            
        except Exception as e:
            self.logger.error("Redis clear error", error=str(e))
            raise ITGlueCacheError(f"Failed to clear Redis cache: {e}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            full_key = self._get_full_key(key)
            return bool(self.redis.exists(full_key))
            
        except Exception as e:
            self.logger.error("Redis exists error", key=key, error=str(e))
            raise ITGlueCacheError(f"Failed to check Redis cache: {e}")


class CacheManager:
    """Manages caching for ITGlue API responses."""
    
    def __init__(self, config: ITGlueConfig):
        self.config = config
        self.logger = structlog.get_logger().bind(component="cache_manager")
        
        # Initialize cache backend
        if not config.enable_caching:
            self.backend = None
            self.logger.info("Caching disabled")
        elif config.cache_type == "memory":
            self.backend = MemoryCache(max_size=1000)  # Default max size
            self.logger.info("Using memory cache")
        elif config.cache_type == "redis":
            if config.redis_url:
                try:
                    import redis
                    redis_client = redis.from_url(config.redis_url)
                    self.backend = RedisCache(redis_client)
                    self.logger.info("Using Redis cache", url=config.redis_url)
                except ImportError:
                    self.logger.warning("Redis not available, falling back to memory cache")
                    self.backend = MemoryCache(max_size=1000)
                except Exception as e:
                    self.logger.error("Failed to connect to Redis", error=str(e))
                    self.backend = MemoryCache(max_size=1000)
            else:
                self.logger.warning("Redis URL not provided, using memory cache")
                self.backend = MemoryCache(max_size=1000)
        else:
            self.logger.warning(f"Unknown cache backend: {config.cache_type}, using memory")
            self.backend = MemoryCache(max_size=1000)
    
    def _generate_cache_key(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> str:
        """Generate cache key for request."""
        # Create a consistent cache key
        key_data = {
            'method': method,
            'endpoint': endpoint,
            'params': params or {}
        }
        
        # Sort params for consistent keys
        if params:
            key_data['params'] = dict(sorted(params.items()))
        
        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        
        return cache_key
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        if not self.backend:
            return None
        
        cache_key = self._generate_cache_key(endpoint, params, method)
        
        try:
            result = self.backend.get(cache_key)
            if result:
                self.logger.debug("Cache hit", endpoint=endpoint, key=cache_key)
            else:
                self.logger.debug("Cache miss", endpoint=endpoint, key=cache_key)
            return result
            
        except Exception as e:
            self.logger.error("Cache get error", error=str(e))
            return None
    
    def set(
        self,
        endpoint: str,
        response_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        ttl: Optional[int] = None
    ) -> None:
        """Cache response data."""
        if not self.backend:
            return
        
        cache_key = self._generate_cache_key(endpoint, params, method)
        
        # Use configured TTL if not provided
        if ttl is None:
            ttl = self.config.cache_ttl
        
        try:
            self.backend.set(cache_key, response_data, ttl)
            self.logger.debug("Cached response", endpoint=endpoint, key=cache_key, ttl=ttl)
            
        except Exception as e:
            self.logger.error("Cache set error", error=str(e))
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> None:
        """Delete cached response."""
        if not self.backend:
            return
        
        cache_key = self._generate_cache_key(endpoint, params, method)
        
        try:
            self.backend.delete(cache_key)
            self.logger.debug("Deleted cache entry", endpoint=endpoint, key=cache_key)
            
        except Exception as e:
            self.logger.error("Cache delete error", error=str(e))
    
    def clear(self) -> None:
        """Clear all cached data."""
        if not self.backend:
            return
        
        try:
            self.backend.clear()
            self.logger.info("Cleared all cache data")
            
        except Exception as e:
            self.logger.error("Cache clear error", error=str(e))
    
    def invalidate_endpoint(self, endpoint_pattern: str) -> None:
        """Invalidate cache entries matching endpoint pattern."""
        # This is a simplified implementation
        # In a production system, you might want more sophisticated pattern matching
        if not self.backend:
            return
        
        self.logger.info("Cache invalidation requested", pattern=endpoint_pattern)
        # For now, we'll just clear everything
        # TODO: Implement pattern-based invalidation
        self.clear() 