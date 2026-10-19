"""
诊疗服务：病历管理和处方管理
"""
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from app.api.v1.module_treatment.model import MedicalRecord, Prescription
from app.repositories.treatment_repository import MedicalRecordRepository, PrescriptionRepository
from app.core.exceptions import NotFoundException
from app.core.logger import logger
from app.utils.common import generate_id


class TreatmentService:
    """诊疗服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.record_repo = MedicalRecordRepository(db)
        self.prescription_repo = PrescriptionRepository(db)
    
    # 病历管理
    def create_medical_record(
        self,
        record_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> MedicalRecord:
        """创建病历"""
        record = self.record_repo.create_medical_record(record_data, tenant_id)
        record.created_by = creator_id
        self.db.commit()
        
        # 如果有关联的挂号，自动更新挂号状态为"已完成"，并设置就诊时间
        if record.registration_id:
            try:
                from app.repositories.registration_repository import RegistrationRepository
                from datetime import datetime
                from uuid import UUID
                
                registration_repo = RegistrationRepository(self.db)
                registration_id_str = str(record.registration_id)
                registration = registration_repo.get_registration_by_id(registration_id_str, tenant_id)
                
                if registration and registration.status == "pending":
                    registration.status = "completed"
                    registration.visit_time = datetime.now()
                    self.db.commit()
                    logger.info(f"自动更新挂号状态为已完成: {registration_id_str}, 就诊时间: {registration.visit_time}")
            except Exception as e:
                logger.warning(f"更新挂号状态失败: {str(e)}", exc_info=True)
                # 不抛出异常，避免影响病历创建
        
        logger.info(f"创建病历: {record.id} by {creator_id}")
        return record
    
    def get_medical_record(self, record_id: str, tenant_id: str) -> MedicalRecord:
        """获取病历详情"""
        record = self.record_repo.get_medical_record_by_id(record_id, tenant_id)
        if not record:
            raise NotFoundException("病历", record_id)
        return record
    
    def list_medical_records(
        self,
        tenant_id: str,
        patient_id: Optional[str] = None,
        doctor_id: Optional[str] = None,
        registration_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[MedicalRecord], int]:
        """获取病历列表"""
        from datetime import date
        return self.record_repo.get_medical_records(
            tenant_id, patient_id, doctor_id, registration_id, start_date, end_date, skip, limit
        )
    
    def update_medical_record(
        self,
        record_id: str,
        tenant_id: str,
        record_data: Dict[str, Any],
        updater_id: str
    ) -> MedicalRecord:
        """更新病历"""
        record = self.record_repo.update_medical_record(record_id, tenant_id, record_data)
        record.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新病历: {record_id} by {updater_id}")
        return record
    
    # 处方管理
    def create_prescription(
        self,
        prescription_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> Prescription:
        """创建处方"""
        # 生成处方单号
        prescription_no = f"PRE{generate_id()[:8].upper()}"
        prescription_data["prescription_no"] = prescription_no
        
        prescription = self.prescription_repo.create_prescription(prescription_data, tenant_id)
        prescription.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建处方: {prescription.id} by {creator_id}")
        return prescription
    
    def get_prescription(self, prescription_id: str, tenant_id: str) -> Prescription:
        """获取处方详情"""
        prescription = self.prescription_repo.get_prescription_by_id(prescription_id, tenant_id)
        if not prescription:
            raise NotFoundException("处方", prescription_id)
        return prescription
    
    def list_prescriptions(
        self,
        tenant_id: str,
        patient_id: Optional[str] = None,
        doctor_id: Optional[str] = None,
        medical_record_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Prescription], int]:
        """获取处方列表"""
        return self.prescription_repo.get_prescriptions(
            tenant_id, patient_id, doctor_id, medical_record_id, status, skip, limit
        )
    
    def update_prescription(
        self,
        prescription_id: str,
        tenant_id: str,
        prescription_data: Dict[str, Any],
        updater_id: str
    ) -> Prescription:
        """更新处方"""
        prescription = self.prescription_repo.update_prescription(
            prescription_id, tenant_id, prescription_data
        )
        prescription.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新处方: {prescription_id} by {updater_id}")
        return prescription

