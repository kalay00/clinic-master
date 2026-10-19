"""
中医服务：中医诊断、四诊、治疗方法、处方等
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID

from app.repositories.tcm_repository import (
    DiagnosisRepository, TCMDiagnosisRepository, TCMFourExaminationsRepository,
    TCMTreatmentRepository, TCMPrescriptionRepository, TCMPrescriptionItemRepository,
    TCMFormulaRepository, TCMDecoctionServiceRepository
)
from app.api.v1.module_tcm.model import (
    Diagnosis, TCMDiagnosis, TCMFourExaminations, TCMTreatment,
    TCMPrescription, TCMPrescriptionItem, TCMFormula, TCMDecoctionService
)
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class TCMService:
    """中医服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.diagnosis_repo = DiagnosisRepository(db)
        self.tcm_diagnosis_repo = TCMDiagnosisRepository(db)
        self.four_examinations_repo = TCMFourExaminationsRepository(db)
        self.treatment_repo = TCMTreatmentRepository(db)
        self.prescription_repo = TCMPrescriptionRepository(db)
        self.prescription_item_repo = TCMPrescriptionItemRepository(db)
        self.formula_repo = TCMFormulaRepository(db)
        self.decoction_service_repo = TCMDecoctionServiceRepository(db)
    
    # 诊断管理
    def create_diagnosis(
        self,
        diagnosis_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> Diagnosis:
        """创建诊断"""
        # 转换medical_record_id为UUID
        if "medical_record_id" in diagnosis_data:
            if isinstance(diagnosis_data["medical_record_id"], str):
                diagnosis_data["medical_record_id"] = UUID(diagnosis_data["medical_record_id"])
        
        diagnosis = self.diagnosis_repo.create_diagnosis(diagnosis_data, tenant_id)
        if creator_id:
            diagnosis.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
        self.db.commit()
        
        logger.info(f"创建诊断: {diagnosis.id} by {creator_id}")
        return diagnosis
    
    def get_diagnosis(self, diagnosis_id: str, tenant_id: str) -> Diagnosis:
        """获取诊断详情"""
        diagnosis = self.diagnosis_repo.get_diagnosis_by_id(diagnosis_id, tenant_id)
        if not diagnosis:
            raise NotFoundException("诊断", diagnosis_id)
        return diagnosis
    
    def get_diagnoses_by_medical_record(
        self,
        medical_record_id: str,
        tenant_id: str
    ) -> List[Diagnosis]:
        """根据病历获取诊断列表"""
        return self.diagnosis_repo.get_diagnoses_by_medical_record(medical_record_id, tenant_id)
    
    # 中医诊断管理
    def create_tcm_diagnosis(
        self,
        tcm_diagnosis_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> TCMDiagnosis:
        """创建中医诊断"""
        if "medical_record_id" in tcm_diagnosis_data:
            if isinstance(tcm_diagnosis_data["medical_record_id"], str):
                tcm_diagnosis_data["medical_record_id"] = UUID(tcm_diagnosis_data["medical_record_id"])
        
        tcm_diagnosis = self.tcm_diagnosis_repo.create_tcm_diagnosis(tcm_diagnosis_data, tenant_id)
        if creator_id:
            tcm_diagnosis.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
        self.db.commit()
        
        logger.info(f"创建中医诊断: {tcm_diagnosis.id} by {creator_id}")
        return tcm_diagnosis
    
    def get_tcm_diagnosis_by_medical_record(
        self,
        medical_record_id: str,
        tenant_id: str
    ) -> Optional[TCMDiagnosis]:
        """根据病历获取中医诊断"""
        return self.tcm_diagnosis_repo.get_tcm_diagnosis_by_medical_record(medical_record_id, tenant_id)
    
    # 中医四诊管理
    def create_or_update_tcm_four_examinations(
        self,
        four_examinations_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> TCMFourExaminations:
        """创建或更新中医四诊"""
        medical_record_id = four_examinations_data.get("medical_record_id")
        if not medical_record_id:
            raise BusinessException("medical_record_id不能为空")
        
        if isinstance(medical_record_id, str):
            medical_record_id = UUID(medical_record_id)
        
        # 检查是否已存在
        existing = self.four_examinations_repo.get_tcm_four_examinations_by_medical_record(
            str(medical_record_id), tenant_id
        )
        
        if existing:
            # 更新
            if isinstance(creator_id, str):
                creator_id = UUID(creator_id)
            four_examinations = self.four_examinations_repo.update_tcm_four_examinations(
                str(medical_record_id), tenant_id, four_examinations_data
            )
            four_examinations.updated_by = creator_id
            self.db.commit()
            return four_examinations
        else:
            # 创建
            four_examinations = self.four_examinations_repo.create_tcm_four_examinations(
                four_examinations_data, tenant_id
            )
            if creator_id:
                four_examinations.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
            self.db.commit()
            return four_examinations
    
    # 中医治疗方法管理
    def create_tcm_treatment(
        self,
        treatment_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> TCMTreatment:
        """创建中医治疗方法"""
        if "medical_record_id" in treatment_data:
            if isinstance(treatment_data["medical_record_id"], str):
                treatment_data["medical_record_id"] = UUID(treatment_data["medical_record_id"])
        
        treatment = self.treatment_repo.create_tcm_treatment(treatment_data, tenant_id)
        if creator_id:
            treatment.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
        self.db.commit()
        
        logger.info(f"创建中医治疗方法: {treatment.id} by {creator_id}")
        return treatment
    
    def get_tcm_treatments_by_medical_record(
        self,
        medical_record_id: str,
        tenant_id: str
    ) -> List[TCMTreatment]:
        """根据病历获取治疗方法列表"""
        return self.treatment_repo.get_tcm_treatments_by_medical_record(medical_record_id, tenant_id)
    
    # 中药处方管理
    def create_tcm_prescription(
        self,
        prescription_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> TCMPrescription:
        """创建中药处方"""
        # 转换UUID字段
        for field in ["prescription_id", "medical_record_id"]:
            if field in prescription_data and prescription_data[field]:
                if isinstance(prescription_data[field], str):
                    prescription_data[field] = UUID(prescription_data[field])
        
        prescription = self.prescription_repo.create_tcm_prescription(prescription_data, tenant_id)
        if creator_id:
            prescription.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
        self.db.commit()
        
        logger.info(f"创建中药处方: {prescription.id} by {creator_id}")
        return prescription
    
    def get_tcm_prescription(self, prescription_id: str, tenant_id: str) -> TCMPrescription:
        """获取中药处方详情"""
        prescription = self.prescription_repo.get_tcm_prescription_by_id(prescription_id, tenant_id)
        if not prescription:
            raise NotFoundException("中药处方", prescription_id)
        return prescription
    
    def list_tcm_prescriptions(
        self,
        tenant_id: str,
        medical_record_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[TCMPrescription], int]:
        """获取中药处方列表"""
        return self.prescription_repo.get_tcm_prescriptions(tenant_id, medical_record_id, skip, limit)
    
    # 中药处方明细管理
    def create_tcm_prescription_item(
        self,
        item_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> TCMPrescriptionItem:
        """创建中药处方明细"""
        # 转换UUID字段
        if "tcm_prescription_id" in item_data:
            if isinstance(item_data["tcm_prescription_id"], str):
                item_data["tcm_prescription_id"] = UUID(item_data["tcm_prescription_id"])
        if "drug_id" in item_data:
            if isinstance(item_data["drug_id"], str):
                item_data["drug_id"] = UUID(item_data["drug_id"])
        
        item = self.prescription_item_repo.create_tcm_prescription_item(item_data, tenant_id)
        if creator_id:
            item.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
        self.db.commit()
        
        return item
    
    def get_tcm_prescription_items(
        self,
        tcm_prescription_id: str,
        tenant_id: str
    ) -> List[TCMPrescriptionItem]:
        """获取中药处方明细列表"""
        return self.prescription_item_repo.get_tcm_prescription_items_by_prescription(
            tcm_prescription_id, tenant_id
        )
    
    # 中医方剂管理
    def create_tcm_formula(
        self,
        formula_data: Dict[str, Any],
        tenant_id: Optional[str],
        creator_id: str
    ) -> TCMFormula:
        """创建中医方剂"""
        formula = self.formula_repo.create_tcm_formula(formula_data, tenant_id)
        if creator_id:
            formula.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
        self.db.commit()
        
        logger.info(f"创建中医方剂: {formula.id} by {creator_id}")
        return formula
    
    def list_tcm_formulas(
        self,
        tenant_id: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[TCMFormula], int]:
        """获取中医方剂列表"""
        return self.formula_repo.get_tcm_formulas(tenant_id, search, skip, limit)
    
    # 煎药服务管理
    def create_decoction_service(
        self,
        service_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> TCMDecoctionService:
        """创建煎药服务"""
        if "tcm_prescription_id" in service_data:
            if isinstance(service_data["tcm_prescription_id"], str):
                service_data["tcm_prescription_id"] = UUID(service_data["tcm_prescription_id"])
        if "operator_id" in service_data and service_data["operator_id"]:
            if isinstance(service_data["operator_id"], str):
                service_data["operator_id"] = UUID(service_data["operator_id"])
        
        service = self.decoction_service_repo.create_decoction_service(service_data, tenant_id)
        if creator_id:
            service.created_by = UUID(creator_id) if isinstance(creator_id, str) else creator_id
        self.db.commit()
        
        logger.info(f"创建煎药服务: {service.id} by {creator_id}")
        return service
    
    def get_decoction_service(self, service_id: str, tenant_id: str) -> TCMDecoctionService:
        """获取煎药服务详情"""
        service = self.decoction_service_repo.get_decoction_service_by_id(service_id, tenant_id)
        if not service:
            raise NotFoundException("煎药服务", service_id)
        return service
    
    def update_decoction_service(
        self,
        service_id: str,
        tenant_id: str,
        service_data: Dict[str, Any],
        updater_id: str
    ) -> TCMDecoctionService:
        """更新煎药服务"""
        service = self.decoction_service_repo.update_decoction_service(
            service_id, tenant_id, service_data
        )
        if updater_id:
            service.updated_by = UUID(updater_id) if isinstance(updater_id, str) else updater_id
        self.db.commit()
        return service

