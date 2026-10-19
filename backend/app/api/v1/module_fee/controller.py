"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from .model import Fee
from .schema import FeeSchema, FeeCreateSchema, FeeUpdateSchema
from .param import FeeQueryParam
from .service import FeeService


router = APIRouter()


@router.get("", summary="获取费用设置列表", dependencies=[Depends(AuthPermission(permission=["fee:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    fee_type: Optional[str] = Query(None, description="费用类型"),
    name: Optional[str] = Query(None, description="费用名称"),
    status: Optional[bool] = Query(None, description="是否启用"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
):
    search: dict = {}
    if fee_type is not None:
        search["fee_type"] = fee_type
    if name:
        search["name"] = name
    if status is not None:
        search["status"] = status
    data = await FeeService(auth).list(page, page_size, order_by, search or None)
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建费用设置", dependencies=[Depends(AuthPermission(permission=["fee:create"]))])
async def create_(
    data: FeeCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await FeeService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取费用设置详情", dependencies=[Depends(AuthPermission(permission=["fee:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await FeeService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新费用设置", dependencies=[Depends(AuthPermission(permission=["fee:update"]))])
async def update_(
    id: str,
    data: FeeUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await FeeService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除费用设置", dependencies=[Depends(AuthPermission(permission=["fee:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await FeeService(auth).delete(id)
    return SuccessResponse(msg="删除成功")
