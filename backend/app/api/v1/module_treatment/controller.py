"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import MedicalRecord
from .schema import (
    MedicalRecordSchema,
    MedicalRecordCreateSchema,
    MedicalRecordUpdateSchema,
    PrescriptionCreateSchema,
    PrescriptionUpdateSchema,
)
from .param import TreatmentQueryParam
from .service import TreatmentService


router = APIRouter()


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _uuid_or_none(value: Optional[str]) -> Optional[UUID]:
    if not value:
        return None
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        return None


@router.get("", summary="获取诊疗列表", dependencies=[Depends(AuthPermission(permission=["treatment:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
    keyword: Optional[str] = Query(None, description="关键词（患者姓名/档案号/诊断/主诉）"),
    patient_id: Optional[str] = Query(None, description="患者ID"),
    doctor_id: Optional[str] = Query(None, description="医生ID"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
):
    search = {}
    pid = _uuid_or_none(patient_id)
    if pid:
        search["patient_id"] = pid
    did = _uuid_or_none(doctor_id)
    if did:
        search["doctor_id"] = did
    if keyword:
        search["keyword"] = keyword
    sd = _parse_date(start_date)
    ed = _parse_date(end_date)
    if sd and ed:
        search["start_date"] = sd
        search["end_date"] = ed
    params = TreatmentQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await TreatmentService(auth).list(params.page_no, params.page_size, params.order_by, search)
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建诊疗", dependencies=[Depends(AuthPermission(permission=["treatment:create"]))])
async def create_(
    data: MedicalRecordCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TreatmentService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


# ───────────────────────── 处方管理 ─────────────────────────
# 注意：处方路由必须放在 "/{id}" 路由之前，否则 GET /prescriptions 会被
# "/{id}" 误匹配为 id="prescriptions" 而返回 405。
@router.get("/prescriptions", summary="获取处方列表", dependencies=[Depends(AuthPermission(permission=["treatment:list"]))])
async def list_prescriptions_(
    auth: AuthSchema = Depends(get_current_user),
    patient_id: Optional[str] = Query(None, description="患者ID"),
    doctor_id: Optional[str] = Query(None, description="医生ID"),
    medical_record_id: Optional[str] = Query(None, description="病历ID"),
    status: Optional[str] = Query(None, description="状态"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(10, ge=1, le=1000, description="每页数量（发药页需一次拉取全部处方，放宽至1000）"),
):
    items, total = await TreatmentService(auth).list_prescriptions(
        patient_id=patient_id,
        doctor_id=doctor_id,
        medical_record_id=medical_record_id,
        status=status,
        skip=skip,
        limit=limit,
    )
    page = (skip // limit) + 1 if limit else 1
    pages = (total + limit - 1) // limit if limit else 0
    return SuccessResponse(
        data={
            "items": items,
            "pagination": {"total": total, "page": page, "page_size": limit, "pages": pages},
        },
        msg="查询成功",
    )


@router.post("/prescriptions", summary="创建处方", dependencies=[Depends(AuthPermission(permission=["treatment:create"]))])
async def create_prescription_(
    data: PrescriptionCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TreatmentService(auth).create_prescription(data.model_dump(exclude_unset=True))
    return SuccessResponse(data=result.model_dump() if hasattr(result, "model_dump") else result, msg="创建成功")


@router.get("/prescriptions/{prescription_id}", summary="获取处方详情", dependencies=[Depends(AuthPermission(permission=["treatment:get"]))])
async def get_prescription_(
    prescription_id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TreatmentService(auth).get_prescription(prescription_id)
    return SuccessResponse(data=result.model_dump() if hasattr(result, "model_dump") else result, msg="查询成功")


@router.put("/prescriptions/{prescription_id}", summary="更新处方", dependencies=[Depends(AuthPermission(permission=["treatment:update"]))])
async def update_prescription_(
    prescription_id: str,
    data: PrescriptionUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TreatmentService(auth).update_prescription(prescription_id, data.model_dump(exclude_unset=True))
    return SuccessResponse(data=result.model_dump() if hasattr(result, "model_dump") else result, msg="更新成功")


@router.delete("/prescriptions/{prescription_id}", summary="删除处方", dependencies=[Depends(AuthPermission(permission=["treatment:delete"]))])
async def delete_prescription_(
    prescription_id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await TreatmentService(auth).prescription_crud.delete([prescription_id])
    return SuccessResponse(msg="删除成功")


@router.get("/{id}", summary="获取诊疗详情", dependencies=[Depends(AuthPermission(permission=["treatment:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TreatmentService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新诊疗", dependencies=[Depends(AuthPermission(permission=["treatment:update"]))])
async def update_(
    id: str,
    data: MedicalRecordUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await TreatmentService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除诊疗", dependencies=[Depends(AuthPermission(permission=["treatment:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await TreatmentService(auth).delete(id)
    return SuccessResponse(msg="删除成功")
