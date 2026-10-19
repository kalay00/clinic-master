"""
控制器（平台管理，已迁移业务逻辑至 service.py）
"""
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, Query, Body, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.common.response import SuccessResponse, ErrorResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException, UnauthorizedException, BusinessException
from app.core.database import get_db
from app.core.logger import logger
from app.services.platform_admin_service import PlatformAdminService
from .model import PlatformAdmin
from .schema import PlatformAdminSchema, PlatformAdminCreateSchema, PlatformAdminUpdateSchema
from .param import PlatformQueryParam
from .service import PlatformService


router = APIRouter()


class PlatformLoginRequest(BaseModel):
    """平台管理员登录请求"""
    username: str
    password: str


@router.post("/login", summary="平台管理员登录")
async def platform_login(
    request_body: PlatformLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """平台管理员登录，验证用户名和密码，返回访问令牌和用户信息"""
    try:
        service = PlatformAdminService(db)
        client_ip = request.client.host if request.client else "unknown"
        result = service.login(
            username=request_body.username,
            password=request_body.password,
            request_ip=client_ip,
        )
        return SuccessResponse(data=result, msg="登录成功")
    except (UnauthorizedException, BusinessException) as e:
        code = getattr(e, "code", 401) or 401
        status_code = code if code in (401, 403, 404) else 400
        return ErrorResponse(msg=str(e), code=code, status_code=status_code)
    except Exception as e:
        logger.error(f"平台管理员登录失败: {str(e)}", exc_info=True)
        return ErrorResponse(msg=f"登录失败: {str(e)}", code=500, status_code=500)


# ── 平台管理员 CRUD ──
@router.get("/admins", summary="平台管理员列表", dependencies=[Depends(AuthPermission(permission=["platform:list"]))])
async def list_admins(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序")):
    params = PlatformQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await PlatformService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("/admins", summary="创建平台管理员", dependencies=[Depends(AuthPermission(permission=["platform:create"]))])
async def create_admin(data: PlatformAdminCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    result = await PlatformService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/admins/{id}", summary="平台管理员详情", dependencies=[Depends(AuthPermission(permission=["platform:get"]))])
async def get_admin(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await PlatformService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/admins/{id}", summary="更新平台管理员", dependencies=[Depends(AuthPermission(permission=["platform:update"]))])
async def update_admin(id: str, data: PlatformAdminUpdateSchema, auth: AuthSchema = Depends(get_current_user)):
    result = await PlatformService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/admins/{id}", summary="删除平台管理员", dependencies=[Depends(AuthPermission(permission=["platform:delete"]))])
async def delete_admin(id: str, auth: AuthSchema = Depends(get_current_user)):
    await PlatformService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


# ── 平台级业务 ──
@router.get("/statistics", summary="平台统计")
async def statistics(auth: AuthSchema = Depends(get_current_user)):
    data = await PlatformService(auth).get_platform_statistics()
    return SuccessResponse(data=data, msg="查询成功")


@router.get("/audit-logs", summary="审计日志列表（跨租户）")
async def list_audit_logs(
    auth: AuthSchema = Depends(get_current_user),
    tenant_id: Optional[str] = Query(None, description="租户ID"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    resource_type: Optional[str] = Query(None, description="资源类型"),
    operation_type: Optional[str] = Query(None, description="操作类型（对应 audit_type）"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    skip: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(20, ge=1, le=100, description="每页数量")):
    items, total = await PlatformService(auth).list_audit_logs(
        tenant_id=tenant_id, user_id=user_id, resource_type=resource_type,
        operation_type=operation_type, start_date=start_date, end_date=end_date,
        skip=skip, limit=limit,
    )
    total_pages = (total + limit - 1) // limit if limit else 1
    return SuccessResponse(
        data={
            "items": items,
            "pagination": {"total": total, "page": skip // limit + 1 if limit else 1, "page_size": limit, "total_pages": total_pages},
        },
        msg="查询成功",
    )


@router.get("/tenants", summary="租户列表（跨租户）")
async def list_tenants(
    auth: AuthSchema = Depends(get_current_user),
    search: Optional[str] = Query(None, description="搜索（名称/编码）"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")):
    items, total = await PlatformService(auth).list_tenants(
        search=search, status=status, skip=(page - 1) * page_size, limit=page_size
    )
    return SuccessResponse(data={"items": items, "total": total, "page_no": page, "page_size": page_size}, msg="查询成功")


@router.get("/tenants/{tenant_id}", summary="租户详情")
async def get_tenant(tenant_id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await PlatformService(auth).get_tenant(tenant_id)
    return SuccessResponse(data=result, msg="查询成功")


@router.post("/tenants", summary="创建租户（含管理员账号）")
async def create_tenant(data: Dict[str, Any] = Body(..., description="租户数据"), auth: AuthSchema = Depends(get_current_user)):
    result = await PlatformService(auth).create_tenant(data, creator_id=str(auth.user.id))
    return SuccessResponse(data=result, msg="创建成功")


@router.put("/tenants/{tenant_id}", summary="更新租户")
async def update_tenant(tenant_id: str, data: Dict[str, Any] = Body(..., description="租户数据"), auth: AuthSchema = Depends(get_current_user)):
    result = await PlatformService(auth).update_tenant(tenant_id, data, updater_id=str(auth.user.id))
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/tenants/{tenant_id}", summary="删除租户")
async def delete_tenant(tenant_id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await PlatformService(auth).delete_tenant(tenant_id, deleter_id=str(auth.user.id))
    return SuccessResponse(data={"ok": result}, msg="删除成功")


@router.put("/tenants/{tenant_id}/admin-password", summary="修改租户管理员密码")
async def update_tenant_admin_password(
    tenant_id: str, new_password: str = Body(..., embed=True, description="新密码"),
    auth: AuthSchema = Depends(get_current_user)):
    result = await PlatformService(auth).update_tenant_admin_password(tenant_id, new_password, updater_id=str(auth.user.id))
    return SuccessResponse(data={"ok": result}, msg="修改成功")


@router.put("/password", summary="修改平台管理员自身密码")
async def change_password(
    old_password: str = Body(..., embed=True, description="旧密码"),
    new_password: str = Body(..., embed=True, description="新密码"),
    auth: AuthSchema = Depends(get_current_user)):
    if not auth.user:
        raise CustomException(msg="未认证", code=401, status_code=401)
    result = await PlatformService(auth).change_password(str(auth.user.id), old_password, new_password)
    return SuccessResponse(data={"ok": result}, msg="修改成功")
