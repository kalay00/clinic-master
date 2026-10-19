"""
诊疗数据仓库：病历和处方的数据操作
"""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_

from app.api.v1.module_treatment.model import MedicalRecord, Prescription
from app.api.v1.module_registration.model import Registration
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class MedicalRecordRepository:
    """病历数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_medical_record(self, record_data: dict, tenant_id: str) -> MedicalRecord:
        """创建病历"""
        record = MedicalRecord(
            tenant_id=tenant_id,
            **record_data
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    def get_medical_record_by_id(self, record_id: str, tenant_id: str) -> Optional[MedicalRecord]:
        """根据ID获取病历"""
        return self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.id == record_id,
                MedicalRecord.tenant_id == tenant_id,
                MedicalRecord.deleted_at.is_(None)
            )
        ).first()
    
    def get_medical_records(
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
        from datetime import date as date_type
        from sqlalchemy import and_
        
        query = self.db.query(MedicalRecord).filter(
            and_(
                MedicalRecord.tenant_id == tenant_id,
                MedicalRecord.deleted_at.is_(None)
            )
        )
        
        if patient_id:
            query = query.filter(MedicalRecord.patient_id == patient_id)
        if doctor_id:
            query = query.filter(MedicalRecord.doctor_id == doctor_id)
        if registration_id:
            query = query.filter(MedicalRecord.registration_id == registration_id)
        if start_date:
            query = query.filter(MedicalRecord.created_at >= start_date)
        if end_date:
            # 确保包含end_date当天的所有记录
            from datetime import datetime, timedelta
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(MedicalRecord.created_at <= end_datetime)
        
        total = query.count()
        records = query.order_by(MedicalRecord.created_at.desc()).offset(skip).limit(limit).all()
        return records, total
    
    def update_medical_record(self, record_id: str, tenant_id: str, record_data: dict) -> MedicalRecord:
        """更新病历"""
        record = self.get_medical_record_by_id(record_id, tenant_id)
        if not record:
            raise NotFoundException("病历", record_id)
        
        for key, value in record_data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        
        self.db.commit()
        self.db.refresh(record)
        return record


class PrescriptionRepository:
    """处方数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_prescription(self, prescription_data: dict, tenant_id: str) -> Prescription:
        """创建处方"""
        prescription = Prescription(
            tenant_id=tenant_id,
            **prescription_data
        )
        self.db.add(prescription)
        self.db.commit()
        self.db.refresh(prescription)
        return prescription
    
    def get_prescription_by_id(self, prescription_id: str, tenant_id: str) -> Optional[Prescription]:
        """根据ID获取处方"""
        from sqlalchemy.orm import joinedload
        from uuid import UUID
        
        # 转换ID为UUID
        if isinstance(prescription_id, str):
            try:
                prescription_id_uuid = UUID(prescription_id)
            except (ValueError, TypeError):
                prescription_id_uuid = prescription_id
        else:
            prescription_id_uuid = prescription_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Prescription).options(
            joinedload(Prescription.patient),
            joinedload(Prescription.doctor),
            joinedload(Prescription.medical_record)
        ).filter(
            and_(
                Prescription.id == prescription_id_uuid,
                Prescription.tenant_id == tenant_id_uuid,
                Prescription.deleted_at.is_(None)
            )
        ).first()
    
    def get_prescriptions(
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
        from sqlalchemy.orm import joinedload
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        # 只加载medical_record，registration会在访问时自动加载（懒加载）
        # 或者使用selectinload加载所有medical_record的registration
        query = self.db.query(Prescription).options(
            joinedload(Prescription.patient),
            joinedload(Prescription.doctor),
            joinedload(Prescription.medical_record)
        ).filter(
            and_(
                Prescription.tenant_id == tenant_id_uuid,
                Prescription.deleted_at.is_(None)
            )
        )
        
        if patient_id:
            if isinstance(patient_id, str):
                try:
                    patient_id_uuid = UUID(patient_id)
                except (ValueError, TypeError):
                    patient_id_uuid = patient_id
            else:
                patient_id_uuid = patient_id
            query = query.filter(Prescription.patient_id == patient_id_uuid)
        if doctor_id:
            if isinstance(doctor_id, str):
                try:
                    doctor_id_uuid = UUID(doctor_id)
                except (ValueError, TypeError):
                    doctor_id_uuid = doctor_id
            else:
                doctor_id_uuid = doctor_id
            query = query.filter(Prescription.doctor_id == doctor_id_uuid)
        if medical_record_id:
            if isinstance(medical_record_id, str):
                try:
                    medical_record_id_uuid = UUID(medical_record_id)
                except (ValueError, TypeError):
                    medical_record_id_uuid = medical_record_id
            else:
                medical_record_id_uuid = medical_record_id
            query = query.filter(Prescription.medical_record_id == medical_record_id_uuid)
        if status:
            query = query.filter(Prescription.status == status)
        
        # 先计算总数
        total = query.count()
        
        # 按创建时间倒序排列（简单排序，避免复杂的关联查询）
        # 如果需要按挂号日期排序，可以在API层处理
        prescriptions = query.order_by(Prescription.created_at.desc()).offset(skip).limit(limit).all()
        return prescriptions, total
    
    def update_prescription(self, prescription_id: str, tenant_id: str, prescription_data: dict) -> Prescription:
        """更新处方"""
        prescription = self.get_prescription_by_id(prescription_id, tenant_id)
        if not prescription:
            raise NotFoundException("处方", prescription_id)
        
        for key, value in prescription_data.items():
            if hasattr(prescription, key):
                setattr(prescription, key, value)
        
        self.db.commit()
        self.db.refresh(prescription)
        return prescription

