"""
安全增强组件：密钥轮换、数据级权限控制
v2.0新增功能
"""
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
import os
import base64

from app.core.encryption import EncryptionService
from app.core.config import settings
from app.core.logger import logger


class KeyRotationService:
    """密钥轮换服务"""
    
    def __init__(self):
        """初始化密钥轮换服务"""
        self.current_key = settings.ENCRYPTION_KEY
        self.key_history: List[Dict[str, Any]] = []
    
    def rotate_key(self, new_key: Optional[str] = None) -> str:
        """
        轮换加密密钥
        
        Args:
            new_key: 新密钥（如果不提供，自动生成）
        
        Returns:
            str: 新密钥
        """
        try:
            # 如果没有提供新密钥，生成一个随机密钥
            if not new_key:
                new_key = base64.b64encode(os.urandom(32)).decode('utf-8')
            
            # 记录旧密钥到历史记录
            self.key_history.append({
                'key': self.current_key,
                'rotated_at': datetime.now(),
                'active_until': datetime.now()
            })
            
            # 更新当前密钥
            old_key = self.current_key
            self.current_key = new_key
            
            logger.info(f"密钥轮换成功: 旧密钥已保存到历史记录")
            
            return new_key
        except Exception as e:
            logger.error(f"密钥轮换失败: {str(e)}")
            raise
    
    def get_current_key(self) -> str:
        """
        获取当前密钥
        
        Returns:
            str: 当前密钥
        """
        return self.current_key
    
    def get_key_history(self) -> List[Dict[str, Any]]:
        """
        获取密钥历史记录
        
        Returns:
            List[Dict]: 密钥历史记录
        """
        return self.key_history


class DataLevelPermissionService:
    """数据级权限控制服务"""
    
    @staticmethod
    def check_data_permission(
        user_id: UUID,
        resource_type: str,
        resource_id: UUID,
        action: str,
        db: Session,
        tenant_id: Optional[UUID] = None
    ) -> bool:
        """
        检查数据级权限
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型（patient/treatment/payment等）
            resource_id: 资源ID
            action: 操作类型（read/write/delete）
            db: 数据库会话
            tenant_id: 租户ID
        
        Returns:
            bool: 是否有权限
        """
        try:
            # TODO: 实现数据级权限检查逻辑
            # 这里先返回True，后续根据实际需求实现
            # 可以基于用户角色、数据所有者、数据共享规则等
            
            # 示例逻辑：
            # 1. 检查用户是否有该资源的访问权限
            # 2. 检查资源是否属于该用户或用户所属的组织
            # 3. 检查是否有数据共享规则允许访问
            
            logger.debug(
                f"数据级权限检查: user={user_id}, resource={resource_type}/{resource_id}, "
                f"action={action}, tenant={tenant_id}"
            )
            
            # 默认返回True，实际实现时需要根据业务规则判断
            return True
        except Exception as e:
            logger.error(f"数据级权限检查失败: {str(e)}")
            # 权限检查失败时，默认拒绝访问
            return False
    
    @staticmethod
    def get_user_accessible_resources(
        user_id: UUID,
        resource_type: str,
        db: Session,
        tenant_id: Optional[UUID] = None
    ) -> List[UUID]:
        """
        获取用户可访问的资源列表
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            db: 数据库会话
            tenant_id: 租户ID
        
        Returns:
            List[UUID]: 可访问的资源ID列表
        """
        try:
            # TODO: 实现获取用户可访问资源列表的逻辑
            # 这里先返回空列表，后续根据实际需求实现
            
            logger.debug(
                f"获取用户可访问资源: user={user_id}, resource_type={resource_type}, "
                f"tenant={tenant_id}"
            )
            
            return []
        except Exception as e:
            logger.error(f"获取用户可访问资源失败: {str(e)}")
            return []


class EnhancedEncryptionService(EncryptionService):
    """增强的加密服务（支持密钥轮换）"""
    
    def __init__(self, key: Optional[str] = None):
        """
        初始化增强加密服务
        
        Args:
            key: 加密密钥（如果不提供，从配置中读取）
        """
        super().__init__(key)
        self.key_rotation_service = KeyRotationService()
    
    def encrypt_with_key_version(self, plaintext: str, key_version: Optional[int] = None) -> Dict[str, Any]:
        """
        使用指定密钥版本加密数据
        
        Args:
            plaintext: 明文数据
            key_version: 密钥版本（如果不提供，使用当前密钥）
        
        Returns:
            Dict: 包含密文和密钥版本的信息
        """
        try:
            # 如果指定了密钥版本，从历史记录中获取对应密钥
            if key_version is not None and key_version < len(self.key_rotation_service.key_history):
                # 使用历史密钥加密（用于数据迁移场景）
                old_key_info = self.key_rotation_service.key_history[key_version]
                old_encryption = EncryptionService(key=old_key_info['key'])
                ciphertext = old_encryption.encrypt(plaintext)
            else:
                # 使用当前密钥加密
                ciphertext = self.encrypt(plaintext)
                key_version = len(self.key_rotation_service.key_history)
            
            return {
                'ciphertext': ciphertext,
                'key_version': key_version,
                'encrypted_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"使用密钥版本加密失败: {str(e)}")
            raise
    
    def decrypt_with_key_version(self, ciphertext: str, key_version: Optional[int] = None) -> str:
        """
        使用指定密钥版本解密数据
        
        Args:
            ciphertext: 密文数据
            key_version: 密钥版本（如果不提供，尝试所有密钥）
        
        Returns:
            str: 明文数据
        """
        try:
            # 如果指定了密钥版本，使用对应密钥解密
            if key_version is not None:
                if key_version < len(self.key_rotation_service.key_history):
                    # 使用历史密钥解密
                    old_key_info = self.key_rotation_service.key_history[key_version]
                    old_encryption = EncryptionService(key=old_key_info['key'])
                    return old_encryption.decrypt(ciphertext)
                else:
                    # 使用当前密钥解密
                    return self.decrypt(ciphertext)
            else:
                # 尝试使用当前密钥解密
                try:
                    return self.decrypt(ciphertext)
                except ValueError:
                    # 如果当前密钥解密失败，尝试历史密钥
                    for i, old_key_info in enumerate(self.key_rotation_service.key_history):
                        try:
                            old_encryption = EncryptionService(key=old_key_info['key'])
                            return old_encryption.decrypt(ciphertext)
                        except ValueError:
                            continue
                    
                    # 所有密钥都解密失败
                    raise ValueError("无法使用任何密钥解密数据")
        except Exception as e:
            logger.error(f"使用密钥版本解密失败: {str(e)}")
            raise


# 创建全局增强加密服务实例
enhanced_encryption_service = EnhancedEncryptionService()
key_rotation_service = KeyRotationService()
data_level_permission_service = DataLevelPermissionService()

