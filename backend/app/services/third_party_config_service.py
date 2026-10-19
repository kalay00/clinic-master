"""
第三方服务配置服务
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.repositories.third_party_config_repository import ThirdPartyConfigRepository
from app.api.v1.module_third_party_config.model import ThirdPartyConfig
from app.core.encryption import EncryptionService
from app.core.exceptions import BusinessException, NotFoundException
from app.core.logger import logger


class ThirdPartyConfigService:
    """第三方服务配置服务"""
    
    # 服务类型定义
    SERVICE_TYPES = {
        "aliyun_sms": {
            "name": "阿里云短信",
            "encrypted_fields": ["access_key_id", "access_key_secret"],
            "required_fields": ["access_key_id", "access_key_secret", "sign_name", "template_code"],
        },
        "alipay": {
            "name": "支付宝",
            "encrypted_fields": ["app_private_key", "alipay_public_key"],
            "required_fields": ["app_id", "app_private_key", "alipay_public_key", "sign_type"],
        },
        "wechat_pay": {
            "name": "微信支付",
            "encrypted_fields": ["api_key", "app_secret"],
            "required_fields": ["app_id", "mch_id", "api_key"],
        },
        "unionpay": {
            "name": "银联支付",
            "encrypted_fields": ["mer_key"],
            "required_fields": ["mer_id", "mer_key"],
        },
    }
    
    def __init__(self, db: Session):
        """
        初始化服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.repo = ThirdPartyConfigRepository(db)
        self.encryption = EncryptionService()
    
    def get_config(self, tenant_id, service_type: str) -> Optional[Dict[str, Any]]:
        """
        获取配置（已解密）
        
        Args:
            tenant_id: 租户ID（可以是UUID或字符串）
            service_type: 服务类型
        
        Returns:
            Dict[str, Any]: 配置数据（已解密），如果不存在返回None
        """
        # 转换tenant_id为UUID类型
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        config = self.repo.get_config(tenant_id, service_type)
        if not config:
            return None
        
        return self.decrypt_config(config)
    
    def get_all_configs(self, tenant_id) -> List[Dict[str, Any]]:
        """
        获取所有配置（已解密）
        
        Args:
            tenant_id: 租户ID（可以是UUID或字符串）
        
        Returns:
            List[Dict[str, Any]]: 配置列表（已解密）
        """
        # 转换tenant_id为UUID类型
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        configs = self.repo.get_all_configs(tenant_id)
        return [self.decrypt_config(config) for config in configs]
    
    def save_config(
        self,
        tenant_id,
        service_type: str,
        config_data: Dict[str, Any],
        creator_id
    ) -> Dict[str, Any]:
        """
        保存配置（加密敏感字段）
        
        Args:
            tenant_id: 租户ID
            service_type: 服务类型
            config_data: 配置数据
            creator_id: 创建人ID
        
        Returns:
            Dict[str, Any]: 保存后的配置（已解密）
        
        Raises:
            BusinessException: 配置验证失败
        """
        # 转换tenant_id和creator_id为UUID类型
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        if isinstance(creator_id, str):
            creator_id = UUID(creator_id)
        
        # 验证服务类型
        if service_type not in self.SERVICE_TYPES:
            raise BusinessException(f"不支持的服务类型: {service_type}")
        
        # 验证必填字段
        service_info = self.SERVICE_TYPES[service_type]
        for field in service_info["required_fields"]:
            if field not in config_data or not config_data[field]:
                raise BusinessException(f"缺少必填字段: {field}")
        
        # 加密敏感字段
        encrypted_config = self.encrypt_config(config_data, service_info["encrypted_fields"])
        
        # 查找现有配置
        existing_config = self.repo.get_config(tenant_id, service_type)
        
        if existing_config:
            # 更新现有配置
            existing_config.config_data = encrypted_config
            existing_config.is_enabled = config_data.get("is_enabled", True)
            existing_config.updated_by = creator_id
            config = self.repo.update_config(existing_config)
        else:
            # 创建新配置
            config = ThirdPartyConfig(
                tenant_id=tenant_id,
                service_type=service_type,
                service_name=service_info["name"],
                is_enabled=config_data.get("is_enabled", True),
                config_data=encrypted_config,
                encrypted_fields=service_info["encrypted_fields"],
                created_by=creator_id,
                updated_by=creator_id,
            )
            config = self.repo.create_config(config)
        
        return self.decrypt_config(config)
    
    def delete_config(self, tenant_id, service_type: str) -> bool:
        """
        删除配置
        
        Args:
            tenant_id: 租户ID（可以是UUID或字符串）
            service_type: 服务类型
        
        Returns:
            bool: 是否成功删除
        """
        # 转换tenant_id为UUID类型
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.repo.delete_config(tenant_id, service_type)
    
    def encrypt_config(self, config_data: Dict[str, Any], encrypted_fields: List[str]) -> Dict[str, Any]:
        """
        加密配置中的敏感字段
        
        Args:
            config_data: 原始配置数据
            encrypted_fields: 需要加密的字段列表
        
        Returns:
            Dict[str, Any]: 加密后的配置数据
        """
        encrypted_config = config_data.copy()
        
        for field in encrypted_fields:
            if field in encrypted_config and encrypted_config[field]:
                # 如果已经是加密格式（以encrypted_开头），跳过
                if isinstance(encrypted_config[field], str) and encrypted_config[field].startswith("encrypted_"):
                    continue
                # 加密字段值
                encrypted_config[field] = self.encryption.encrypt(str(encrypted_config[field]))
        
        return encrypted_config
    
    def decrypt_config(self, config: ThirdPartyConfig) -> Dict[str, Any]:
        """
        解密配置中的敏感字段
        
        Args:
            config: 配置对象
        
        Returns:
            Dict[str, Any]: 解密后的配置数据
        """
        # 安全地复制config_data
        if config.config_data is None:
            config_data = {}
        elif isinstance(config.config_data, dict):
            config_data = config.config_data.copy()
        else:
            # 如果config_data不是字典，尝试转换
            try:
                import json
                if isinstance(config.config_data, str):
                    config_data = json.loads(config.config_data)
                else:
                    config_data = dict(config.config_data)
            except Exception as e:
                logger.warning(f"解析config_data失败: {str(e)}")
                config_data = {}
        
        encrypted_fields = config.encrypted_fields or []
        for field in encrypted_fields:
            if field in config_data and config_data[field]:
                try:
                    # 尝试解密
                    config_data[field] = self.encryption.decrypt(config_data[field])
                except Exception as e:
                    logger.warning(f"解密字段 {field} 失败: {str(e)}")
                    # 如果解密失败，保持原值（可能是已经是明文）
                    pass
        
        return {
            "id": str(config.id),
            "tenant_id": str(config.tenant_id),
            "service_type": config.service_type,
            "service_name": config.service_name,
            "is_enabled": config.is_enabled,
            "config_data": config_data,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None,
        }
    
    def validate_config(self, service_type: str, config_data: Dict[str, Any]) -> bool:
        """
        验证配置数据
        
        Args:
            service_type: 服务类型
            config_data: 配置数据
        
        Returns:
            bool: 是否有效
        
        Raises:
            BusinessException: 配置无效
        """
        if service_type not in self.SERVICE_TYPES:
            raise BusinessException(f"不支持的服务类型: {service_type}")
        
        service_info = self.SERVICE_TYPES[service_type]
        
        # 检查必填字段
        for field in service_info["required_fields"]:
            if field not in config_data or not config_data[field]:
                raise BusinessException(f"缺少必填字段: {field}")
        
        return True

