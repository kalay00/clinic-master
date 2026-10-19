"""
患者数据仓库
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.api.v1.module_patient.model import Patient
from app.core.exceptions import NotFoundException


class PatientRepository:
    """患者数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_patient(self, patient_data: dict, tenant_id: str) -> Patient:
        """创建患者"""
        from uuid import UUID
        # 将tenant_id转换为UUID对象（如果模型使用UUID类型）
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        patient = Patient(
            tenant_id=tenant_id_uuid,
            **patient_data
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def get_patient_by_id(self, patient_id: str, tenant_id: str) -> Optional[Patient]:
        """根据ID获取患者"""
        from uuid import UUID
        # 将ID转换为UUID对象（如果模型使用UUID类型）
        if isinstance(patient_id, str):
            try:
                patient_id_uuid = UUID(patient_id)
            except (ValueError, TypeError):
                patient_id_uuid = patient_id
        else:
            patient_id_uuid = patient_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Patient).filter(
            and_(
                Patient.id == patient_id_uuid,
                Patient.tenant_id == tenant_id_uuid,
                Patient.deleted_at.is_(None)
            )
        ).first()
    
    def get_patients(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> tuple[List[Patient], int]:
        """获取患者列表"""
        from uuid import UUID
        # 将tenant_id转换为UUID对象（如果模型使用UUID类型）
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(Patient).filter(
            and_(
                Patient.tenant_id == tenant_id_uuid,
                Patient.deleted_at.is_(None)
            )
        )
        
        if search and search.strip():
            # 姓名/身份证号/手机号均支持模糊匹配（已改为明文存储）
            like = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Patient.patient_no.ilike(like),
                    Patient.name.ilike(like),
                    Patient.id_card.ilike(like),
                    Patient.phone.ilike(like),
                )
            )
        
        total = query.count()
        patients = query.offset(skip).limit(limit).all()
        return patients, total
    
    def update_patient(self, patient_id: str, tenant_id: str, patient_data: dict) -> Patient:
        """更新患者"""
        # get_patient_by_id已经处理了UUID转换
        patient = self.get_patient_by_id(patient_id, tenant_id)
        if not patient:
            raise NotFoundException("患者", patient_id)
        
        for key, value in patient_data.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        
        self.db.commit()
        self.db.refresh(patient)
        return patient
    
    def delete_patient(self, patient_id: str, tenant_id: str) -> bool:
        """删除患者（软删除）"""
        patient = self.get_patient_by_id(patient_id, tenant_id)
        if not patient:
            raise NotFoundException("患者", patient_id)
        
        patient.deleted_at = datetime.now()
        self.db.commit()
        return True
    
    def get_patient_by_id_card(self, id_card: str, tenant_id: str) -> Optional[Patient]:
        """根据身份证号获取患者（用于判断是否为复诊患者）"""
        from uuid import UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Patient).filter(
            and_(
                Patient.id_card == id_card,
                Patient.tenant_id == tenant_id_uuid,
                Patient.deleted_at.is_(None)
            )
        ).first()

