"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import Role
from .schema import RoleSchema, RoleCreateSchema, RoleUpdateSchema
from .param import RoleQueryParam
from .service import RoleService


router = APIRouter()


@router.get("", summary="获取角色列表", dependencies=[Depends(AuthPermission(permission=["role:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序")):
    params = RoleQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await RoleService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建角色", dependencies=[Depends(AuthPermission(permission=["role:create"]))])
async def create_(
    data: RoleCreateSchema,
    auth: AuthSchema = Depends(get_current_user)):
    result = await RoleService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取角色详情", dependencies=[Depends(AuthPermission(permission=["role:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user)):
    result = await RoleService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新角色", dependencies=[Depends(AuthPermission(permission=["role:update"]))])
async def update_(
    id: str,
    data: RoleUpdateSchema,
    auth: AuthSchema = Depends(get_current_user)):
    result = await RoleService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除角色", dependencies=[Depends(AuthPermission(permission=["role:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user)):
    await RoleService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


@router.get("/{id}/permissions", summary="获取角色权限")
async def role_permissions(id: str, auth: AuthSchema = Depends(get_current_user)):
    data = await RoleService(auth).get_permissions(id)
    return SuccessResponse(data=data, msg="查询成功")


@router.post("/{id}/permissions/{permission_id}", summary="为角色分配权限")
async def assign_permission(id: str, permission_id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await RoleService(auth).assign_permission(id, permission_id)
    return SuccessResponse(data={"ok": result}, msg="分配成功")


@router.delete("/{id}/permissions/{permission_id}", summary="撤销角色权限")
async def revoke_permission(id: str, permission_id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await RoleService(auth).revoke_permission(id, permission_id)
    return SuccessResponse(data={"ok": result}, msg="撤销成功")
