"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import Registration
from .schema import (
    RegistrationSchema,
    RegistrationCreateSchema,
    RegistrationUpdateSchema,
    ScheduleCreateSchema,
    ScheduleUpdateSchema,
)
from .param import RegistrationQueryParam
from .service import RegistrationService


router = APIRouter()


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@router.get("", summary="获取挂号列表", dependencies=[Depends(AuthPermission(permission=["registration:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
    keyword: Optional[str] = Query(None, description="关键词（挂号单号 / 患者姓名 / 患者档案号）"),
    search: Optional[str] = Query(None, description="关键词别名（同 keyword）"),
    status: Optional[str] = Query(None, description="挂号状态: pending/completed/cancelled"),
    payment_status: Optional[str] = Query(None, description="支付状态: unpaid/paid/refunded/cancelled"),
    patient_id: Optional[str] = Query(None, description="患者ID"),
    doctor_id: Optional[str] = Query(None, description="医生ID"),
    department_id: Optional[str] = Query(None, description="科室ID"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
):
    filters: dict = {}
    if status:
        filters["status"] = status
    if payment_status:
        filters["payment_status"] = payment_status
    pid = RegistrationService._uuid_or_none(patient_id)
    if pid:
        filters["patient_id"] = pid
    did = RegistrationService._uuid_or_none(doctor_id)
    if did:
        filters["doctor_id"] = did
    deptid = RegistrationService._uuid_or_none(department_id)
    if deptid:
        filters["department_id"] = deptid
    # keyword / search 都是关键词别名（前端可能用 search 也可能用 keyword 传字符串）
    kw = (keyword or search or "")
    kw = kw.strip() if isinstance(kw, str) else str(kw).strip()
    if kw:
        filters["keyword"] = kw
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    if sd and ed:
        filters["registration_date"] = ("between", [sd, ed])
    params = RegistrationQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await RegistrationService(auth).list(params.page_no, params.page_size, params.order_by, filters)
    return SuccessResponse(data=data, msg="查询成功")


# ───────────────────────── 排班管理 ─────────────────────────
@router.get("/schedules", summary="获取排班列表", dependencies=[Depends(AuthPermission(permission=["registration:list"]))])
async def list_schedules_(
    auth: AuthSchema = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(10, ge=1, le=500, description="每页数量"),
    doctor_id: Optional[str] = Query(None, description="医生ID"),
    department_id: Optional[str] = Query(None, description="科室ID"),
    schedule_date: Optional[str] = Query(None, description="排班日期 (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
):
    items, total = await RegistrationService(auth).list_schedules(
        doctor_id=doctor_id,
        department_id=department_id,
        schedule_date=_parse_date(schedule_date),
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        skip=skip,
        limit=limit,
    )
    page = (skip // limit) + 1 if limit else 1
    pages = (total + limit - 1) // limit if limit else 0
    return SuccessResponse(
        data={"items": items, "pagination": {"total": total, "page": page, "page_size": limit, "pages": pages}},
        msg="查询成功",
    )


@router.post("/schedules", summary="创建排班", dependencies=[Depends(AuthPermission(permission=["registration:create"]))])
async def create_schedule_(
    data: ScheduleCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).create_schedule(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/schedules/{schedule_id}", summary="获取排班详情", dependencies=[Depends(AuthPermission(permission=["registration:get"]))])
async def get_schedule_(
    schedule_id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).get_schedule(schedule_id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/schedules/{schedule_id}", summary="更新排班", dependencies=[Depends(AuthPermission(permission=["registration:update"]))])
async def update_schedule_(
    schedule_id: str,
    data: ScheduleUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).update_schedule(schedule_id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/schedules/{schedule_id}", summary="删除排班", dependencies=[Depends(AuthPermission(permission=["registration:delete"]))])
async def delete_schedule_(
    schedule_id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await RegistrationService(auth).schedule_crud.delete([schedule_id])
    return SuccessResponse(msg="删除成功")


@router.post("/schedules/{schedule_id}/pause", summary="暂停挂号", dependencies=[Depends(AuthPermission(permission=["registration:update"]))])
async def pause_schedule_(
    schedule_id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).pause_schedule(schedule_id)
    return SuccessResponse(data=result, msg="暂停成功")


@router.post("/schedules/{schedule_id}/resume", summary="恢复挂号", dependencies=[Depends(AuthPermission(permission=["registration:update"]))])
async def resume_schedule_(
    schedule_id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).resume_schedule(schedule_id)
    return SuccessResponse(data=result, msg="恢复成功")


@router.post("/schedules/{schedule_id}/swap", summary="换班", dependencies=[Depends(AuthPermission(permission=["registration:update"]))])
async def swap_schedule_(
    schedule_id: str,
    new_doctor_id: str = Query(..., description="新医生ID"),
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).swap_schedule(schedule_id, new_doctor_id)
    return SuccessResponse(data=result, msg="换班成功")


@router.post("", summary="创建挂号", dependencies=[Depends(AuthPermission(permission=["registration:create"]))])
async def create_(
    data: RegistrationCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取挂号详情", dependencies=[Depends(AuthPermission(permission=["registration:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新挂号", dependencies=[Depends(AuthPermission(permission=["registration:update"]))])
async def update_(
    id: str,
    data: RegistrationUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await RegistrationService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除挂号", dependencies=[Depends(AuthPermission(permission=["registration:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await RegistrationService(auth).delete(id)
    return SuccessResponse(msg="删除成功")
