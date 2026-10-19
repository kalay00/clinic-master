"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, Query, Body

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import Tenant
from .schema import TenantSchema, TenantCreateSchema, TenantUpdateSchema, TenantCurrentUpdateSchema
from .param import TenantQueryParam
from .service import TenantService


router = APIRouter()


@router.get("", summary="获取租户配置列表", dependencies=[Depends(AuthPermission(permission=["tenant:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序")):
    params = TenantQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await TenantService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建租户配置", dependencies=[Depends(AuthPermission(permission=["tenant:create"]))])
async def create_(
    data: TenantCreateSchema,
    auth: AuthSchema = Depends(get_current_user)):
    result = await TenantService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


# ── 具体路由（必须在 /{id} 之前，避免被路径参数抢匹配）──
@router.get("/config/defaults", summary="获取默认租户配置")
async def config_defaults(auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=TenantService(auth).get_default_config(), msg="查询成功")


@router.get("/config", summary="获取当前租户配置（合并默认）")
async def get_current_config(auth: AuthSchema = Depends(get_current_user)):
    data = await TenantService(auth).get_tenant_config(auth.tenant_id)
    return SuccessResponse(data=data, msg="查询成功")


@router.put("/config", summary="更新当前租户配置")
async def update_current_config(
    config_updates: Dict[str, Any] = Body(..., description="配置更新项（与现有配置合并）"),
    auth: AuthSchema = Depends(get_current_user)):
    data = await TenantService(auth).update_tenant_config(auth.tenant_id, config_updates)
    return SuccessResponse(data=data, msg="配置已更新")


@router.get("/current", summary="获取当前诊所信息")
async def get_current_tenant(auth: AuthSchema = Depends(get_current_user)):
    data = await TenantService(auth).get_current(auth.tenant_id)
    return SuccessResponse(data=data, msg="查询成功")


@router.put("/current", summary="更新当前诊所信息")
async def update_current_tenant(
    data: TenantCurrentUpdateSchema,
    auth: AuthSchema = Depends(get_current_user)):
    result = await TenantService(auth).update_current(auth.tenant_id, data)
    return SuccessResponse(data=result, msg="诊所信息已更新")


@router.get("/pharmacist-review-enabled", summary="药师审核开关是否启用")
async def pharmacist_review(
    tenant_id: str = Query(..., description="租户ID"),
    auth: AuthSchema = Depends(get_current_user)):
    enabled = await TenantService(auth).is_pharmacist_review_enabled(tenant_id)
    return SuccessResponse(data={"enabled": enabled}, msg="查询成功")


@router.get("/by-code/{code}", summary="按编码查询租户")
async def by_code(code: str, auth: AuthSchema = Depends(get_current_user)):
    result = await TenantService(auth).get_tenant_by_code(code)
    return SuccessResponse(data=result, msg="查询成功")


@router.get("/by-domain/{domain}", summary="按域名查询租户")
async def by_domain(domain: str, auth: AuthSchema = Depends(get_current_user)):
    result = await TenantService(auth).get_tenant_by_domain(domain)
    return SuccessResponse(data=result, msg="查询成功")


@router.get("/{id}", summary="获取租户配置详情", dependencies=[Depends(AuthPermission(permission=["tenant:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user)):
    result = await TenantService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新租户配置", dependencies=[Depends(AuthPermission(permission=["tenant:update"]))])
async def update_(
    id: str,
    data: TenantUpdateSchema,
    auth: AuthSchema = Depends(get_current_user)):
    result = await TenantService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除租户配置", dependencies=[Depends(AuthPermission(permission=["tenant:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user)):
    await TenantService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


@router.get("/{id}/config", summary="获取租户配置（合并默认）")
async def get_config(id: str, auth: AuthSchema = Depends(get_current_user)):
    data = await TenantService(auth).get_tenant_config(id)
    return SuccessResponse(data=data, msg="查询成功")


@router.put("/{id}/config", summary="更新租户配置")
async def update_config(
    id: str,
    config_updates: Dict[str, Any] = Body(..., description="配置更新项"),
    auth: AuthSchema = Depends(get_current_user)):
    data = await TenantService(auth).update_tenant_config(id, config_updates)
    return SuccessResponse(data=data, msg="更新成功")
