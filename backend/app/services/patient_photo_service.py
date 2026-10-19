"""
患者照片服务
v2.0新增功能
"""
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import uuid
import os
from PIL import Image
from sqlalchemy.orm import Session

from app.api.v1.module_patient.model import PatientPhoto
from app.repositories.patient_photo_repository import PatientPhotoRepository
from app.services.patient_service import PatientService
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger
from app.core.config import settings


class PatientPhotoService:
    """患者照片服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.photo_repo = PatientPhotoRepository(db)
        self.patient_service = PatientService(db)
    
    def upload_photo(
        self,
        patient_id: str,
        file_content: bytes,
        file_name: str,
        file_type: str,
        tenant_id: str,
        creator_id: str,
        is_primary: bool = False,
        description: Optional[str] = None
    ) -> PatientPhoto:
        """
        上传患者照片
        
        Args:
            patient_id: 患者ID
            file_content: 文件内容（字节）
            file_name: 文件名
            file_type: 文件类型
            tenant_id: 租户ID
            creator_id: 创建人ID
            is_primary: 是否为主照片
            description: 照片描述
        
        Returns:
            PatientPhoto: 患者照片记录
        """
        try:
            # 验证患者是否存在
            patient = self.patient_service.get_patient(patient_id, tenant_id)
            if not patient:
                raise NotFoundException("患者", patient_id)
            
            # 验证文件类型
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
            if file_type not in allowed_types:
                raise BusinessException(f"不支持的文件类型: {file_type}，支持的格式：{', '.join(allowed_types)}")
            
            # 验证文件大小
            file_size = len(file_content)
            max_size = settings.MAX_UPLOAD_SIZE
            if file_size > max_size:
                raise BusinessException(f"文件大小超过限制: {file_size} bytes，最大允许：{max_size} bytes")
            
            # 生成唯一文件名
            file_ext = Path(file_name).suffix.lower()
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            
            # 确定保存路径
            upload_dir = self._get_upload_dir()
            patient_dir = upload_dir / "patients" / str(patient_id)
            patient_dir.mkdir(parents=True, exist_ok=True)
            
            save_path = patient_dir / unique_filename
            
            # 保存文件
            with open(save_path, "wb") as f:
                f.write(file_content)
            
            # 获取图片尺寸
            width, height = None, None
            try:
                with Image.open(save_path) as img:
                    width, height = img.size
            except Exception as e:
                logger.warning(f"获取图片尺寸失败: {str(e)}")
            
            # 生成访问URL
            photo_url = f"/uploads/patients/{patient_id}/{unique_filename}"
            
            # 创建照片记录
            photo_data = {
                "patient_id": patient_id,
                "photo_url": photo_url,
                "photo_path": str(save_path),
                "file_name": unique_filename,
                "file_size": file_size,
                "file_type": file_type,
                "width": width,
                "height": height,
                "is_primary": is_primary,
                "description": description,
            }
            
            photo = self.photo_repo.create_photo(photo_data, tenant_id)
            photo.created_by = creator_id
            self.db.commit()
            
            # 如果设置为主照片，需要取消其他主照片
            if is_primary:
                self.set_primary_photo(str(photo.id), patient_id, tenant_id)
            
            logger.info(f"上传患者照片成功: patient_id={patient_id}, photo_id={photo.id}")
            
            return photo
            
        except Exception as e:
            logger.error(f"上传患者照片失败: patient_id={patient_id}, error={str(e)}")
            raise
    
    def get_photo(self, photo_id: str, tenant_id: str) -> PatientPhoto:
        """
        获取患者照片详情
        
        Args:
            photo_id: 照片ID
            tenant_id: 租户ID
        
        Returns:
            PatientPhoto: 患者照片记录
        """
        photo = self.photo_repo.get_photo_by_id(photo_id, tenant_id)
        if not photo:
            raise NotFoundException("患者照片", photo_id)
        return photo
    
    def list_photos(
        self,
        patient_id: str,
        tenant_id: str,
        is_primary: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[PatientPhoto], int]:
        """
        获取患者照片列表
        
        Args:
            patient_id: 患者ID
            tenant_id: 租户ID
            is_primary: 是否为主照片（可选）
            skip: 跳过数量
            limit: 返回数量
        
        Returns:
            Tuple[List[PatientPhoto], int]: 照片列表和总数
        """
        return self.photo_repo.get_photos_by_patient(patient_id, tenant_id, is_primary, skip, limit)
    
    def get_primary_photo(self, patient_id: str, tenant_id: str) -> Optional[PatientPhoto]:
        """
        获取患者主照片
        
        Args:
            patient_id: 患者ID
            tenant_id: 租户ID
        
        Returns:
            Optional[PatientPhoto]: 主照片记录，如果没有则返回None
        """
        return self.photo_repo.get_primary_photo(patient_id, tenant_id)
    
    def set_primary_photo(
        self,
        photo_id: str,
        patient_id: str,
        tenant_id: str,
        updater_id: str
    ) -> PatientPhoto:
        """
        设置患者主照片
        
        Args:
            photo_id: 照片ID
            patient_id: 患者ID
            tenant_id: 租户ID
            updater_id: 更新人ID
        
        Returns:
            PatientPhoto: 更新后的照片记录
        """
        photo = self.photo_repo.set_primary_photo(photo_id, patient_id, tenant_id)
        photo.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"设置患者主照片: patient_id={patient_id}, photo_id={photo_id}")
        
        return photo
    
    def delete_photo(self, photo_id: str, tenant_id: str) -> bool:
        """
        删除患者照片
        
        Args:
            photo_id: 照片ID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否删除成功
        """
        try:
            # 获取照片记录
            photo = self.get_photo(photo_id, tenant_id)
            
            # 删除文件
            if photo.photo_path and os.path.exists(photo.photo_path):
                try:
                    os.remove(photo.photo_path)
                    logger.info(f"删除照片文件: {photo.photo_path}")
                except Exception as e:
                    logger.warning(f"删除照片文件失败: {photo.photo_path}, error={str(e)}")
            
            # 软删除记录
            self.photo_repo.delete_photo(photo_id, tenant_id)
            
            logger.info(f"删除患者照片成功: photo_id={photo_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"删除患者照片失败: photo_id={photo_id}, error={str(e)}")
            raise
    
    def _get_upload_dir(self) -> Path:
        """
        获取上传文件存储目录
        
        Returns:
            Path: 上传目录路径
        """
        project_root = Path(__file__).resolve().parents[3].parent
        upload_dir = project_root / settings.UPLOAD_DIR
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

