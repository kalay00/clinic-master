"""
Redis连接管理
"""
import redis
from typing import Optional
from redis.connection import ConnectionPool

from app.core.config import settings


class RedisClient:
    """Redis客户端管理类"""
    
    _pool: Optional[ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    
    @classmethod
    def get_pool(cls) -> ConnectionPool:
        """
        获取Redis连接池
        
        Returns:
            ConnectionPool: Redis连接池对象
        """
        if cls._pool is None:
            # 优先使用REDIS_URL，如果没有则使用单独配置
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                redis_url = settings.REDIS_URL
                if settings.REDIS_PASSWORD and settings.REDIS_PASSWORD != "":
                    # 如果设置了密码，需要手动构建连接参数
                    import urllib.parse
                    parsed = urllib.parse.urlparse(redis_url)
                    cls._pool = ConnectionPool(
                        host=parsed.hostname or getattr(settings, 'REDIS_HOST', 'localhost'),
                        port=parsed.port or getattr(settings, 'REDIS_PORT', 6379),
                        password=settings.REDIS_PASSWORD,
                        db=int(parsed.path.lstrip('/')) if parsed.path else getattr(settings, 'REDIS_DB', 0),
                        max_connections=50,
                        decode_responses=True,
                    )
                else:
                    cls._pool = ConnectionPool.from_url(
                        redis_url,
                        max_connections=50,
                        decode_responses=True,
                    )
            else:
                # 使用单独配置
                cls._pool = ConnectionPool(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    password=getattr(settings, 'REDIS_PASSWORD', None) or None,
                    db=getattr(settings, 'REDIS_DB', 0),
                    max_connections=50,
                    decode_responses=True,
                )
        return cls._pool
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """
        获取Redis客户端实例
        
        Returns:
            redis.Redis: Redis客户端对象
        """
        if cls._client is None:
            cls._client = redis.Redis(connection_pool=cls.get_pool())
        return cls._client
    
    @classmethod
    def close(cls) -> None:
        """
        关闭Redis连接池
        """
        if cls._pool:
            cls._pool.disconnect()
            cls._pool = None
            cls._client = None
    
    @classmethod
    def test_connection(cls) -> bool:
        """
        测试Redis连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            client = cls.get_client()
            client.ping()
            return True
        except Exception:
            return False


# 导出Redis客户端实例
redis_client = RedisClient.get_client()

