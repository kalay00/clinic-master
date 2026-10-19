"""
患者数据层（对齐 FastapiAdmin: module_hospital/patient/crud.py）
"""
from typing import Any, Dict, Optional

from sqlalchemy import or_

from app.core.base_crud import CRUDBase
from app.core.base_schema import AuthSchema, PageResultSchema
from app.utils.common import generate_id

from .model import Patient as PatientModel, FamilyMember as FamilyMemberModel
from .schema import PatientCreateSchema, PatientUpdateSchema, FamilyMemberCreateSchema, FamilyMemberUpdateSchema
from .param import PatientQueryParam


class FamilyMemberCRUD(CRUDBase[FamilyMemberModel, FamilyMemberCreateSchema, FamilyMemberUpdateSchema]):
    """家庭成员数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=FamilyMemberModel, auth=auth)

    async def get_by_patient(
        self,
        patient_id: Any,
        page: int = 1,
        page_size: int = 100,
    ) -> PageResultSchema:
        return await self.page(
            offset=(page - 1) * page_size,
            limit=page_size,
            search={"patient_id": patient_id},
            order_by=[{"created_at": "desc"}],
        )


class PatientCRUD(CRUDBase[PatientModel, PatientCreateSchema, PatientUpdateSchema]):
    """患者数据层"""

    def __init__(self, auth: AuthSchema) -> None:
        super().__init__(model=PatientModel, auth=auth)

    async def build_search(self, query_param: PatientQueryParam) -> dict:
        """将查询参数转换为 search 字典（姓名/手机号模糊，身份证精确，档案号模糊）"""
        search: dict = {}
        if not query_param:
            return search
        if query_param.patient_no:
            search["patient_no"] = ("like", query_param.patient_no)
        if query_param.name:
            search["name"] = ("like", query_param.name)
        if query_param.id_card:
            search["id_card"] = query_param.id_card
        if query_param.phone:
            search["phone"] = ("like", query_param.phone)
        if query_param.gender:
            search["gender"] = query_param.gender
        if query_param.blood_type:
            search["blood_type"] = query_param.blood_type
        return search

    async def get_page_by_filters(
        self,
        query_param: PatientQueryParam,
        page: int = 1,
        page_size: int = 20,
        order_by: Optional[list] = None,
    ) -> PageResultSchema:
        search = await self.build_search(query_param)
        extra_conditions = []
        if query_param.search:
            kw = (query_param.search or "").strip()
            if kw:
                # 姓名/身份证号/手机号均支持模糊匹配（已改为明文存储）
                or_conditions = [self.model.patient_no.like(f"%{kw}%")]
                or_conditions.append(self.model.name.like(f"%{kw}%"))
                or_conditions.append(self.model.id_card.like(f"%{kw}%"))
                or_conditions.append(self.model.phone.like(f"%{kw}%"))
                extra_conditions.append(or_(*or_conditions))
        return await self.page(
            offset=(page - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search,
            extra_conditions=extra_conditions,
        )

    async def create_patient(self, data: Dict[str, Any]) -> PatientModel:
        """创建患者（明文存储 + 自动生成档案号）"""
        create_data = data.copy()
        if "patient_no" not in create_data or not create_data.get("patient_no"):
            create_data["patient_no"] = f"P{generate_id().replace('-', '')[:8].upper()}"
        return await self.create(create_data)

    async def update_patient(self, id: Any, data: Dict[str, Any]) -> PatientModel:
        """更新患者（明文存储）"""
        return await self.update(id, data)

    async def serialize_patient(self, patient: PatientModel) -> Dict[str, Any]:
        """序列化患者数据（明文字段，含年龄/出生日期）"""
        from datetime import date

        data: Dict[str, Any] = {
            "id": str(patient.id),
            "tenant_id": str(patient.tenant_id) if patient.tenant_id else None,
            "patient_no": patient.patient_no,
            "name": patient.name,
            "gender": patient.gender,
            "id_card": patient.id_card,
            "phone": patient.phone,
            "birthday": patient.birthday,
            "birth_date": patient.birthday.isoformat() if patient.birthday else None,
            "address": patient.address,
            "emergency_contact": patient.emergency_contact,
            "emergency_phone": patient.emergency_phone,
            "blood_type": patient.blood_type,
            "allergy_history": patient.allergy_history,
            "chronic_disease": patient.chronic_disease,
            "remark": patient.remark,
            "member_level_id": str(patient.member_level_id) if patient.member_level_id else None,
            "balance": float(patient.balance) if patient.balance is not None else 0,
            "points": int(patient.points) if patient.points is not None else 0,
            "created_at": patient.created_at,
            "updated_at": patient.updated_at,
            "deleted_at": patient.deleted_at,
        }
        if patient.birthday:
            today = date.today()
            age = today.year - patient.birthday.year
            if (today.month, today.day) < (patient.birthday.month, patient.birthday.day):
                age -= 1
            data["age"] = age
        return data

    async def get_by_id_card(self, id_card: str) -> Optional[PatientModel]:
        if not id_card:
            return None
        return await self.get(id_card=id_card)
