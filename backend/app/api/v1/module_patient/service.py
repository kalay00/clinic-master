"""
患者服务层（对齐 FastapiAdmin: module_hospital/patient/service.py）
"""
from __future__ import annotations
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.base_schema import AuthSchema, PageResultSchema
from app.core.exceptions import CustomException
from app.core.logger import logger

from app.api.v1.module_treatment.model import MedicalRecord
from app.api.v1.module_doctor.model import Doctor
from app.api.v1.module_department.model import Department

from .crud import FamilyMemberCRUD, PatientCRUD
from .schema import (
    FamilyMemberCreateSchema,
    FamilyMemberSchema,
    FamilyMemberUpdateSchema,
    PatientCreateSchema,
    PatientSchema,
    PatientUpdateSchema,
)
from .param import PatientQueryParam


class PatientService:
    """患者管理服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = PatientCRUD(auth)

    async def create_patient(self, data: PatientCreateSchema) -> PatientSchema:
        """创建患者（明文存储、自动档案号）

        严格唯一：同一租户下身份证号不可重复。若已存在，则拒绝新建，
        避免产生重复的身份证号档案（DB 层另以部分唯一索引兜底）。
        """
        if not data.id_card or not data.id_card.strip():
            raise CustomException(msg="身份证号是必填项，所有患者必须以身份证号建立就诊档案", code=400, status_code=400)

        # 严格唯一校验：同租户下身份证号不可重复
        existing = await self.crud.get_by_id_card(data.id_card)
        if existing:
            raise CustomException(code=400, status_code=400, msg="身份证号已存在，请勿重复建档")

        patient = await self.crud.create_patient(data.model_dump())
        # 默认会员等级（普通会员）
        if not patient.member_level_id:
            try:
                from app.api.v1.module_member.service import MemberLevelService
                default_level = await MemberLevelService(self.auth).get_default()
                if default_level:
                    patient.member_level_id = default_level.id
                    patient.consumption_total = 0
                    await self.crud.session.flush()
            except Exception:
                pass
        patient_data = await self.crud.serialize_patient(patient)
        patient_data["is_return_visit"] = False
        return PatientSchema(**patient_data)

    async def get_patient(self, id: str) -> PatientSchema:
        patient = await self.crud.get(id=id)
        if not patient:
            raise CustomException(msg="患者不存在", code=404, status_code=404)
        patient_data = await self.crud.serialize_patient(patient)
        return PatientSchema(**patient_data)

    async def get_patient_by_id_card(self, id_card: str) -> Optional[PatientSchema]:
        patient = await self.crud.get_by_id_card(id_card)
        if not patient:
            return None
        patient_data = await self.crud.serialize_patient(patient)
        return PatientSchema(**patient_data)

    async def update_patient(self, id: str, data: PatientUpdateSchema) -> PatientSchema:
        patient = await self.crud.get(id=id)
        if not patient:
            raise CustomException(code=404, msg="患者不存在")
        if data.id_card:
            # 仅当身份证号真正发生变化时才做重复校验。
            if data.id_card != patient.id_card:
                other = await self.crud.get_by_id_card(data.id_card)
                if other and str(other.id) != str(id):
                    raise CustomException(code=400, status_code=400, msg="身份证号已存在")
        updated = await self.crud.update_patient(id, data.model_dump(exclude_unset=True))
        patient_data = await self.crud.serialize_patient(updated)
        return PatientSchema(**patient_data)

    async def delete_patient(self, id: str) -> bool:
        patient = await self.crud.get(id=id)
        if not patient:
            raise CustomException(msg="患者不存在", code=404, status_code=404)
        return await self.crud.soft_delete(id)

    async def list_patients(
        self, query_param: PatientQueryParam, page: int = 1, page_size: int = 20
    ) -> PageResultSchema[PatientSchema]:
        result = await self.crud.get_page_by_filters(query_param, page, page_size)
        items: List[dict] = []
        for patient in result.items:
            patient_data = await self.crud.serialize_patient(patient)
            items.append(PatientSchema(**patient_data).model_dump())
        return PageResultSchema(
            items=items,
            total=result.total,
            page_no=result.page_no,
            page_size=result.page_size,
            has_next=result.has_next,
        )

    async def search_patients(self, keyword: str, page: int = 1, page_size: int = 20) -> PageResultSchema[PatientSchema]:
        query_param = PatientQueryParam(search=keyword)
        return await self.list_patients(query_param, page, page_size)

    async def get_patient_visits(
        self, patient_id: str, limit: int = 50
    ) -> List[dict]:
        """获取患者就诊历史（基于诊疗病历，预加载医生与科室）

        前端 patients/detail.html 的 getVisits 期望字段：
        visit_date / created_at、doctor_name / doctor.name、department / department_name、diagnosis。
        """
        stmt = (
            select(MedicalRecord)
            .where(MedicalRecord.deleted_at.is_(None))
            .where(MedicalRecord.patient_id == patient_id)
            .options(
                joinedload(MedicalRecord.doctor).joinedload(Doctor.department),
            )
            .order_by(MedicalRecord.created_at.desc())
            .limit(limit)
        )
        if self.auth and self.auth.tenant_id is not None:
            stmt = stmt.where(MedicalRecord.tenant_id == self.auth.tenant_id)
        rows = (await self.crud.db.execute(stmt)).scalars().all()

        visits: List[dict] = []
        for rec in rows:
            doctor = rec.doctor
            department_name = ""
            if doctor is not None and doctor.department is not None:
                department_name = doctor.department.name or ""
            doctor_name = doctor.name if doctor is not None else ""
            visits.append(
                {
                    "id": str(rec.id),
                    "visit_date": rec.created_at.isoformat() if rec.created_at else None,
                    "created_at": rec.created_at.isoformat() if rec.created_at else None,
                    "doctor_name": doctor_name,
                    "doctor": {"name": doctor_name} if doctor_name else None,
                    "department": department_name,
                    "department_name": department_name,
                    "diagnosis": rec.diagnosis or "",
                    "chief_complaint": rec.chief_complaint or "",
                    "status": "已完成",
                }
            )
        return visits

    async def recharge(self, patient_id: str, amount: float, method: Optional[str] = None, remark: Optional[str] = None) -> dict:
        """患者余额充值（按系统设置赠送比例计算赠送金额）"""
        patient = await self.crud.get(id=patient_id)
        if not patient:
            raise CustomException(msg="患者不存在", code=404, status_code=404)
        amount = float(amount)
        # 读取租户会员积分配置，按 recharge_bonus_ratio 计算赠送
        bonus_ratio = 0
        try:
            from app.api.v1.module_tenant.service import TenantService

            cfg = await TenantService(self.auth).get_tenant_config(self.auth.tenant_id)
            loyalty = (cfg or {}).get("loyalty", {}) or {}
            bonus_ratio = float(loyalty.get("recharge_bonus_ratio", 0) or 0)
        except Exception as e:
            logger.warning(f"读取会员积分配置失败，充值不赠送: {e}")
        gift = round(amount * bonus_ratio, 2)
        patient.balance = round(float(patient.balance or 0) + amount + gift, 2)
        await self.crud.db.flush()
        await self.crud.db.commit()
        patient_data = await self.crud.serialize_patient(patient)
        patient_data["gift"] = gift
        patient_data["recharge_amount"] = amount
        return patient_data


class FamilyMemberService:
    """家庭成员服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = FamilyMemberCRUD(auth)

    async def list(
        self, patient_id: str, page: int = 1, page_size: int = 100
    ) -> PageResultSchema:
        return await self.crud.get_by_patient(patient_id, page, page_size)

    async def create(
        self, patient_id: str, data: FamilyMemberCreateSchema
    ) -> dict:
        create_data = data.model_dump(exclude_unset=True)
        create_data["patient_id"] = patient_id
        item = await self.crud.create(create_data)
        return FamilyMemberSchema.model_validate(item).model_dump()

    async def update(
        self, id: str, data: FamilyMemberUpdateSchema
    ) -> dict:
        item = await self.crud.update(id, data.model_dump(exclude_unset=True))
        return FamilyMemberSchema.model_validate(item).model_dump()

    async def delete(self, id: str) -> bool:
        item = await self.crud.get(id=id)
        if not item:
            raise CustomException(msg="家庭成员不存在", code=404, status_code=404)
        return await self.crud.soft_delete(id)
