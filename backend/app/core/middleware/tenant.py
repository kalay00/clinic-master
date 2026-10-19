"""
多租户中间件：自动提取和验证tenant_id
"""
from typing import Optional
from fastapi import Request, HTTPException, status

from app.core.logger import logger
from app.core.exceptions import UnauthorizedException, BusinessException


async def tenant_middleware(request: Request, call_next):
    """
    多租户中间件：从Token、Header或域名中提取tenant_id
    
    优先级：
    1. Token中的tenant_id（已认证用户）
    2. Header中的X-Tenant-Id
    3. Header中的X-Tenant-Code（根据代码查找租户）
    4. 域名识别（从Host header提取）
    
    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理函数
    
    Returns:
        Response: 响应对象
    """
    tenant_id = None
    
    # 从请求状态中获取用户信息（由认证中间件设置）
    user = getattr(request.state, "user", None)
    
    if user:
        # 优先级1：从Token中获取tenant_id（已认证用户）
        tenant_id = user.get("tenant_id")
        
        # 如果是平台管理员（tenant_id为null或"platform"），跳过租户设置
        if tenant_id in (None, "platform", ""):
            request.state.is_platform_admin = True
            response = await call_next(request)
            return response
    
    # 优先级2：从Header中获取X-Tenant-Id
    if not tenant_id:
        tenant_id = request.headers.get("X-Tenant-Id")
    
    # 优先级3：从Header中获取X-Tenant-Code，根据代码查找租户
    # 注意：在中间件中无法直接访问db会话，这里暂时跳过
    # 租户代码查找应该在API路由中处理（通过依赖注入的db会话）
    if not tenant_id:
        tenant_code = request.headers.get("X-Tenant-Code")
        if tenant_code:
            # 将tenant_code存储到state中，供API路由使用
            request.state.tenant_code = tenant_code
            logger.warning(f"租户代码查找需要在API路由中处理: {tenant_code}")
    
    # 优先级4：从域名识别租户
    # 注意：在中间件中无法直接访问db会话，这里暂时跳过
    # 域名识别应该在API路由中处理（通过依赖注入的db会话）
    if not tenant_id:
        host = request.headers.get("Host", "")
        if host:
            # 提取子域名（假设格式：{code}.his.example.com）
            parts = host.split(".")
            if len(parts) >= 3 and parts[1] == "his":  # 子域名格式
                tenant_code = parts[0]
                # 将tenant_code存储到state中，供API路由使用
                request.state.tenant_code = tenant_code
                logger.warning(f"域名识别需要在API路由中处理: {host}")
    
    # 设置租户ID到请求状态
    if tenant_id:
        request.state.tenant_id = tenant_id
    else:
        logger.warning(f"请求缺少tenant_id: {request.url.path}, Host: {request.headers.get('Host')}")
    
    response = await call_next(request)
    return response


def get_tenant_id(request: Request) -> Optional[str]:
    """
    从请求中获取租户ID
    
    Args:
        request: 请求对象
    
    Returns:
        Optional[str]: 租户ID，不存在返回None
    """
    return getattr(request.state, "tenant_id", None)


def require_tenant_id(request: Request) -> str:
    """
    要求请求必须包含租户ID
    
    Args:
        request: 请求对象
    
    Returns:
        str: 租户ID
    
    Raises:
        BusinessException: 租户ID不存在
    """
    tenant_id = get_tenant_id(request)
    if not tenant_id:
        raise BusinessException("租户ID不存在", code=400)
    return tenant_id

