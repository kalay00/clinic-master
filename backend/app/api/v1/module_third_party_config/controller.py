"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import ThirdPartyConfig
from .schema import ThirdPartyConfigSchema, ThirdPartyConfigCreateSchema, ThirdPartyConfigUpdateSchema
from .param import Third_party_configQueryParam
from .service import ThirdPartyConfigService


router = APIRouter()


@router.get("", summary="获取第三方服务配置列表", dependencies=[Depends(AuthPermission(permission=["third_party_config:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
):
    params = Third_party_configQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await ThirdPartyConfigService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建第三方服务配置", dependencies=[Depends(AuthPermission(permission=["third_party_config:create"]))])
async def create_(
    data: ThirdPartyConfigCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await ThirdPartyConfigService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取第三方服务配置详情", dependencies=[Depends(AuthPermission(permission=["third_party_config:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await ThirdPartyConfigService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新第三方服务配置", dependencies=[Depends(AuthPermission(permission=["third_party_config:update"]))])
async def update_(
    id: str,
    data: ThirdPartyConfigUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await ThirdPartyConfigService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除第三方服务配置", dependencies=[Depends(AuthPermission(permission=["third_party_config:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await ThirdPartyConfigService(auth).delete(id)
    return SuccessResponse(msg="删除成功")
