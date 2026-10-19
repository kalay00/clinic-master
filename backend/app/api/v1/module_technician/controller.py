"""
技师模块 路由
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from uuid import UUID
from app.core.dependencies import AuthPermission, get_current_user
from app.core.base_schema import AuthSchema
from app.common.response import SuccessResponse
from .service import TechnicianService
from .schema import TechnicianCreateSchema, TechnicianUpdateSchema

router = APIRouter(tags=["技师管理"])


@router.get("", summary="技师列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["technician:list"]))])
async def list_technicians(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    return SuccessResponse(data=await TechnicianService(auth).list_technicians(page, page_size, keyword, status))


@router.post("", summary="新增技师", response_model=None, dependencies=[Depends(AuthPermission(permission=["technician:create"]))])
async def create_technician(data: TechnicianCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await TechnicianService(auth).create(data))


@router.put("/{tech_id}", summary="编辑技师", response_model=None, dependencies=[Depends(AuthPermission(permission=["technician:update"]))])
async def update_technician(tech_id: UUID, data: TechnicianUpdateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await TechnicianService(auth).update(tech_id, data))


@router.delete("", summary="删除技师", response_model=None, dependencies=[Depends(AuthPermission(permission=["technician:delete"]))])
async def delete_technician(tech_ids: List[UUID], auth: AuthSchema = Depends(get_current_user)):
    await TechnicianService(auth).delete(tech_ids)
    return SuccessResponse(message="删除成功")
