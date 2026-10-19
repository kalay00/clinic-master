"""
提成方案模块 路由
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from uuid import UUID
from app.core.dependencies import AuthPermission, get_current_user
from app.core.base_schema import AuthSchema
from app.common.response import SuccessResponse
from .service import CommissionPlanService
from .schema import CommissionPlanCreateSchema, CommissionPlanUpdateSchema

router = APIRouter(tags=["提成方案"])


@router.get("", summary="提成方案列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["commission:list"]))])
async def list_plans(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    return SuccessResponse(data=await CommissionPlanService(auth).list_plans(page, page_size, keyword, status))


@router.post("", summary="新增提成方案", response_model=None, dependencies=[Depends(AuthPermission(permission=["commission:create"]))])
async def create_plan(data: CommissionPlanCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await CommissionPlanService(auth).create(data))


@router.put("/{plan_id}", summary="编辑提成方案", response_model=None, dependencies=[Depends(AuthPermission(permission=["commission:update"]))])
async def update_plan(plan_id: UUID, data: CommissionPlanUpdateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await CommissionPlanService(auth).update(plan_id, data))


@router.delete("", summary="删除提成方案", response_model=None, dependencies=[Depends(AuthPermission(permission=["commission:delete"]))])
async def delete_plan(plan_ids: List[UUID], auth: AuthSchema = Depends(get_current_user)):
    await CommissionPlanService(auth).delete(plan_ids)
    return SuccessResponse(message="删除成功")
