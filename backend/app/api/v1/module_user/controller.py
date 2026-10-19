"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import User
from .schema import UserSchema, UserCreateSchema, UserUpdateSchema
from .param import UserQueryParam
from .service import UserService


router = APIRouter()


@router.get("", summary="获取用户列表", dependencies=[Depends(AuthPermission(permission=["user:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序")):
    params = UserQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await UserService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建用户", dependencies=[Depends(AuthPermission(permission=["user:create"]))])
async def create_(
    data: UserCreateSchema,
    auth: AuthSchema = Depends(get_current_user)):
    result = await UserService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取用户详情", dependencies=[Depends(AuthPermission(permission=["user:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user)):
    result = await UserService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新用户", dependencies=[Depends(AuthPermission(permission=["user:update"]))])
async def update_(
    id: str,
    data: UserUpdateSchema,
    auth: AuthSchema = Depends(get_current_user)):
    result = await UserService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除用户", dependencies=[Depends(AuthPermission(permission=["user:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user)):
    await UserService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


@router.get("/{id}/roles", summary="获取用户角色")
async def user_roles(id: str, auth: AuthSchema = Depends(get_current_user)):
    data = await UserService(auth).get_user_roles(id)
    return SuccessResponse(data=data, msg="查询成功")


@router.get("/{id}/permissions", summary="获取用户权限")
async def user_permissions(id: str, auth: AuthSchema = Depends(get_current_user)):
    data = await UserService(auth).get_user_permissions(id)
    return SuccessResponse(data=data, msg="查询成功")


@router.post("/{id}/roles/{role_id}", summary="为用户分配角色")
async def assign_role(id: str, role_id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await UserService(auth).assign_role(id, role_id)
    return SuccessResponse(data={"ok": result}, msg="分配成功")


@router.delete("/{id}/roles/{role_id}", summary="撤销用户角色")
async def revoke_role(id: str, role_id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await UserService(auth).revoke_role(id, role_id)
    return SuccessResponse(data={"ok": result}, msg="撤销成功")
