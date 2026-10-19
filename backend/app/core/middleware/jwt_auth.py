"""
JWT认证中间件：自动验证Token并设置用户信息
"""
from typing import Optional
from fastapi import Request, HTTPException, status

from app.core.security import decode_token
from app.core.logger import logger
from app.core.exceptions import UnauthorizedException


async def jwt_auth_middleware(request: Request, call_next):
    """
    JWT认证中间件：自动验证Token并设置用户信息到request.state
    
    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理函数
    
    Returns:
        Response: 响应对象
    """
    # 排除不需要认证的路径
    excluded_paths = [
        "/",
        "/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/platform/login",
    ]
    
    # 检查是否需要认证
    need_auth = True
    for path in excluded_paths:
        if request.url.path.startswith(path):
            need_auth = False
            break
    
    # 无论是否需要认证，都尝试提取Token（用于可选认证的路径）
    authorization = request.headers.get("Authorization")
    if authorization:
        try:
            # 提取Bearer Token
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authorization scheme")
            
            # 解码Token
            payload = decode_token(token)
            if payload is None:
                if need_auth:
                    logger.warning(f"Token验证失败: {request.url.path}")
                # 不抛出异常，让路由处理函数决定如何处理
            else:
                # 设置用户信息到request.state（无论是否需要认证）
                request.state.user = payload
                request.state.token = token
                logger.info(f"用户认证成功: {payload.get('user_id')}, 角色: {payload.get('role')}, 租户: {payload.get('tenant_id')}")
        except (ValueError, IndexError) as e:
            if need_auth:
                logger.warning(f"Token格式错误: {str(e)}")
        except Exception as e:
            logger.error(f"Token验证异常: {str(e)}")
    elif need_auth:
        # 需要认证但没有Token，但不抛出异常（由路由处理函数决定）
        logger.debug(f"请求未包含Token: {request.url.path}")
    
    response = await call_next(request)
    return response

