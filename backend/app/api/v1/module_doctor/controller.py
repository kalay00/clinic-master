"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import Doctor
from .schema import DoctorSchema, DoctorCreateSchema, DoctorUpdateSchema
from .param import DoctorQueryParam
from .service import DoctorService


router = APIRouter()


@router.get("", summary="获取医生列表", dependencies=[Depends(AuthPermission(permission=["doctor:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=500, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
):
    params = DoctorQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await DoctorService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建医生", dependencies=[Depends(AuthPermission(permission=["doctor:create"]))])
async def create_(
    data: DoctorCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await DoctorService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取医生详情", dependencies=[Depends(AuthPermission(permission=["doctor:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await DoctorService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新医生", dependencies=[Depends(AuthPermission(permission=["doctor:update"]))])
async def update_(
    id: str,
    data: DoctorUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await DoctorService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除医生", dependencies=[Depends(AuthPermission(permission=["doctor:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await DoctorService(auth).delete(id)
    return SuccessResponse(msg="删除成功")
