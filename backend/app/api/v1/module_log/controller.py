"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import OperationLog
from .schema import OperationLogSchema, OperationLogCreateSchema, OperationLogUpdateSchema
from .param import LogQueryParam
from .service import LogService


router = APIRouter()


@router.get("", summary="获取操作日志列表", dependencies=[Depends(AuthPermission(permission=["log:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
):
    params = LogQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await LogService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建操作日志", dependencies=[Depends(AuthPermission(permission=["log:create"]))])
async def create_(
    data: OperationLogCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await LogService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取操作日志详情", dependencies=[Depends(AuthPermission(permission=["log:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await LogService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新操作日志", dependencies=[Depends(AuthPermission(permission=["log:update"]))])
async def update_(
    id: str,
    data: OperationLogUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await LogService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除操作日志", dependencies=[Depends(AuthPermission(permission=["log:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await LogService(auth).delete(id)
    return SuccessResponse(msg="删除成功")
