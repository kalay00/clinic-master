"""
认证API路由
"""
from typing import Optional
from datetime import timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.middleware.tenant import get_tenant_id
from app.services.user_service import UserService
from app.services.user_tenant_service import UserTenantService
from app.core.response import success_response, error_response
from app.core.exceptions import UnauthorizedException, NotFoundException, BusinessException
from app.core.security import verify_password, create_access_token
from app.core.logger import logger
from app.repositories.user_repository import UserRepository
from app.api.v1.module_user.model import User

router = APIRouter()


class LoginRequest(BaseModel):
    """
    登录请求
    
    Attributes:
        username: 用户名
        password: 密码
        tenant_id: 租户ID（可选，如果提供则直接使用）
        tenant_code: 租户代码（可选，如果提供则根据代码查找租户）
    """
    username: str
    password: str
    tenant_id: Optional[str] = None
    tenant_code: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str


class SwitchTenantRequest(BaseModel):
    """切换租户请求"""
    tenant_id: str


@router.post(
    "/login",
    summary="用户登录",
    description="用户登录接口，验证用户名和密码，返回访问令牌和用户信息",
    response_description="登录成功返回访问令牌、刷新令牌和用户信息",
    tags=["认证"]
)
async def login(
    request_body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    验证用户凭据，生成JWT访问令牌和刷新令牌。
    
    **请求示例**:
    ```json
    {
        "username": "admin",
        "password": "password123",
        "tenant_id": "default"
    }
    ```
    
    **响应示例**:
    ```json
    {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "bearer",
            "user": {
                "id": "uuid",
                "username": "admin",
                "real_name": "管理员",
                "email": "admin@example.com",
                "permissions": ["user:read", "user:write"]
            }
        }
    }
    ```
    
    Args:
        request_body: 登录请求体，包含用户名、密码和租户ID
        request: FastAPI请求对象
        db: 数据库会话
    
    Returns:
        JSONResponse: 包含访问令牌、刷新令牌和用户信息的响应
    
    Raises:
        UnauthorizedException: 用户名或密码错误
    """
    try:
        service = UserService(db)
        client_ip = request.client.host if request.client else "unknown"
        
        # 如果提供了tenant_code，根据代码查找租户ID
        tenant_id = request_body.tenant_id
        if not tenant_id and request_body.tenant_code:
            try:
                from app.api.v1.module_tenant.model import Tenant
                # 直接使用传入的db会话查询，而不是创建新的服务
                tenant = db.query(Tenant).filter(
                    Tenant.code == request_body.tenant_code,
                    Tenant.deleted_at.is_(None),
                    Tenant.status == "active"
                ).first()
                
                if not tenant:
                    return error_response(
                        message=f"租户代码不存在: {request_body.tenant_code}",
                        code=404
                    )
                tenant_id = str(tenant.id)
            except Exception as e:
                logger.error(f"查找租户失败: {str(e)}", exc_info=True)
                return error_response(
                    message="查找租户失败",
                    code=500
                )
        
        # 如果都没有提供，尝试从请求中获取（域名或Header）
        if not tenant_id:
            from app.core.middleware.tenant import get_tenant_id
            tenant_id = get_tenant_id(request)
        
        # 如果都没有提供租户信息，尝试根据用户名查找用户所属的租户
        if not tenant_id:
            # 先验证用户名和密码（不指定租户）
            from app.repositories.user_repository import UserRepository
            user_repo = UserRepository(db)
            
            # 查找用户（可能属于多个租户）
            # 注意：get_users_by_username可能不存在，使用直接查询
            users = db.query(User).filter(
                User.username == request_body.username,
                User.deleted_at.is_(None)
            ).all()
            
            if not users:
                return error_response(
                    message="用户名或密码错误",
                    code=401
                )
            
            # 验证密码（使用第一个用户）
            first_user = users[0]
            if not verify_password(request_body.password, first_user.password_hash):
                return error_response(
                    message="用户名或密码错误",
                    code=401
                )
            
            # 获取用户所属的所有租户
            from app.services.user_tenant_service import UserTenantService
            user_tenant_service = UserTenantService(db)
            try:
                user_tenants = user_tenant_service.get_user_tenants(str(first_user.id))
            except Exception as e:
                logger.error(f"获取用户租户列表失败: {str(e)}", exc_info=True)
                # 如果获取租户列表失败，尝试使用用户的tenant_id（如果存在）
                if first_user.tenant_id:
                    tenant_id = str(first_user.tenant_id)
                else:
                    return error_response(
                        message="获取用户租户信息失败，请提供租户ID或租户代码",
                        code=500
                    )
                user_tenants = []
            
            # 如果用户只属于一个租户，直接使用
            if len(user_tenants) == 1:
                tenant_id = str(user_tenants[0]["id"])
            elif len(user_tenants) > 1:
                # 用户属于多个租户，返回租户列表让用户选择
                # 下发短期临时 token，供切换租户接口识别用户（此时尚未选定租户）
                temp_token = create_access_token(
                    {
                        "user_id": str(first_user.id),
                        "username": first_user.username,
                        "temp": True,
                    },
                    expires_delta=timedelta(minutes=10),
                )
                return success_response(data={
                    "requires_tenant_selection": True,
                    "user_id": str(first_user.id),
                    "temp_token": temp_token,
                    "tenants": user_tenants,
                    "message": "请选择要登录的租户"
                }, message="需要选择租户")
            else:
                # 用户不属于任何租户，使用传统方式（根据tenant_id查找）
                return error_response(
                    message="请提供租户ID或租户代码",
                    code=400
                )
        
        # 确保tenant_id是字符串格式
        if tenant_id and not isinstance(tenant_id, str):
            tenant_id = str(tenant_id)
        
        if not tenant_id:
            return error_response(
                message="请提供租户ID或租户代码",
                code=400
            )
        
        result = service.login(
            username=request_body.username,
            password=request_body.password,
            tenant_id=tenant_id,
            request_ip=client_ip
        )
        
        return success_response(data=result, message="登录成功")
    except UnauthorizedException as e:
        logger.warning(f"登录失败（认证错误）: {str(e)}")
        return error_response(message=str(e), code=401)
    except BusinessException as e:
        logger.warning(f"登录失败（业务错误）: {str(e)}")
        return error_response(message=str(e), code=e.code if hasattr(e, 'code') else 400)
    except Exception as e:
        logger.error(f"登录失败（服务器错误）: {str(e)}", exc_info=True)
        # 返回更详细的错误信息用于调试
        error_msg = str(e)
        if "user_tenants" in error_msg.lower():
            error_msg = "用户租户关联表查询失败，请检查数据库"
        elif "tenant" in error_msg.lower():
            error_msg = "租户信息查询失败"
        return error_response(message=f"登录失败: {error_msg}", code=500)


@router.post(
    "/logout",
    summary="用户登出",
    description="用户登出接口，清除服务器端的令牌缓存",
    response_description="登出成功响应",
    tags=["认证"]
)
async def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户登出
    
    清除服务器端的令牌缓存，使令牌失效。
    
    **注意**: 需要提供有效的JWT令牌在请求头中。
    
    **响应示例**:
    ```json
    {
        "code": 200,
        "message": "登出成功",
        "data": null
    }
    ```
    
    Args:
        request: FastAPI请求对象（自动提取JWT令牌）
        db: 数据库会话
    
    Returns:
        JSONResponse: 登出成功响应
    """
    try:
        from app.core.middleware.auth import get_current_user
        
        user = get_current_user(request)
        user_id = user.get("user_id")
        tenant_id = user.get("tenant_id")
        
        service = UserService(db)
        service.logout(user_id, tenant_id)
        
        return success_response(message="登出成功")
    except Exception as e:
        return error_response(message="登出失败", code=500)


@router.post(
    "/refresh",
    summary="刷新访问令牌",
    description="使用刷新令牌获取新的访问令牌",
    response_description="返回新的访问令牌和刷新令牌",
    tags=["认证"]
)
async def refresh_token(
    request_body: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    使用有效的刷新令牌获取新的访问令牌。
    
    **请求示例**:
    ```json
    {
        "refresh_token": "eyJ..."
    }
    ```
    
    **响应示例**:
    ```json
    {
        "code": 200,
        "message": "Token刷新成功",
        "data": {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "bearer"
        }
    }
    ```
    
    Args:
        request_body: 刷新令牌请求体，包含refresh_token
        db: 数据库会话
    
    Returns:
        JSONResponse: 包含新访问令牌和刷新令牌的响应
    
    Raises:
        UnauthorizedException: 刷新令牌无效或已过期
    """
    try:
        service = UserService(db)
        result = service.refresh_token(request_body.refresh_token)
        
        return success_response(data=result, message="Token刷新成功")
    except UnauthorizedException as e:
        return error_response(message=str(e), code=401)
    except Exception as e:
        return error_response(message="Token刷新失败", code=500)


@router.get("/tenants")
async def get_user_tenants(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    获取当前用户所属的所有租户列表
    
    用于用户登录后选择租户（如果用户属于多个租户）
    """
    try:
        from app.core.middleware.auth import get_current_user_id
        user_id = get_current_user_id(request)
        
        service = UserTenantService(db)
        tenants = service.get_user_tenants(user_id)
        
        return success_response(data={"tenants": tenants})
    except Exception as e:
        return error_response(message=f"获取租户列表失败: {str(e)}", code=500)


@router.post("/switch-tenant")
async def switch_tenant(
    request_body: SwitchTenantRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    切换租户
    
    用户切换当前使用的租户，重新生成Token
    """
    try:
        from app.core.middleware.auth import get_current_user
        from app.core.security import create_access_token, create_refresh_token
        from app.services.user_service import UserService
        from app.services.user_tenant_service import UserTenantService
        
        user = get_current_user(request)
        user_id = user.get("user_id")
        
        # 验证用户是否属于该租户
        user_tenant_service = UserTenantService(db)
        user_tenants = user_tenant_service.get_user_tenants(user_id)
        
        tenant_ids = [t["id"] for t in user_tenants]
        if request_body.tenant_id not in tenant_ids:
            return error_response(
                message="用户不属于该租户",
                code=403
            )
        
        # 更新最后访问时间
        user_tenant_service.update_last_accessed(user_id, request_body.tenant_id)
        
        # 重新生成Token
        user_service = UserService(db)
        # 用户可能属于多个租户，User.tenant_id 仅记录其主租户；
        # 切换时按 user_id 取用户（不限定租户），并把当前租户更新为所选租户，
        # 以保证后续 /auth/me 等按 tenant_id 过滤的查询能用新租户命中。
        user_obj = db.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).first()
        if not user_obj:
            return error_response(message="用户不存在", code=404)

        if str(user_obj.tenant_id) != str(request_body.tenant_id):
            user_obj.tenant_id = request_body.tenant_id
            db.commit()
        
        # 获取用户权限
        permissions = user_service.get_user_permissions(user_id, request_body.tenant_id)
        permission_codes = [p.code for p in permissions]
        
        token_data = {
            "user_id": str(user_obj.id),
            "tenant_id": request_body.tenant_id,
            "username": user_obj.username,
            "permissions": permission_codes
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return success_response(data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "tenant_id": request_body.tenant_id,
        }, message="切换租户成功")
    except UnauthorizedException as e:
        logger.warning(f"切换租户失败（未授权）: {str(e)}")
        return error_response(message="登录已失效，请重新登录", code=401)
    except NotFoundException as e:
        logger.warning(f"切换租户失败（资源不存在）: {str(e)}")
        return error_response(message=str(e), code=404)
    except Exception as e:
        logger.error(f"切换租户失败（服务器错误）: {str(e)}", exc_info=True)
        return error_response(message=f"切换租户失败: {str(e)}", code=500)


@router.get("/me")
async def get_current_user_info(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    
    返回当前登录用户的信息，包括所属租户列表
    """
    try:
        from app.core.middleware.auth import get_current_user, get_current_user_id
        from app.services.user_tenant_service import UserTenantService
        from app.core.exceptions import UnauthorizedException
        from app.core.logger import logger
        
        try:
            user = get_current_user(request)
            user_id = get_current_user_id(request)
        except UnauthorizedException as e:
            logger.warning(f"获取用户信息失败（未授权）: {str(e)}")
            return error_response(message="未授权访问，请先登录", code=401)
        except Exception as e:
            logger.error(f"获取用户信息失败（认证错误）: {str(e)}", exc_info=True)
            return error_response(message=f"认证失败: {str(e)}", code=401)
        
        tenant_id = user.get("tenant_id")
        
        # 获取用户所属的所有租户
        user_tenants = []
        try:
            user_tenant_service = UserTenantService(db)
            user_tenants = user_tenant_service.get_user_tenants(user_id)
        except Exception as e:
            logger.warning(f"获取用户租户列表失败: {str(e)}")
            # 如果获取租户列表失败，继续处理，但不返回租户列表
        
        # 获取用户详细信息
        user_service = UserService(db)
        if tenant_id and tenant_id != "platform":
            try:
                user_obj = user_service.get_user(user_id, tenant_id)
                if not user_obj:
                    logger.error(f"用户不存在: user_id={user_id}, tenant_id={tenant_id}")
                    return error_response(message="用户不存在", code=404)
                
                # 电话（明文存储，直接返回）
                phone_decrypted = user_obj.phone
                
                # 获取用户角色信息
                roles = []
                if hasattr(user_obj, 'roles') and user_obj.roles:
                    roles = [{"id": str(r.id), "name": r.name, "code": r.code} for r in user_obj.roles]
                
                # 获取用户权限信息
                from app.repositories.user_repository import PermissionRepository
                permission_repo = PermissionRepository(db)
                permissions = permission_repo.get_user_permissions(str(user_obj.id), tenant_id)
                permission_codes = [p.code for p in permissions]

                user_info = {
                    "id": str(user_obj.id),
                    "username": user_obj.username,
                    "name": user_obj.real_name or user_obj.username,  # 兼容前端
                    "real_name": user_obj.real_name,
                    "phone": phone_decrypted,
                    "email": user_obj.email,
                    "tenant_id": str(tenant_id) if tenant_id else None,
                    "tenants": user_tenants,
                    "roles": roles,
                    "permissions": permission_codes,
                    "is_platform_admin": False,
                }
            except Exception as e:
                logger.error(f"获取用户详细信息失败: {str(e)}", exc_info=True)
                return error_response(message=f"获取用户详细信息失败: {str(e)}", code=500)
        else:
            # 平台管理员
            try:
                from app.services.platform_admin_service import PlatformAdminService
                platform_service = PlatformAdminService(db)
                admin = platform_service.get_platform_admin(user_id)
                if not admin:
                    logger.error(f"平台管理员不存在: user_id={user_id}")
                    return error_response(message="用户不存在", code=404)
                
                user_info = {
                    "id": str(admin.id),
                    "username": admin.username,
                    "name": admin.real_name or admin.username,  # 兼容前端
                    "real_name": admin.real_name,
                    "email": admin.email,
                    "tenant_id": None,
                    "tenants": user_tenants,
                    "roles": [],
                    "is_platform_admin": True,
                }
            except Exception as e:
                logger.error(f"获取平台管理员信息失败: {str(e)}", exc_info=True)
                return error_response(message=f"获取平台管理员信息失败: {str(e)}", code=500)
        
        return success_response(data=user_info)
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"获取用户信息失败（未知错误）: {str(e)}", exc_info=True)
        return error_response(message=f"获取用户信息失败: {str(e)}", code=500)


class UpdateProfileRequest(BaseModel):
    """
    更新个人资料请求
    
    Attributes:
        real_name: 真实姓名（可选）
        phone: 手机号（可选）
        email: 邮箱（可选）
        password: 新密码（可选）
    """
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


@router.put("/me")
async def update_current_user_info(
    request_body: UpdateProfileRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    
    允许用户更新自己的个人信息，包括姓名、电话、邮箱和密码。
    
    **请求示例**:
    ```json
    {
        "real_name": "更新后的姓名",
        "phone": "13800138000",
        "email": "newemail@example.com",
        "password": "newpassword123"
    }
    ```
    
    **响应示例**:
    ```json
    {
        "code": 200,
        "message": "更新成功",
        "data": {
            "id": "uuid",
            "username": "user",
            "real_name": "更新后的姓名",
            "email": "newemail@example.com"
        }
    }
    ```
    """
    try:
        from app.core.middleware.auth import get_current_user, get_current_user_id
        from app.services.platform_admin_service import PlatformAdminService
        
        user = get_current_user(request)
        user_id = get_current_user_id(request)
        tenant_id = user.get("tenant_id")
        
        # 准备更新数据
        update_data = request_body.dict(exclude_unset=True)
        
        # 如果是平台管理员
        if not tenant_id or tenant_id == "platform":
            platform_service = PlatformAdminService(db)
            admin = platform_service.get_platform_admin(user_id)
            if not admin:
                return error_response(message="用户不存在", code=404)
            
            # 更新平台管理员信息
            if "real_name" in update_data:
                admin.real_name = update_data["real_name"]
            if "email" in update_data:
                admin.email = update_data["email"]
            if "password" in update_data:
                from app.core.security import get_password_hash
                admin.password_hash = get_password_hash(update_data["password"])
            
            db.commit()
            db.refresh(admin)
            
            return success_response(data={
                "id": str(admin.id),
                "username": admin.username,
                "real_name": admin.real_name,
                "email": admin.email,
                "is_platform_admin": True,
            })
        else:
            # 普通租户用户
            user_service = UserService(db)
            user_obj = user_service.get_user(user_id, tenant_id)
            
            # 更新用户信息
            user_obj = user_service.update_user(
                user_id=user_id,
                tenant_id=tenant_id,
                user_data=update_data,
                updater_id=user_id  # 自己更新自己
            )
            
            # 电话为明文存储，直接返回
            return success_response(data={
                "id": str(user_obj.id),
                "username": user_obj.username,
                "real_name": user_obj.real_name,
                "phone": user_obj.phone,
                "email": user_obj.email,
                "is_platform_admin": False,
            })
            
    except NotFoundException as e:
        return error_response(message=str(e), code=404)
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"更新用户信息失败: {str(e)}", exc_info=True)
        return error_response(message=f"更新用户信息失败: {str(e)}", code=400)


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str


@router.post("/change-password", summary="修改当前用户密码")
async def change_current_user_password(
    request_body: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """校验原密码后修改当前登录用户的密码。"""
    try:
        from app.core.middleware.auth import get_current_user, get_current_user_id
        from app.core.security import get_password_hash
        from app.services.platform_admin_service import PlatformAdminService

        user = get_current_user(request)
        user_id = get_current_user_id(request)
        tenant_id = user.get("tenant_id")

        old_password = (request_body.old_password or "").strip()
        new_password = (request_body.new_password or "").strip()
        if not old_password or not new_password:
            return error_response(message="原密码和新密码不能为空", code=400)
        if len(new_password) < 6:
            return error_response(message="新密码长度不能少于6位", code=400)
        if old_password == new_password:
            return error_response(message="新密码不能与原密码相同", code=400)

        if not tenant_id or tenant_id == "platform":
            platform_service = PlatformAdminService(db)
            admin = platform_service.get_platform_admin(user_id)
            if not admin:
                return error_response(message="用户不存在", code=404)
            if not verify_password(old_password, admin.password_hash):
                return error_response(message="原密码不正确", code=400)
            admin.password_hash = get_password_hash(new_password)
            db.commit()
            return success_response(message="密码修改成功", data={"id": str(admin.id)})

        user_service = UserService(db)
        user_obj = user_service.get_user(user_id, tenant_id)
        if not user_obj:
            return error_response(message="用户不存在", code=404)
        if not verify_password(old_password, user_obj.password_hash):
            return error_response(message="原密码不正确", code=400)

        user_service.update_user(
            user_id=user_id,
            tenant_id=tenant_id,
            user_data={"password": new_password},
            updater_id=user_id,
        )
        return success_response(message="密码修改成功", data={"id": str(user_id)})

    except NotFoundException as e:
        return error_response(message=str(e), code=404)
    except Exception as e:
        from app.core.logger import logger
        logger.error(f"修改密码失败: {str(e)}", exc_info=True)
        return error_response(message=f"修改密码失败: {str(e)}", code=400)

