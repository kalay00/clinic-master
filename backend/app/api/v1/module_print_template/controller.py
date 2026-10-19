"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import PrintTemplate
from .schema import PrintTemplateSchema, PrintTemplateCreateSchema, PrintTemplateUpdateSchema
from .param import Print_templateQueryParam
from .service import Print_templateService


router = APIRouter()


@router.get("", summary="获取打印模板管理列表", dependencies=[Depends(AuthPermission(permission=["print_template:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
    type: Optional[str] = Query(None, description="模板类型：bill/prescription/medical_record"),
    name: Optional[str] = Query(None, description="模板名称"),
):
    params = Print_templateQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    search: dict = {}
    if type:
        search["type"] = type
    if name:
        search["name"] = name
    data = await Print_templateService(auth).list(params.page_no, params.page_size, params.order_by, search)
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建打印模板管理", dependencies=[Depends(AuthPermission(permission=["print_template:create"]))])
async def create_(
    data: PrintTemplateCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await Print_templateService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取打印模板管理详情", dependencies=[Depends(AuthPermission(permission=["print_template:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await Print_templateService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新打印模板管理", dependencies=[Depends(AuthPermission(permission=["print_template:update"]))])
async def update_(
    id: str,
    data: PrintTemplateUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await Print_templateService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除打印模板管理", dependencies=[Depends(AuthPermission(permission=["print_template:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await Print_templateService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


@router.post("/{id}/set-default", summary="设为默认模板", dependencies=[Depends(AuthPermission(permission=["print_template:update"]))])
async def set_default_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await Print_templateService(auth).set_default(id)
    return SuccessResponse(data=result, msg="设置成功")


@router.post("/{id}/duplicate", summary="复制模板", dependencies=[Depends(AuthPermission(permission=["print_template:create"]))])
async def duplicate_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
    new_name: Optional[str] = Query(None, description="新模板名称"),
):
    result = await Print_templateService(auth).duplicate(id, new_name)
    return SuccessResponse(data=result, msg="复制成功")
