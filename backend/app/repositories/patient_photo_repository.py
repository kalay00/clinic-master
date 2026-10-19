"""
患者照片数据仓库
v2.0新增功能
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from uuid import UUID

from app.api.v1.module_patient.model import PatientPhoto
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class PatientPhotoRepository:
    """患者照片数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_photo(self, photo_data: dict, tenant_id: str) -> PatientPhoto:
        """创建患者照片记录"""
        photo = PatientPhoto(
            tenant_id=tenant_id,
            **photo_data
        )
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo
    
    def get_photo_by_id(self, photo_id: str, tenant_id: str) -> Optional[PatientPhoto]:
        """根据ID获取患者照片"""
        if isinstance(photo_id, str):
            try:
                photo_id_uuid = UUID(photo_id)
            except (ValueError, TypeError):
                photo_id_uuid = photo_id
        else:
            photo_id_uuid = photo_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(PatientPhoto).filter(
            and_(
                PatientPhoto.id == photo_id_uuid,
                PatientPhoto.tenant_id == tenant_id_uuid,
                PatientPhoto.deleted_at.is_(None)
            )
        ).first()
    
    def get_photos_by_patient(
        self,
        patient_id: str,
        tenant_id: str,
        is_primary: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PatientPhoto], int]:
        """获取患者照片列表"""
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
        
        query = self.db.query(PatientPhoto).filter(
            and_(
                PatientPhoto.patient_id == patient_id_uuid,
                PatientPhoto.tenant_id == tenant_id_uuid,
                PatientPhoto.deleted_at.is_(None)
            )
        )
        
        if is_primary is not None:
            query = query.filter(PatientPhoto.is_primary == is_primary)
        
        total = query.count()
        photos = query.order_by(desc(PatientPhoto.is_primary), desc(PatientPhoto.created_at)).offset(skip).limit(limit).all()
        
        return photos, total
    
    def get_primary_photo(self, patient_id: str, tenant_id: str) -> Optional[PatientPhoto]:
        """获取患者主照片"""
        photos, _ = self.get_photos_by_patient(patient_id, tenant_id, is_primary=True, limit=1)
        return photos[0] if photos else None
    
    def update_photo(self, photo_id: str, photo_data: dict, tenant_id: str) -> PatientPhoto:
        """更新患者照片记录"""
        photo = self.get_photo_by_id(photo_id, tenant_id)
        if not photo:
            raise NotFoundException("患者照片", photo_id)
        
        for key, value in photo_data.items():
            if hasattr(photo, key):
                setattr(photo, key, value)
        
        self.db.commit()
        self.db.refresh(photo)
        return photo
    
    def delete_photo(self, photo_id: str, tenant_id: str) -> bool:
        """软删除患者照片记录"""
        photo = self.get_photo_by_id(photo_id, tenant_id)
        if not photo:
            raise NotFoundException("患者照片", photo_id)
        
        photo.deleted_at = datetime.now()
        self.db.commit()
        return True
    
    def set_primary_photo(self, photo_id: str, patient_id: str, tenant_id: str) -> PatientPhoto:
        """设置患者主照片"""
        # 先取消其他主照片
        photos, _ = self.get_photos_by_patient(patient_id, tenant_id)
        for photo in photos:
            if photo.id != UUID(photo_id) if isinstance(photo_id, str) else photo_id:
                photo.is_primary = False
        
        # 设置新的主照片
        photo = self.update_photo(photo_id, {"is_primary": True}, tenant_id)
        
        return photo

