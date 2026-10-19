"""
患者服务
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.api.v1.module_patient.model import Patient
from app.repositories.patient_repository import PatientRepository
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class PatientService:
    """患者服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.patient_repo = PatientRepository(db)
    
    def create_patient(self, patient_data: Dict[str, Any], tenant_id: str, creator_id: str) -> Patient:
        """创建患者"""
        # 验证身份证号必填
        if "id_card" not in patient_data or not patient_data.get("id_card"):
            raise ValueError("身份证号是必填项，所有患者必须以身份证号建立就诊档案")
        
        # 检查是否已存在相同身份证号的患者
        existing_patient = self.patient_repo.get_patient_by_id_card(patient_data["id_card"], tenant_id)

        # 严格唯一：同一租户下身份证号不可重复，若已存在则拒绝新建
        if existing_patient:
            raise BusinessException("身份证号已存在，请勿重复建档", code=400)

        # 生成档案号（如果未提供）
        if "patient_no" not in patient_data or not patient_data.get("patient_no"):
            from app.utils.common import generate_id
            generated_id = generate_id()
            # 移除UUID中的连字符，取前8个字符
            clean_id = generated_id.replace("-", "")[:8]
            patient_data["patient_no"] = f"P{clean_id.upper()}"
            logger.debug(f"初诊患者，生成档案号: {patient_data['patient_no']}")
        
        # 转换birthday字符串为date对象
        if "birthday" in patient_data and isinstance(patient_data["birthday"], str):
            from datetime import datetime
            try:
                patient_data["birthday"] = datetime.strptime(patient_data["birthday"], "%Y-%m-%d").date()
            except ValueError:
                # 尝试其他格式
                try:
                    patient_data["birthday"] = datetime.strptime(patient_data["birthday"], "%Y/%m/%d").date()
                except ValueError:
                    pass  # 如果无法解析，保留原值
        

        # 确保patient_no存在
        if "patient_no" not in patient_data or not patient_data.get("patient_no"):
            from app.utils.common import generate_id
            generated_id = generate_id()
            clean_id = generated_id.replace("-", "")[:8]
            patient_data["patient_no"] = f"P{clean_id.upper()}"
        
        logger.debug(f"创建患者前检查: patient_no={patient_data.get('patient_no')}")
        patient = self.patient_repo.create_patient(patient_data, tenant_id)
        
        # 确保creator_id是UUID对象
        from uuid import UUID
        if isinstance(creator_id, str):
            try:
                creator_id_uuid = UUID(creator_id)
            except (ValueError, TypeError):
                creator_id_uuid = creator_id
        else:
            creator_id_uuid = creator_id
        
        patient.created_by = creator_id_uuid
        self.db.commit()
        
        logger.info(f"创建患者: {patient.id} by {creator_id}")
        return patient
    
    def get_patient(self, patient_id: str, tenant_id: str) -> Patient:
        """获取患者详情"""
        patient = self.patient_repo.get_patient_by_id(patient_id, tenant_id)
        if not patient:
            raise NotFoundException("患者", patient_id)
        return patient
    
    def list_patients(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> tuple[List[Patient], int]:
        """获取患者列表"""
        return self.patient_repo.get_patients(tenant_id, skip, limit, search)
    
    def update_patient(
        self,
        patient_id: str,
        tenant_id: str,
        patient_data: Dict[str, Any],
        updater_id: str
    ) -> Patient:
        """更新患者"""
        # 明文存储：无需加密
        if "id_card" in patient_data:
            # 严格唯一：若身份证号变更且被其他患者占用，则拒绝
            current = self.patient_repo.get_patient_by_id(patient_id, tenant_id)
            if current is None or current.id_card != patient_data["id_card"]:
                dup = self.patient_repo.get_patient_by_id_card(patient_data["id_card"], tenant_id)
                if dup is not None and str(dup.id) != str(patient_id):
                    raise BusinessException("身份证号已存在，请勿重复建档", code=400)
        
        patient = self.patient_repo.update_patient(patient_id, tenant_id, patient_data)
        
        # 确保updater_id是UUID对象
        from uuid import UUID
        if isinstance(updater_id, str):
            try:
                updater_id_uuid = UUID(updater_id)
            except (ValueError, TypeError):
                updater_id_uuid = updater_id
        else:
            updater_id_uuid = updater_id
        
        patient.updated_by = updater_id_uuid
        self.db.commit()
        
        logger.info(f"更新患者: {patient_id} by {updater_id}")
        return patient
    
    def delete_patient(self, patient_id: str, tenant_id: str, deleter_id: str) -> bool:
        """删除患者"""
        result = self.patient_repo.delete_patient(patient_id, tenant_id)
        logger.info(f"删除患者: {patient_id} by {deleter_id}")
        return result
    
    def decrypt_patient_data(self, patient: Patient) -> Dict[str, Any]:
        """序列化患者数据（明文字段）"""
        from datetime import date

        data = {
            "id": str(patient.id),
            "patient_no": patient.patient_no,
            "name": patient.name,
            "id_card": patient.id_card,
            "phone": patient.phone,
            "gender": patient.gender,
            "birthday": patient.birthday.isoformat() if patient.birthday else None,
            "birth_date": patient.birthday.isoformat() if patient.birthday else None,  # 兼容前端
            "address": patient.address,
            "emergency_contact": patient.emergency_contact,
            "emergency_phone": patient.emergency_phone,
            "allergy_history": patient.allergy_history,
            "chronic_disease": patient.chronic_disease,
            "blood_type": patient.blood_type,
            "remark": patient.remark,
            "created_at": patient.created_at.isoformat() if patient.created_at else None,
        }

        # 计算年龄
        if patient.birthday:
            today = date.today()
            age = today.year - patient.birthday.year
            if (today.month, today.day) < (patient.birthday.month, patient.birthday.day):
                age -= 1
            data["age"] = age

        return data

