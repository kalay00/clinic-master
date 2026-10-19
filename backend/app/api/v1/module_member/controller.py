"""
会员模块 路由
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from uuid import UUID
from app.core.dependencies import AuthPermission, get_current_user
from app.core.base_schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.exceptions import CustomException
from app.core.base_schema import BaseSchema
from .service import MemberLevelService, MemberService
from .schema import (
    MemberLevelSchema, MemberLevelCreateSchema, MemberLevelUpdateSchema,
    MemberRechargeSchema, MemberRefundSchema, MemberPointsSchema, MemberLevelSetSchema,
    MemberUpdateSchema,
)

router = APIRouter(tags=["会员等级"])


@router.get("", summary="会员等级列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:list"]))])
async def list_member_levels(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    svc = MemberLevelService(auth)
    result = await svc.list_levels(page, page_size, keyword, status)
    return SuccessResponse(data=result)


@router.post("", summary="新增会员等级", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:create"]))])
async def create_member_level(
    data: MemberLevelCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    svc = MemberLevelService(auth)
    return SuccessResponse(data=await svc.create(data))


@router.put("/{level_id}", summary="编辑会员等级", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:update"]))])
async def update_member_level(
    level_id: UUID,
    data: MemberLevelUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    svc = MemberLevelService(auth)
    return SuccessResponse(data=await svc.update(level_id, data))


@router.delete("", summary="删除会员等级", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:delete"]))])
async def delete_member_level(
    level_ids: List[UUID],
    auth: AuthSchema = Depends(get_current_user),
):
    svc = MemberLevelService(auth)
    await svc.delete(level_ids)
    return SuccessResponse(message="删除成功")


# ===== 会员（患者资产）管理 =====
member_router = APIRouter(tags=["会员管理"])


@member_router.get("/members", summary="会员列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:list"]))])
async def list_members(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    level_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    member_type: Optional[str] = Query(None),
):
    svc = MemberService(auth)
    return SuccessResponse(data=await svc.list_members(page, page_size, keyword, level_id, status, member_type))


@member_router.put("/members/{patient_id}", summary="编辑会员信息", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:update"]))])
async def update_member(
    patient_id: str,
    data: MemberUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    svc = MemberService(auth)
    return SuccessResponse(data=await svc.update_member(patient_id, data), msg="保存成功")


@member_router.post("/members/{patient_id}/recharge", summary="会员储值充值", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:update"]))])
async def recharge_member(
    patient_id: str,
    data: MemberRechargeSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    svc = MemberService(auth)
    return SuccessResponse(data=await svc.recharge(patient_id, data), msg="充值成功")


@member_router.post("/members/{patient_id}/refund", summary="会员余额退款", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:update"]))])
async def refund_member(
    patient_id: str,
    data: MemberRefundSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    svc = MemberService(auth)
    return SuccessResponse(data=await svc.refund(patient_id, data), msg="退款成功")


@member_router.post("/members/{patient_id}/points", summary="会员积分变动", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:update"]))])
async def points_member(
    patient_id: str,
    data: MemberPointsSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    svc = MemberService(auth)
    return SuccessResponse(data=await svc.adjust_points(patient_id, data), msg="积分变动成功")


@member_router.post("/members/{patient_id}/level", summary="设置会员等级", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:update"]))])
async def set_member_level(
    patient_id: str,
    data: MemberLevelSetSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    svc = MemberService(auth)
    return SuccessResponse(data=await svc.set_level(patient_id, data), msg="设置成功")


@member_router.get("/members/{patient_id}/transactions", summary="会员交易流水", response_model=None, dependencies=[Depends(AuthPermission(permission=["member:list"]))])
async def member_transactions(
    patient_id: str,
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None),
):
    svc = MemberService(auth)
    return SuccessResponse(data=await svc.get_transactions(patient_id, page, page_size, type))
