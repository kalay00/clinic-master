"""
权限验证中间件和装饰器
"""
from typing import List, Optional, Callable
from functools import wraps
from fastapi import Request, HTTPException, status

from app.core.exceptions import ForbiddenException
from app.core.logger import logger
from app.core.middleware.auth import get_current_user


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self):
        """初始化权限检查器"""
        self._permission_cache = {}  # 权限缓存
    
    async def check_permission(
        self,
        request: Request,
        required_permissions: List[str]
    ) -> bool:
        """
        检查用户权限
        
        Args:
            request: 请求对象
            required_permissions: 所需权限列表
        
        Returns:
            bool: 是否有权限
        """
        if not required_permissions:
            return True
        
        try:
            user = get_current_user(request)
            user_id = user.get("user_id") or user.get("sub")
            
            if not user_id:
                return False
            
            # 检查用户权限（这里简化处理，实际应该从数据库或缓存中获取）
            # TODO: 实现完整的权限检查逻辑
            user_permissions = await self._get_user_permissions(user_id)
            
            # 检查是否有任一所需权限
            for perm in required_permissions:
                if perm in user_permissions:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"权限检查失败: {str(e)}")
            return False
    
    async def _get_user_permissions(self, user_id: str) -> List[str]:
        """
        获取用户权限列表
        
        Args:
            user_id: 用户ID
        
        Returns:
            List[str]: 权限列表
        """
        # TODO: 从数据库或Redis缓存中获取用户权限
        # 这里返回空列表，实际实现时需要查询数据库
        return []


# 创建全局权限检查器实例
permission_checker = PermissionChecker()


def require_permissions(*permissions: str):
    """
    权限验证装饰器
    
    Args:
        *permissions: 所需权限列表
    
    Returns:
        Callable: 装饰后的函数
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取request对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request object not found"
                )
            
            # 检查权限
            has_permission = await permission_checker.check_permission(
                request,
                list(permissions)
            )
            
            if not has_permission:
                raise ForbiddenException(
                    f"缺少所需权限: {', '.join(permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

