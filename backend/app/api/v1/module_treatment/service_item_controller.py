"""
处方服务项目 路由（诊疗结束后开具处方时，选择服务项目）
"""
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from sqlalchemy import select, func
from app.core.dependencies import AuthPermission, get_current_user
from app.core.base_schema import AuthSchema
from app.core.base_crud import CRUDBase
from app.common.response import SuccessResponse
from app.core.exceptions import CustomException
from .model import Prescription, PrescriptionServiceItem
from app.api.v1.module_project.model import Project
from app.api.v1.module_patient.model import Patient
from app.api.v1.module_member.model import MemberLevel
from app.api.v1.module_doctor.model import Doctor
from app.api.v1.module_commission.model import CommissionPlan
from app.api.v1.module_payment.model import Bill

prescription_service_router = APIRouter(tags=["处方服务项目"])


async def _recalc_total(db, prescription_id):
    prescription = (await db.execute(
        select(Prescription).where(Prescription.id == prescription_id)
    )).scalars().first()
    if not prescription:
        return
    service_total = (await db.execute(
        select(func.coalesce(func.sum(PrescriptionServiceItem.total_amount), 0)).where(
            PrescriptionServiceItem.prescription_id == prescription_id,
            PrescriptionServiceItem.deleted_at.is_(None),
        )
    )).scalar() or 0
    drug_total = 0
    if isinstance(prescription.items, list):
        for it in prescription.items:
            drug_total += float(it.get("total_amount") or it.get("amount") or 0)
    prescription.total_amount = round(float(drug_total) + float(service_total), 2)
    await db.flush()
    # 同步关联收费账单（仅未支付时），确保服务项目费用可正常结算
    bill = (await db.execute(
        select(Bill).where(Bill.prescription_id == prescription_id)
    )).scalars().first()
    if bill and bill.status == "unpaid":
        bill.total_amount = prescription.total_amount
        await db.flush()


@prescription_service_router.get("/prescriptions/{prescription_id}/services", summary="处方服务项目列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["treatment:list"]))])
async def list_services(prescription_id: UUID, auth: AuthSchema = Depends(get_current_user)):
    rows = (await auth.db.execute(
        select(PrescriptionServiceItem).where(
            PrescriptionServiceItem.prescription_id == prescription_id,
            PrescriptionServiceItem.deleted_at.is_(None),
        ).order_by(PrescriptionServiceItem.created_at.asc())
    )).scalars().all()
    return SuccessResponse(data=[{**r.__dict__, "id": str(r.id)} for r in rows])


@prescription_service_router.post("/prescriptions/{prescription_id}/services", summary="添加服务项目", response_model=None, dependencies=[Depends(AuthPermission(permission=["treatment:update"]))])
async def add_service(prescription_id: UUID, body: dict, auth: AuthSchema = Depends(get_current_user)):
    db = auth.db
    prescription = (await db.execute(select(Prescription).where(Prescription.id == prescription_id))).scalars().first()
    if not prescription:
        raise CustomException(msg="处方不存在")
    project_id = body.get("project_id")
    quantity = int(body.get("quantity", 1))
    technician_id = body.get("technician_id")
    project = (await db.execute(select(Project).where(Project.id == project_id, Project.deleted_at.is_(None)))).scalars().first()
    if not project:
        raise CustomException(msg="项目不存在")

    # 会员折扣
    unit_price = float(project.price or 0)
    participate_member_discount = bool(project.participate_member_discount)
    if participate_member_discount:
        patient = (await db.execute(select(Patient).where(Patient.id == prescription.patient_id))).scalars().first()
        discount = 1.0
        if patient and patient.member_level_id:
            level = (await db.execute(select(MemberLevel).where(MemberLevel.id == patient.member_level_id))).scalars().first()
            discount = float(level.discount_rate) if level else 1.0
        unit_price = round(unit_price * discount, 2)
    total_amount = round(unit_price * quantity, 2)

    # 提成
    participate_commission = bool(project.participate_commission)
    commission_amount = 0.0
    if participate_commission:
        doctor = (await db.execute(select(Doctor).where(Doctor.id == prescription.doctor_id))).scalars().first()
        if doctor and doctor.commission_plan_id:
            plan = (await db.execute(select(CommissionPlan).where(CommissionPlan.id == doctor.commission_plan_id))).scalars().first()
            if plan:
                if plan.type == "fixed":
                    commission_amount = float(plan.fixed_amount or 0)
                else:
                    commission_amount = round(total_amount * float(plan.percentage_rate or 0), 2)

    item = PrescriptionServiceItem(
        prescription_id=prescription_id,
        project_id=str(project.id),
        project_name=project.name,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        technician_id=str(technician_id) if technician_id else None,
        participate_member_discount=participate_member_discount,
        participate_commission=participate_commission,
        commission_amount=commission_amount,
        status="pending",
        tenant_id=auth.tenant_id,
    )
    db.add(item)
    await db.flush()
    await _recalc_total(db, prescription_id)
    await db.commit()
    return SuccessResponse(data={"id": str(item.id), "total_amount": total_amount, "commission_amount": commission_amount})


@prescription_service_router.delete("/prescriptions/services/{item_id}", summary="移除服务项目", response_model=None, dependencies=[Depends(AuthPermission(permission=["treatment:update"]))])
async def remove_service(item_id: UUID, auth: AuthSchema = Depends(get_current_user)):
    db = auth.db
    item = (await db.execute(select(PrescriptionServiceItem).where(PrescriptionServiceItem.id == item_id, PrescriptionServiceItem.deleted_at.is_(None)))).scalars().first()
    if not item:
        raise CustomException(msg="服务项目不存在")
    pid = item.prescription_id
    await CRUDBase(PrescriptionServiceItem, auth, db).delete([item_id])
    await _recalc_total(db, pid)
    await db.commit()
    return SuccessResponse(message="移除成功")
