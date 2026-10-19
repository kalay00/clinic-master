"""
诊疗服务（对齐旧 services/treatment_service.py + repositories/treatment_repository.py，迁移为异步 + CRUDBase，Python 3.12+）

业务规则：
- 创建病历：若关联挂号且状态为 pending，自动置为 completed 并记录就诊时间
- 处方号自动生成（PRE + 8位）
"""
from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List, Tuple, Any

from sqlalchemy import select, func, or_
from sqlalchemy.orm import joinedload

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.api.v1.module_treatment.model import MedicalRecord, Prescription
from app.api.v1.module_registration.model import Registration
from app.api.v1.module_pharmacy.model import Drug, Inventory
from app.api.v1.module_patient.model import Patient
from app.utils.common import generate_id

from .schema import (
    MedicalRecordSchema, MedicalRecordCreateSchema, MedicalRecordUpdateSchema,
    PrescriptionSchema, PrescriptionCreateSchema, PrescriptionUpdateSchema,
)
from .crud import MedicalRecordCRUD, PrescriptionCRUD


def _parse_date_str(value):
    """将 YYYY-MM-DD 字符串解析为 date，失败返回 None"""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


class TreatmentService:
    """诊疗服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = MedicalRecordCRUD(MedicalRecord, auth=auth)
        self.prescription_crud = PrescriptionCRUD(Prescription, auth=auth)

    @property
    def _db(self):
        return self.crud.db

    @property
    def _tenant_id(self) -> Optional[str]:
        return self.auth.tenant_id if self.auth else None

    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    # ── 病历（primary）──
    async def create(self, data: MedicalRecordCreateSchema) -> MedicalRecordSchema:
        record = await self.crud.create(data)
        uid = self._user_id
        if uid and hasattr(record, "created_by"):
            setattr(record, "created_by", uid)
            await self._db.flush()

        # 自动更新挂号状态为已完成
        if record.registration_id:
            try:
                registration = (
                    await self._db.execute(
                        select(Registration).where(Registration.id == record.registration_id)
                    )
                ).scalars().first()
                if registration and registration.status == "pending":
                    registration.status = "completed"
                    registration.visit_time = datetime.now()
                    await self._db.flush()
                    logger.info(f"自动更新挂号状态为已完成: {record.registration_id}")
            except Exception as e:  # pragma: no cover
                logger.warning(f"更新挂号状态失败: {e!s}", exc_info=True)

        await self._db.commit()
        logger.info(f"创建病历: {record.id} by {uid}")
        # commit 后对象属性过期，直接 model_validate 触发懒加载导致 MissingGreenlet；先 refresh 回载列。
        await self._db.refresh(record)
        return MedicalRecordSchema.model_validate(record)

    async def create_medical_record(self, record_data: dict, creator_id: Optional[str] = None) -> MedicalRecordSchema:
        record = await self.crud.create(record_data)
        uid = creator_id or self._user_id
        if uid and hasattr(record, "created_by"):
            setattr(record, "created_by", uid)
            await self._db.flush()
        if record.registration_id:
            try:
                registration = (
                    await self._db.execute(
                        select(Registration).where(Registration.id == record.registration_id)
                    )
                ).scalars().first()
                if registration and registration.status == "pending":
                    registration.status = "completed"
                    registration.visit_time = datetime.now()
                    await self._db.flush()
            except Exception as e:  # pragma: no cover
                logger.warning(f"更新挂号状态失败: {e!s}", exc_info=True)
        await self._db.commit()
        await self._db.refresh(record)
        return MedicalRecordSchema.model_validate(record)

    async def get(self, id: str) -> MedicalRecordSchema:
        return await self.crud.get_or_404(id=id, out_schema=MedicalRecordSchema)

    async def get_medical_record(self, record_id: str) -> MedicalRecordSchema:
        return await self.crud.get_or_404(id=record_id, out_schema=MedicalRecordSchema)

    async def _record_dict(self, record: MedicalRecord) -> dict:
        """病历 ORM 转富化字典（患者姓名解密，补全医生/挂号展示字段）"""
        data = MedicalRecordSchema.model_validate(record).model_dump()
        patient = getattr(record, "patient", None)
        doctor = getattr(record, "doctor", None)
        registration = getattr(record, "registration", None)
        patient_name = ""
        patient_no = None
        if patient:
            patient_no = getattr(patient, "patient_no", None)
            patient_name = patient.name or ""
        data["patient_name"] = patient_name
        data["patient_no"] = patient_no
        data["doctor_name"] = getattr(doctor, "name", "") if doctor else ""
        data["registration_no"] = getattr(registration, "registration_no", None) if registration else None
        return data

    async def list(
        self, page_no: int, page_size: int, order_by=None, search: Optional[dict] = None
    ) -> object:
        search = dict(search or {})
        extra_conditions = []
        # 关键词：患者姓名(哈希精确)/档案号(模糊) OR 诊断/主诉(模糊)
        keyword = search.pop("keyword", None)
        if keyword and keyword.strip():
            kw = keyword.strip()
            patient_subq = (
                select(Patient)
                .where(
                    Patient.id == MedicalRecord.patient_id,
                    Patient.deleted_at.is_(None),
                        or_(
                            Patient.patient_no.like(f"%{kw}%"),
                            Patient.name.like(f"%{kw}%"),
                        ),
                )
                .exists()
            )
            extra_conditions.append(
                or_(
                    MedicalRecord.diagnosis.like(f"%{kw}%"),
                    MedicalRecord.chief_complaint.like(f"%{kw}%"),
                    patient_subq,
                )
            )
        # 日期范围（按创建时间）
        sd = search.pop("start_date", None)
        ed = search.pop("end_date", None)
        if isinstance(sd, str):
            sd = _parse_date_str(sd)
        if isinstance(ed, str):
            ed = _parse_date_str(ed)
        if sd and ed:
            extra_conditions.append(MedicalRecord.created_at >= sd)
            extra_conditions.append(MedicalRecord.created_at <= datetime.combine(ed, datetime.max.time()))
        result = await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search,
            extra_conditions=extra_conditions,
            preload=["patient", "doctor", "registration"],
        )
        result.items = [await self._record_dict(obj) for obj in result.items]
        return result

    async def list_medical_records(
        self, patient_id: Optional[str] = None, doctor_id: Optional[str] = None,
        registration_id: Optional[str] = None, start_date: Optional[date] = None,
        end_date: Optional[date] = None, skip: int = 0, limit: int = 100,
    ) -> Tuple[List[MedicalRecordSchema], int]:
        stmt = select(MedicalRecord).where(MedicalRecord.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(MedicalRecord.tenant_id == self._tenant_id)
        if patient_id:
            stmt = stmt.where(MedicalRecord.patient_id == patient_id)
        if doctor_id:
            stmt = stmt.where(MedicalRecord.doctor_id == doctor_id)
        if registration_id:
            stmt = stmt.where(MedicalRecord.registration_id == registration_id)
        if start_date:
            stmt = stmt.where(MedicalRecord.created_at >= start_date)
        if end_date:
            stmt = stmt.where(MedicalRecord.created_at <= datetime.combine(end_date, datetime.max.time()))
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.order_by(MedicalRecord.created_at.desc()).offset(skip).limit(limit))).scalars().all()
        return [MedicalRecordSchema.model_validate(r) for r in rows], int(total or 0)

    async def update(self, id: str, data: MedicalRecordUpdateSchema) -> MedicalRecordSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        await self._db.refresh(obj)
        return MedicalRecordSchema.model_validate(obj)

    async def update_medical_record(self, record_id: str, record_data: dict, updater_id: Optional[str] = None) -> MedicalRecordSchema:
        obj = await self.crud.update(record_id, record_data)
        uid = updater_id or self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        await self._db.refresh(obj)
        return MedicalRecordSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 处方 ──
    async def _prescription_dict(self, prescription: Prescription) -> dict:
        """将处方 ORM 转为富化字典（含患者/医生名称，明细补全药品信息）

        PrescriptionSchema 未声明 patient/doctor 关联字段，直接 model_validate 会
        丢失展示用字段。这里在已预加载关联对象基础上手工补齐 patient_name/
        patient_no/doctor_name，并把 items 中仅含 drug_id/quantity 的明细补全药品
        名称、规格、单位、厂家、批号等展示字段。
        """
        data = PrescriptionSchema.model_validate(prescription).model_dump()
        patient = getattr(prescription, "patient", None)
        doctor = getattr(prescription, "doctor", None)

        patient_name = ""
        patient_no = None
        if patient:
            patient_no = getattr(patient, "patient_no", None)
            patient_name = patient.name or ""

        data["patient_name"] = patient_name
        data["patient_no"] = patient_no
        data["doctor_name"] = getattr(doctor, "name", "") if doctor else ""

        # 补全处方明细中的药品展示信息（items 可能缺 drug_name/specification/unit 等）
        data["items"] = await self._enrich_prescription_items(data.get("items"))
        return data

    async def _enrich_prescription_items(self, items: Any) -> Any:
        """将处方明细统一为数组，并补全药品名称/规格/单位/厂家/批号。

        items 存储形态可能为：
        - dict：以 drug_id 为 key，value 含 quantity/dosage/price/amount
        - list：元素含 drug_id（或 drugId）及上述字段
        仅存储 drug_id 时，前端详情无法展示药品名称，这里按 drug_id 联表补全。
        """
        if not items:
            return items

        # 统一为 (drug_id, item) 列表
        pairs: List[Tuple[Optional[str], dict]] = []
        if isinstance(items, dict):
            for drug_id, it in items.items():
                pairs.append((str(drug_id), dict(it or {})))
        elif isinstance(items, list):
            for it in items:
                if not isinstance(it, dict):
                    continue
                drug_id = it.get("drug_id") or it.get("drugId")
                pairs.append((str(drug_id) if drug_id is not None else None, dict(it)))
        else:
            return items

        # 批量查询药品信息
        drug_ids = [pid for pid, _ in pairs if pid]
        drug_map: dict = {}
        if drug_ids:
            rows = (await self._db.execute(select(Drug).where(Drug.id.in_(drug_ids)))).scalars().all()
            for d in rows:
                drug_map[str(d.id)] = d

        # 批量查询库存批号（每个 drug_id 取一条即可用于展示）
        batch_map: dict = {}
        if drug_ids:
            inv_rows = (await self._db.execute(
                select(Inventory.drug_id, Inventory.batch_no)
                .where(Inventory.drug_id.in_(drug_ids))
                .where(Inventory.batch_no.isnot(None))
            )).all()
            for drug_id, batch_no in inv_rows:
                if drug_id and str(drug_id) not in batch_map:
                    batch_map[str(drug_id)] = batch_no

        enriched = []
        for drug_id, it in pairs:
            drug = drug_map.get(drug_id) if drug_id else None
            it["drug_id"] = drug_id
            if drug is not None:
                it.setdefault("drug_name", getattr(drug, "name", "") or "")
                it.setdefault("specification", getattr(drug, "specification", "") or "")
                it.setdefault("unit", getattr(drug, "unit", "") or "")
                it.setdefault("manufacturer", getattr(drug, "manufacturer", "") or "")
                it.setdefault("category", getattr(drug, "category", "") or "")
            else:
                it.setdefault("drug_name", "")
                it.setdefault("specification", "")
                it.setdefault("unit", "")
                it.setdefault("manufacturer", "")
                it.setdefault("category", "")
            # 批号优先取明细自带，否则取库存
            if not it.get("batch_no") and drug_id in batch_map:
                it["batch_no"] = batch_map[drug_id]
            enriched.append(it)
        return enriched

    async def create_prescription(self, prescription_data: dict, creator_id: Optional[str] = None) -> dict:
        prescription_data = dict(prescription_data)
        prescription_data.setdefault("prescription_no", f"PRE{generate_id()[:8].upper()}")
        prescription = await self.prescription_crud.create(prescription_data)

        # 处方创建后自动生成收费账单：状态流转 待收费(pending) → 已收费(paid) → 已发药(dispensed)
        try:
            from app.api.v1.module_payment.model import Bill as BillModel
            bill_no = f"BILL{generate_id()[:8].upper()}"
            bill_data = {
                "bill_no": bill_no,
                "tenant_id": self._tenant_id,
                "patient_id": prescription.patient_id,
                "medical_record_id": prescription.medical_record_id,
                "prescription_id": prescription.id,
                "bill_type": "prescription",
                "total_amount": float(prescription.total_amount or 0),
                "status": "unpaid",
                "items": prescription.items,
                "remark": f"处方收费：{prescription.prescription_no or ''}",
            }
            if prescription.medical_record_id:
                mr = (
                    await self._db.execute(
                        select(MedicalRecord).where(MedicalRecord.id == prescription.medical_record_id)
                    )
                ).scalars().first()
                if mr:
                    bill_data["registration_id"] = mr.registration_id
            bill = BillModel(**bill_data)
            self._db.add(bill)
            await self._db.flush()
            prescription.bill_id = bill.id
            await self._db.flush()
            logger.info(f"处方 {prescription.id} 已生成收费账单 {bill_no}")
        except Exception as e:  # pragma: no cover
            logger.warning(f"创建处方收费账单失败: {e!s}", exc_info=True)

        uid = creator_id or self._user_id
        if uid and hasattr(prescription, "created_by"):
            setattr(prescription, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        logger.info(f"创建处方: {prescription.id} by {uid}")
        await self._db.refresh(prescription)
        await self._db.refresh(prescription, attribute_names=["patient", "doctor"])
        return await self._prescription_dict(prescription)

    async def get_prescription(self, prescription_id: str) -> dict:
        prescription = await self.prescription_crud.get_or_404(
            id=prescription_id, preload=["patient", "doctor", "medical_record"]
        )
        return await self._prescription_dict(prescription)

    async def list_prescriptions(
        self, patient_id: Optional[str] = None, doctor_id: Optional[str] = None,
        medical_record_id: Optional[str] = None, status: Optional[str] = None,
        skip: int = 0, limit: int = 100,
    ) -> Tuple[List[dict], int]:
        stmt = select(Prescription).options(
            joinedload(Prescription.patient), joinedload(Prescription.doctor), joinedload(Prescription.medical_record)
        ).where(Prescription.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(Prescription.tenant_id == self._tenant_id)
        if patient_id:
            stmt = stmt.where(Prescription.patient_id == patient_id)
        if doctor_id:
            stmt = stmt.where(Prescription.doctor_id == doctor_id)
        if medical_record_id:
            stmt = stmt.where(Prescription.medical_record_id == medical_record_id)
        if status:
            stmt = stmt.where(Prescription.status == status)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.order_by(Prescription.created_at.desc()).offset(skip).limit(limit))).scalars().all()
        enriched_rows = [await self._prescription_dict(r) for r in rows]
        return enriched_rows, int(total or 0)

    async def update_prescription(self, prescription_id: str, prescription_data: dict, updater_id: Optional[str] = None) -> dict:
        obj = await self.prescription_crud.update(prescription_id, prescription_data)
        uid = updater_id or self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        await self._db.refresh(obj)
        await self._db.refresh(obj, attribute_names=["patient", "doctor"])
        return await self._prescription_dict(obj)
