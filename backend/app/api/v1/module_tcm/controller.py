"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import TCMTreatment
from .schema import TCMTreatmentSchema, TCMTreatmentCreateSchema, TCMTreatmentUpdateSchema
from .param import TcmQueryParam
from .service import TCMService


router = APIRouter()


@router.get("", summary="获取中医列表", dependencies=[Depends(AuthPermission(permission=["tcm:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
):
    params = TcmQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await TCMService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建中医", dependencies=[Depends(AuthPermission(permission=["tcm:create"]))])
async def create_(
    data: TCMTreatmentCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TCMService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取中医详情", dependencies=[Depends(AuthPermission(permission=["tcm:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TCMService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新中医", dependencies=[Depends(AuthPermission(permission=["tcm:update"]))])
async def update_(
    id: str,
    data: TCMTreatmentUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TCMService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除中医", dependencies=[Depends(AuthPermission(permission=["tcm:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await TCMService(auth).delete(id)
    return SuccessResponse(msg="删除成功")
