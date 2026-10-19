"""
第三方服务配置Repository
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.api.v1.module_third_party_config.model import ThirdPartyConfig


class ThirdPartyConfigRepository:
    """第三方服务配置Repository"""
    
    def __init__(self, db: Session):
        """
        初始化Repository
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def get_config(self, tenant_id, service_type: str) -> Optional[ThirdPartyConfig]:
        """
        获取租户的指定服务配置
        
        Args:
            tenant_id: 租户ID（可以是UUID或字符串）
            service_type: 服务类型
        
        Returns:
            ThirdPartyConfig: 配置对象，如果不存在返回None
        """
        # 转换tenant_id为UUID类型
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(ThirdPartyConfig).filter(
            and_(
                ThirdPartyConfig.tenant_id == tenant_id,
                ThirdPartyConfig.service_type == service_type
            )
        ).first()
    
    def get_all_configs(self, tenant_id) -> List[ThirdPartyConfig]:
        """
        获取租户的所有服务配置
        
        Args:
            tenant_id: 租户ID（可以是UUID或字符串）
        
        Returns:
            List[ThirdPartyConfig]: 配置列表
        """
        # 转换tenant_id为UUID类型
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(ThirdPartyConfig).filter(
            ThirdPartyConfig.tenant_id == tenant_id
        ).all()
    
    def create_config(self, config: ThirdPartyConfig) -> ThirdPartyConfig:
        """
        创建配置
        
        Args:
            config: 配置对象
        
        Returns:
            ThirdPartyConfig: 创建的配置对象
        """
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def update_config(self, config: ThirdPartyConfig) -> ThirdPartyConfig:
        """
        更新配置
        
        Args:
            config: 配置对象
        
        Returns:
            ThirdPartyConfig: 更新后的配置对象
        """
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def delete_config(self, tenant_id, service_type: str) -> bool:
        """
        删除配置
        
        Args:
            tenant_id: 租户ID（可以是UUID或字符串）
            service_type: 服务类型
        
        Returns:
            bool: 是否成功删除
        """
        config = self.get_config(tenant_id, service_type)
        if config:
            self.db.delete(config)
            self.db.commit()
            return True
        return False

