# src/utils/cache.py
import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import aioredis
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Cache manager using Redis"""
    
    def __init__(self, url: str = "redis://localhost:6379/0", ttl: int = 3600):
        self.redis = None
        self.url = url
        self.default_ttl = ttl
        
    async def init_redis(self):
        """Initialize Redis connection"""
        if not self.redis:
            self.redis = await aioredis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis connection established")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            await self.redis.connection_pool.disconnect()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.redis:
                await self.init_redis()
                
            value = await self.redis.get(key)
            if value is not None:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if not self.redis:
                await self.init_redis()
                
            ttl = ttl or self.default_ttl
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
                
            await self.redis.set(key, value, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from cache"""
        try:
            if not self.redis:
                await self.init_redis()
                
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return 0
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache keys matching a pattern"""
        try:
            if not self.redis:
                await self.init_redis()
                
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern: {str(e)}")
            return 0

# Global cache instance
cache_manager = CacheManager()

# Context manager for async operations
class CacheContext:
    def __init__(self, cache: CacheManager):
        self.cache = cache
    
    async def __aenter__(self):
        await self.cache.init_redis()
        return self.cache
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cache.close()

# Example usage:
# async with CacheContext(cache_manager) as cache:
#     await cache.set("key", "value")
#     value = await cache.get("key")