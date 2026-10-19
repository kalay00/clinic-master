"""
中医服务（对齐旧 services/tcm_service.py + repositories/tcm_repository.py，迁移为异步 + CRUDBase，Python 3.12+）

涵盖：西医诊断 / 中医诊断 / 四诊 / 中医治疗方法 / 中药处方 / 处方明细 / 方剂 / 煎药服务
（旧代码中的 UUID 字符串转换在异步 SQLAlchemy 下无需手动处理，直接传字符串即可）
"""
from __future__ import annotations
from typing import Optional

from sqlalchemy import select, func

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import (
    Diagnosis, TCMDiagnosis, TCMFourExaminations, TCMTreatment,
    TCMPrescription, TCMPrescriptionItem, TCMFormula, TCMDecoctionService,
)
from .schema import (
    DiagnosisSchema, DiagnosisCreateSchema, DiagnosisUpdateSchema,
    TCMDiagnosisSchema, TCMDiagnosisCreateSchema, TCMDiagnosisUpdateSchema,
    TCMFourExaminationsSchema, TCMFourExaminationsCreateSchema, TCMFourExaminationsUpdateSchema,
    TCMTreatmentSchema, TCMTreatmentCreateSchema, TCMTreatmentUpdateSchema,
    TCMPrescriptionSchema, TCMPrescriptionCreateSchema, TCMPrescriptionUpdateSchema,
    TCMPrescriptionItemSchema, TCMPrescriptionItemCreateSchema, TCMPrescriptionItemUpdateSchema,
    TCMFormulaSchema, TCMFormulaCreateSchema, TCMFormulaUpdateSchema,
    TCMDecoctionServiceSchema, TCMDecoctionServiceCreateSchema, TCMDecoctionServiceUpdateSchema,
)
from .crud import (
    DiagnosisCRUD, TCMDiagnosisCRUD, TCMFourExaminationsCRUD, TCMTreatmentCRUD,
    TCMPrescriptionCRUD, TCMPrescriptionItemCRUD, TCMFormulaCRUD, TCMDecoctionServiceCRUD,
)


class TCMService:
    """中医服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = DiagnosisCRUD(Diagnosis, auth=auth)
        self.tcm_diagnosis_crud = TCMDiagnosisCRUD(TCMDiagnosis, auth=auth)
        self.four_exam_crud = TCMFourExaminationsCRUD(TCMFourExaminations, auth=auth)
        self.treatment_crud = TCMTreatmentCRUD(TCMTreatment, auth=auth)
        self.prescription_crud = TCMPrescriptionCRUD(TCMPrescription, auth=auth)
        self.prescription_item_crud = TCMPrescriptionItemCRUD(TCMPrescriptionItem, auth=auth)
        self.formula_crud = TCMFormulaCRUD(TCMFormula, auth=auth)
        self.decoction_crud = TCMDecoctionServiceCRUD(TCMDecoctionService, auth=auth)

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

    async def _persist(self, obj, creator_id: Optional[str] = None):
        uid = creator_id or self._user_id
        if uid and hasattr(obj, "created_by"):
            setattr(obj, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return obj

    # ── 标准 CRUD（primary: Diagnosis）──
    async def create(self, data: DiagnosisCreateSchema) -> DiagnosisSchema:
        obj = await self._persist(await self.crud.create(data))
        return DiagnosisSchema.model_validate(obj)

    async def get(self, id: str) -> DiagnosisSchema:
        return await self.crud.get_or_404(id=id, out_schema=DiagnosisSchema)

    async def list(self, page_no: int, page_size: int, order_by=None, search: Optional[dict] = None) -> object:
        return await self.crud.page(
            offset=(page_no - 1) * page_size, limit=page_size,
            order_by=order_by or [{"created_at": "desc"}], search=search or {}, out_schema=DiagnosisSchema,
        )

    async def update(self, id: str, data: DiagnosisUpdateSchema) -> DiagnosisSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return DiagnosisSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 西医诊断 ──
    async def create_diagnosis(self, diagnosis_data: dict, creator_id: Optional[str] = None) -> DiagnosisSchema:
        obj = await self._persist(await self.crud.create(diagnosis_data), creator_id)
        return DiagnosisSchema.model_validate(obj)

    async def get_diagnosis(self, diagnosis_id: str) -> DiagnosisSchema:
        return await self.crud.get_or_404(id=diagnosis_id, out_schema=DiagnosisSchema)

    async def get_diagnoses_by_medical_record(self, medical_record_id: str) -> list[DiagnosisSchema]:
        stmt = select(Diagnosis).where(Diagnosis.deleted_at.is_(None), Diagnosis.medical_record_id == medical_record_id)
        if self._tenant_id is not None:
            stmt = stmt.where(Diagnosis.tenant_id == self._tenant_id)
        rows = (await self._db.execute(stmt)).scalars().all()
        return [DiagnosisSchema.model_validate(r) for r in rows]

    # ── 中医诊断 ──
    async def create_tcm_diagnosis(self, data: dict, creator_id: Optional[str] = None) -> TCMDiagnosisSchema:
        obj = await self._persist(await self.tcm_diagnosis_crud.create(data), creator_id)
        return TCMDiagnosisSchema.model_validate(obj)

    async def get_tcm_diagnosis_by_medical_record(self, medical_record_id: str) -> Optional[TCMDiagnosisSchema]:
        stmt = select(TCMDiagnosis).where(TCMDiagnosis.deleted_at.is_(None), TCMDiagnosis.medical_record_id == medical_record_id)
        if self._tenant_id is not None:
            stmt = stmt.where(TCMDiagnosis.tenant_id == self._tenant_id)
        obj = (await self._db.execute(stmt)).scalars().first()
        return TCMDiagnosisSchema.model_validate(obj) if obj else None

    # ── 四诊 ──
    async def create_or_update_tcm_four_examinations(self, data: dict, creator_id: Optional[str] = None) -> TCMFourExaminationsSchema:
        medical_record_id = data.get("medical_record_id")
        if not medical_record_id:
            raise CustomException(msg="medical_record_id不能为空", code=400)
        existing_stmt = select(TCMFourExaminations).where(
            TCMFourExaminations.deleted_at.is_(None), TCMFourExaminations.medical_record_id == medical_record_id
        )
        if self._tenant_id is not None:
            existing_stmt = existing_stmt.where(TCMFourExaminations.tenant_id == self._tenant_id)
        existing = (await self._db.execute(existing_stmt)).scalars().first()
        if existing:
            obj = await self.four_exam_crud.update(str(existing.id), data)
            uid = creator_id or self._user_id
            if uid and hasattr(obj, "updated_by"):
                setattr(obj, "updated_by", uid)
                await self._db.flush()
            await self._db.commit()
            return TCMFourExaminationsSchema.model_validate(obj)
        obj = await self._persist(await self.four_exam_crud.create(data), creator_id)
        return TCMFourExaminationsSchema.model_validate(obj)

    # ── 中医治疗方法 ──
    async def create_tcm_treatment(self, data: dict, creator_id: Optional[str] = None) -> TCMTreatmentSchema:
        obj = await self._persist(await self.treatment_crud.create(data), creator_id)
        return TCMTreatmentSchema.model_validate(obj)

    async def get_tcm_treatments_by_medical_record(self, medical_record_id: str) -> list[TCMTreatmentSchema]:
        stmt = select(TCMTreatment).where(TCMTreatment.deleted_at.is_(None), TCMTreatment.medical_record_id == medical_record_id)
        if self._tenant_id is not None:
            stmt = stmt.where(TCMTreatment.tenant_id == self._tenant_id)
        rows = (await self._db.execute(stmt)).scalars().all()
        return [TCMTreatmentSchema.model_validate(r) for r in rows]

    # ── 中药处方 ──
    async def create_tcm_prescription(self, data: dict, creator_id: Optional[str] = None) -> TCMPrescriptionSchema:
        obj = await self._persist(await self.prescription_crud.create(data), creator_id)
        return TCMPrescriptionSchema.model_validate(obj)

    async def get_tcm_prescription(self, prescription_id: str) -> TCMPrescriptionSchema:
        obj = await self.prescription_crud.get_or_404(id=prescription_id, out_schema=TCMPrescriptionSchema)
        return obj

    async def list_tcm_prescriptions(self, medical_record_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[list[TCMPrescriptionSchema], int]:
        stmt = select(TCMPrescription).where(TCMPrescription.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(TCMPrescription.tenant_id == self._tenant_id)
        if medical_record_id:
            stmt = stmt.where(TCMPrescription.medical_record_id == medical_record_id)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.order_by(TCMPrescription.created_at.desc()).offset(skip).limit(limit))).scalars().all()
        return [TCMPrescriptionSchema.model_validate(r) for r in rows], int(total or 0)

    # ── 中药处方明细 ──
    async def create_tcm_prescription_item(self, data: dict, creator_id: Optional[str] = None) -> TCMPrescriptionItemSchema:
        obj = await self._persist(await self.prescription_item_crud.create(data), creator_id)
        return TCMPrescriptionItemSchema.model_validate(obj)

    async def get_tcm_prescription_items(self, tcm_prescription_id: str) -> list[TCMPrescriptionItemSchema]:
        stmt = select(TCMPrescriptionItem).where(
            TCMPrescriptionItem.deleted_at.is_(None), TCMPrescriptionItem.tcm_prescription_id == tcm_prescription_id
        )
        if self._tenant_id is not None:
            stmt = stmt.where(TCMPrescriptionItem.tenant_id == self._tenant_id)
        rows = (await self._db.execute(stmt)).scalars().all()
        return [TCMPrescriptionItemSchema.model_validate(r) for r in rows]

    # ── 中医方剂 ──
    async def create_tcm_formula(self, data: dict, creator_id: Optional[str] = None) -> TCMFormulaSchema:
        obj = await self._persist(await self.formula_crud.create(data), creator_id)
        return TCMFormulaSchema.model_validate(obj)

    async def list_tcm_formulas(self, search: Optional[str] = None, skip: int = 0, limit: int = 100) -> tuple[list[TCMFormulaSchema], int]:
        stmt = select(TCMFormula).where(TCMFormula.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(TCMFormula.tenant_id == self._tenant_id)
        if search:
            stmt = stmt.where(TCMFormula.name.ilike(f"%{search}%"))
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.offset(skip).limit(limit))).scalars().all()
        return [TCMFormulaSchema.model_validate(r) for r in rows], int(total or 0)

    # ── 煎药服务 ──
    async def create_decoction_service(self, data: dict, creator_id: Optional[str] = None) -> TCMDecoctionServiceSchema:
        obj = await self._persist(await self.decoction_crud.create(data), creator_id)
        return TCMDecoctionServiceSchema.model_validate(obj)

    async def get_decoction_service(self, service_id: str) -> TCMDecoctionServiceSchema:
        obj = await self.decoction_crud.get_or_404(id=service_id, out_schema=TCMDecoctionServiceSchema)
        return obj

    async def update_decoction_service(self, service_id: str, data: dict, updater_id: Optional[str] = None) -> TCMDecoctionServiceSchema:
        obj = await self.decoction_crud.update(service_id, data)
        uid = updater_id or self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return TCMDecoctionServiceSchema.model_validate(obj)
