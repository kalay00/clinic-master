"""
认证中间件：JWT Token验证
"""
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.core.logger import logger


class JWTBearer(HTTPBearer):
    """JWT Bearer Token认证"""
    
    def __init__(self, auto_error: bool = True):
        """
        初始化JWT Bearer
        
        Args:
            auto_error: 是否自动抛出错误
        """
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[dict]:
        """
        验证Token
        
        Args:
            request: 请求对象
        
        Returns:
            Optional[dict]: Token载荷，验证失败返回None或抛出异常
        
        Raises:
            HTTPException: Token验证失败
        """
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            
            payload = decode_token(credentials.credentials)
            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            
            return payload
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code."
            )


# 创建JWT认证实例
jwt_bearer = JWTBearer()


def get_current_user(request: Request) -> dict:
    """
    从请求中获取当前用户信息
    
    Args:
        request: 请求对象
    
    Returns:
        dict: 用户信息（包含user_id, tenant_id等）
    
    Raises:
        UnauthorizedException: 未授权
    """
    # 从请求状态中获取用户信息（由中间件设置）
    user = getattr(request.state, "user", None)
    if not user:
        raise UnauthorizedException("未授权访问")
    return user


def get_current_tenant_id(request: Request) -> str:
    """
    从请求中获取当前租户ID
    
    Args:
        request: 请求对象
    
    Returns:
        str: 租户ID
    
    Raises:
        UnauthorizedException: 未授权
    """
    user = get_current_user(request)
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        raise UnauthorizedException("租户ID不存在")
    return tenant_id


def get_current_user_id(request: Request) -> str:
    """
    从请求中获取当前用户ID
    
    Args:
        request: 请求对象
    
    Returns:
        str: 用户ID
    
    Raises:
        UnauthorizedException: 未授权
    """
    user = get_current_user(request)
    user_id = user.get("user_id") or user.get("sub")
    if not user_id:
        raise UnauthorizedException("用户ID不存在")
    return user_id


def get_current_tenant(request: Request) -> str:
    """
    依赖注入函数：从请求中获取当前租户ID（用于FastAPI的Depends）
    
    Args:
        request: 请求对象
    
    Returns:
        str: 租户ID
    
    Raises:
        UnauthorizedException: 未授权或租户ID不存在
    """
    return get_current_tenant_id(request)


def get_current_tenant_optional(request: Request) -> Optional[str]:
    """
    依赖注入函数：从请求中获取当前租户ID（可选，用于FastAPI的Depends）
    
    Args:
        request: 请求对象
    
    Returns:
        Optional[str]: 租户ID，不存在返回None
    """
    try:
        return get_current_tenant_id(request)
    except Exception:
        return None

