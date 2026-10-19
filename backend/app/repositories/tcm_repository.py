"""
中医相关数据仓库：诊断、中医诊断、四诊、治疗方法、处方等
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from app.api.v1.module_tcm.model import (
    Diagnosis, TCMDiagnosis, TCMFourExaminations, TCMTreatment,
    TCMPrescription, TCMPrescriptionItem, TCMFormula, TCMDecoctionService
)
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class DiagnosisRepository:
    """诊断数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_diagnosis(self, diagnosis_data: dict, tenant_id: str) -> Diagnosis:
        """创建诊断"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        diagnosis = Diagnosis(
            tenant_id=tenant_id,
            **diagnosis_data
        )
        self.db.add(diagnosis)
        self.db.commit()
        self.db.refresh(diagnosis)
        return diagnosis
    
    def get_diagnosis_by_id(self, diagnosis_id: str, tenant_id: str) -> Optional[Diagnosis]:
        """根据ID获取诊断"""
        if isinstance(diagnosis_id, str):
            diagnosis_id = UUID(diagnosis_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(Diagnosis).filter(
            and_(
                Diagnosis.id == diagnosis_id,
                Diagnosis.tenant_id == tenant_id,
                Diagnosis.deleted_at.is_(None)
            )
        ).first()
    
    def get_diagnoses_by_medical_record(
        self,
        medical_record_id: str,
        tenant_id: str
    ) -> List[Diagnosis]:
        """根据病历ID获取诊断列表"""
        if isinstance(medical_record_id, str):
            medical_record_id = UUID(medical_record_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(Diagnosis).filter(
            and_(
                Diagnosis.medical_record_id == medical_record_id,
                Diagnosis.tenant_id == tenant_id,
                Diagnosis.deleted_at.is_(None)
            )
        ).all()
    
    def update_diagnosis(
        self,
        diagnosis_id: str,
        tenant_id: str,
        diagnosis_data: dict
    ) -> Diagnosis:
        """更新诊断"""
        diagnosis = self.get_diagnosis_by_id(diagnosis_id, tenant_id)
        if not diagnosis:
            raise NotFoundException("诊断", diagnosis_id)
        
        for key, value in diagnosis_data.items():
            if hasattr(diagnosis, key):
                setattr(diagnosis, key, value)
        
        self.db.commit()
        self.db.refresh(diagnosis)
        return diagnosis
    
    def delete_diagnosis(self, diagnosis_id: str, tenant_id: str) -> bool:
        """删除诊断（软删除）"""
        diagnosis = self.get_diagnosis_by_id(diagnosis_id, tenant_id)
        if not diagnosis:
            raise NotFoundException("诊断", diagnosis_id)
        
        diagnosis.deleted_at = datetime.now()
        self.db.commit()
        return True


class TCMDiagnosisRepository:
    """中医诊断数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tcm_diagnosis(self, tcm_diagnosis_data: dict, tenant_id: str) -> TCMDiagnosis:
        """创建中医诊断"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        tcm_diagnosis = TCMDiagnosis(
            tenant_id=tenant_id,
            **tcm_diagnosis_data
        )
        self.db.add(tcm_diagnosis)
        self.db.commit()
        self.db.refresh(tcm_diagnosis)
        return tcm_diagnosis
    
    def get_tcm_diagnosis_by_id(self, tcm_diagnosis_id: str, tenant_id: str) -> Optional[TCMDiagnosis]:
        """根据ID获取中医诊断"""
        if isinstance(tcm_diagnosis_id, str):
            tcm_diagnosis_id = UUID(tcm_diagnosis_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(TCMDiagnosis).filter(
            and_(
                TCMDiagnosis.id == tcm_diagnosis_id,
                TCMDiagnosis.tenant_id == tenant_id,
                TCMDiagnosis.deleted_at.is_(None)
            )
        ).first()
    
    def get_tcm_diagnosis_by_medical_record(
        self,
        medical_record_id: str,
        tenant_id: str
    ) -> Optional[TCMDiagnosis]:
        """根据病历ID获取中医诊断"""
        if isinstance(medical_record_id, str):
            medical_record_id = UUID(medical_record_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(TCMDiagnosis).filter(
            and_(
                TCMDiagnosis.medical_record_id == medical_record_id,
                TCMDiagnosis.tenant_id == tenant_id,
                TCMDiagnosis.deleted_at.is_(None)
            )
        ).first()
    
    def update_tcm_diagnosis(
        self,
        tcm_diagnosis_id: str,
        tenant_id: str,
        tcm_diagnosis_data: dict
    ) -> TCMDiagnosis:
        """更新中医诊断"""
        tcm_diagnosis = self.get_tcm_diagnosis_by_id(tcm_diagnosis_id, tenant_id)
        if not tcm_diagnosis:
            raise NotFoundException("中医诊断", tcm_diagnosis_id)
        
        for key, value in tcm_diagnosis_data.items():
            if hasattr(tcm_diagnosis, key):
                setattr(tcm_diagnosis, key, value)
        
        self.db.commit()
        self.db.refresh(tcm_diagnosis)
        return tcm_diagnosis


class TCMFourExaminationsRepository:
    """中医四诊数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tcm_four_examinations(
        self,
        four_examinations_data: dict,
        tenant_id: str
    ) -> TCMFourExaminations:
        """创建中医四诊"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        four_examinations = TCMFourExaminations(
            tenant_id=tenant_id,
            **four_examinations_data
        )
        self.db.add(four_examinations)
        self.db.commit()
        self.db.refresh(four_examinations)
        return four_examinations
    
    def get_tcm_four_examinations_by_medical_record(
        self,
        medical_record_id: str,
        tenant_id: str
    ) -> Optional[TCMFourExaminations]:
        """根据病历ID获取中医四诊"""
        if isinstance(medical_record_id, str):
            medical_record_id = UUID(medical_record_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(TCMFourExaminations).filter(
            and_(
                TCMFourExaminations.medical_record_id == medical_record_id,
                TCMFourExaminations.tenant_id == tenant_id,
                TCMFourExaminations.deleted_at.is_(None)
            )
        ).first()
    
    def update_tcm_four_examinations(
        self,
        medical_record_id: str,
        tenant_id: str,
        four_examinations_data: dict
    ) -> TCMFourExaminations:
        """更新中医四诊"""
        four_examinations = self.get_tcm_four_examinations_by_medical_record(
            medical_record_id, tenant_id
        )
        if not four_examinations:
            raise NotFoundException("中医四诊", medical_record_id)
        
        for key, value in four_examinations_data.items():
            if hasattr(four_examinations, key):
                setattr(four_examinations, key, value)
        
        self.db.commit()
        self.db.refresh(four_examinations)
        return four_examinations


class TCMTreatmentRepository:
    """中医治疗方法数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tcm_treatment(self, treatment_data: dict, tenant_id: str) -> TCMTreatment:
        """创建中医治疗方法"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        treatment = TCMTreatment(
            tenant_id=tenant_id,
            **treatment_data
        )
        self.db.add(treatment)
        self.db.commit()
        self.db.refresh(treatment)
        return treatment
    
    def get_tcm_treatments_by_medical_record(
        self,
        medical_record_id: str,
        tenant_id: str
    ) -> List[TCMTreatment]:
        """根据病历ID获取中医治疗方法列表"""
        if isinstance(medical_record_id, str):
            medical_record_id = UUID(medical_record_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(TCMTreatment).filter(
            and_(
                TCMTreatment.medical_record_id == medical_record_id,
                TCMTreatment.tenant_id == tenant_id,
                TCMTreatment.deleted_at.is_(None)
            )
        ).all()
    
    def delete_tcm_treatment(self, treatment_id: str, tenant_id: str) -> bool:
        """删除中医治疗方法（软删除）"""
        if isinstance(treatment_id, str):
            treatment_id = UUID(treatment_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        treatment = self.db.query(TCMTreatment).filter(
            and_(
                TCMTreatment.id == treatment_id,
                TCMTreatment.tenant_id == tenant_id,
                TCMTreatment.deleted_at.is_(None)
            )
        ).first()
        
        if not treatment:
            raise NotFoundException("中医治疗方法", treatment_id)
        
        treatment.deleted_at = datetime.now()
        self.db.commit()
        return True


class TCMPrescriptionRepository:
    """中药处方数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tcm_prescription(
        self,
        prescription_data: dict,
        tenant_id: str
    ) -> TCMPrescription:
        """创建中药处方"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        prescription = TCMPrescription(
            tenant_id=tenant_id,
            **prescription_data
        )
        self.db.add(prescription)
        self.db.commit()
        self.db.refresh(prescription)
        return prescription
    
    def get_tcm_prescription_by_id(
        self,
        prescription_id: str,
        tenant_id: str
    ) -> Optional[TCMPrescription]:
        """根据ID获取中药处方"""
        if isinstance(prescription_id, str):
            prescription_id = UUID(prescription_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(TCMPrescription).filter(
            and_(
                TCMPrescription.id == prescription_id,
                TCMPrescription.tenant_id == tenant_id,
                TCMPrescription.deleted_at.is_(None)
            )
        ).first()
    
    def get_tcm_prescriptions(
        self,
        tenant_id: str,
        medical_record_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[TCMPrescription], int]:
        """获取中药处方列表"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        query = self.db.query(TCMPrescription).filter(
            and_(
                TCMPrescription.tenant_id == tenant_id,
                TCMPrescription.deleted_at.is_(None)
            )
        )
        
        if medical_record_id:
            if isinstance(medical_record_id, str):
                medical_record_id = UUID(medical_record_id)
            query = query.filter(TCMPrescription.medical_record_id == medical_record_id)
        
        total = query.count()
        prescriptions = query.offset(skip).limit(limit).all()
        return prescriptions, total


class TCMPrescriptionItemRepository:
    """中药处方明细数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tcm_prescription_item(
        self,
        item_data: dict,
        tenant_id: str
    ) -> TCMPrescriptionItem:
        """创建中药处方明细"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        item = TCMPrescriptionItem(
            tenant_id=tenant_id,
            **item_data
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
    
    def get_tcm_prescription_items_by_prescription(
        self,
        tcm_prescription_id: str,
        tenant_id: str
    ) -> List[TCMPrescriptionItem]:
        """根据处方ID获取明细列表"""
        if isinstance(tcm_prescription_id, str):
            tcm_prescription_id = UUID(tcm_prescription_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(TCMPrescriptionItem).filter(
            and_(
                TCMPrescriptionItem.tcm_prescription_id == tcm_prescription_id,
                TCMPrescriptionItem.tenant_id == tenant_id,
                TCMPrescriptionItem.deleted_at.is_(None)
            )
        ).all()


class TCMFormulaRepository:
    """中医方剂数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_tcm_formula(self, formula_data: dict, tenant_id: Optional[str] = None) -> TCMFormula:
        """创建中医方剂"""
        if tenant_id and isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        formula = TCMFormula(
            tenant_id=tenant_id,
            **formula_data
        )
        self.db.add(formula)
        self.db.commit()
        self.db.refresh(formula)
        return formula
    
    def get_tcm_formulas(
        self,
        tenant_id: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[TCMFormula], int]:
        """获取中医方剂列表"""
        query = self.db.query(TCMFormula).filter(
            TCMFormula.deleted_at.is_(None)
        )
        
        if tenant_id:
            if isinstance(tenant_id, str):
                tenant_id = UUID(tenant_id)
            query = query.filter(
                or_(
                    TCMFormula.tenant_id == tenant_id,
                    TCMFormula.tenant_id.is_(None)  # 系统方剂
                )
            )
        
        if search:
            query = query.filter(
                TCMFormula.formula_name.ilike(f"%{search}%")
            )
        
        total = query.count()
        formulas = query.offset(skip).limit(limit).all()
        return formulas, total


class TCMDecoctionServiceRepository:
    """中药煎药服务数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_decoction_service(
        self,
        service_data: dict,
        tenant_id: str
    ) -> TCMDecoctionService:
        """创建煎药服务"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        service = TCMDecoctionService(
            tenant_id=tenant_id,
            **service_data
        )
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service
    
    def get_decoction_service_by_id(
        self,
        service_id: str,
        tenant_id: str
    ) -> Optional[TCMDecoctionService]:
        """根据ID获取煎药服务"""
        if isinstance(service_id, str):
            service_id = UUID(service_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(TCMDecoctionService).filter(
            and_(
                TCMDecoctionService.id == service_id,
                TCMDecoctionService.tenant_id == tenant_id,
                TCMDecoctionService.deleted_at.is_(None)
            )
        ).first()
    
    def update_decoction_service(
        self,
        service_id: str,
        tenant_id: str,
        service_data: dict
    ) -> TCMDecoctionService:
        """更新煎药服务"""
        service = self.get_decoction_service_by_id(service_id, tenant_id)
        if not service:
            raise NotFoundException("煎药服务", service_id)
        
        for key, value in service_data.items():
            if hasattr(service, key):
                setattr(service, key, value)
        
        self.db.commit()
        self.db.refresh(service)
        return service

