"""
用户多租户服务
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.api.v1.module_user.model import User
from app.api.v1.module_tenant.model import Tenant
from app.api.v1.module_tenant.model import UserTenant
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class UserTenantService:
    """用户多租户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_tenants(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户所属的所有租户
        
        Args:
            user_id: 用户ID（字符串或UUID）
        
        Returns:
            List[Dict[str, Any]]: 租户列表
        """
        from uuid import UUID
        
        # 将user_id转换为UUID对象（如果模型使用UUID类型）
        if isinstance(user_id, str):
            try:
                user_id_uuid = UUID(user_id)
            except (ValueError, TypeError):
                user_id_uuid = user_id
        else:
            user_id_uuid = user_id
        
        user_tenants = self.db.query(UserTenant).filter(
            UserTenant.user_id == user_id_uuid
        ).all()
        
        result = []
        for ut in user_tenants:
            tenant = self.db.query(Tenant).filter(
                Tenant.id == ut.tenant_id,
                Tenant.deleted_at.is_(None)
            ).first()
            
            if tenant:
                result.append({
                    "id": str(tenant.id),
                    "code": tenant.code,
                    "name": tenant.name,
                    "domain": tenant.domain,
                    "is_primary": ut.is_primary,
                    "last_accessed_at": ut.last_accessed_at.isoformat() if ut.last_accessed_at else None,
                })
        
        return result
    
    def add_user_to_tenant(self, user_id: str, tenant_id: str, is_primary: bool = False) -> UserTenant:
        """
        将用户添加到租户
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID
            is_primary: 是否为主要租户
        
        Returns:
            UserTenant: 关联对象
        """
        # 检查用户是否存在
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("用户", user_id)
        
        # 检查租户是否存在
        tenant = self.db.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.deleted_at.is_(None)
        ).first()
        if not tenant:
            raise NotFoundException("租户", tenant_id)
        
        # 检查关联是否已存在
        existing = self.db.query(UserTenant).filter(
            UserTenant.user_id == user_id,
            UserTenant.tenant_id == tenant_id
        ).first()
        
        if existing:
            raise BusinessException("用户已属于该租户", code=400)
        
        # 如果设置为主要租户，取消其他主要租户标记
        if is_primary:
            self.db.query(UserTenant).filter(
                UserTenant.user_id == user_id,
                UserTenant.is_primary == True
            ).update({"is_primary": False})
        
        user_tenant = UserTenant(
            user_id=user_id,
            tenant_id=tenant_id,
            is_primary=is_primary
        )
        self.db.add(user_tenant)
        self.db.commit()
        self.db.refresh(user_tenant)
        
        logger.info(f"用户 {user_id} 添加到租户 {tenant_id}")
        return user_tenant
    
    def remove_user_from_tenant(self, user_id: str, tenant_id: str) -> bool:
        """
        从租户中移除用户
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否成功
        """
        user_tenant = self.db.query(UserTenant).filter(
            UserTenant.user_id == user_id,
            UserTenant.tenant_id == tenant_id
        ).first()
        
        if not user_tenant:
            raise NotFoundException("用户租户关联", f"{user_id}-{tenant_id}")
        
        self.db.delete(user_tenant)
        self.db.commit()
        
        logger.info(f"用户 {user_id} 从租户 {tenant_id} 移除")
        return True
    
    def set_primary_tenant(self, user_id: str, tenant_id: str) -> bool:
        """
        设置用户的主要租户
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否成功
        """
        # 取消其他主要租户标记
        self.db.query(UserTenant).filter(
            UserTenant.user_id == user_id,
            UserTenant.is_primary == True
        ).update({"is_primary": False})
        
        # 设置新的主要租户
        user_tenant = self.db.query(UserTenant).filter(
            UserTenant.user_id == user_id,
            UserTenant.tenant_id == tenant_id
        ).first()
        
        if not user_tenant:
            raise NotFoundException("用户租户关联", f"{user_id}-{tenant_id}")
        
        user_tenant.is_primary = True
        self.db.commit()
        
        logger.info(f"设置用户 {user_id} 的主要租户为 {tenant_id}")
        return True
    
    def update_last_accessed(self, user_id: str, tenant_id: str) -> None:
        """
        更新用户最后访问租户的时间
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID
        """
        user_tenant = self.db.query(UserTenant).filter(
            UserTenant.user_id == user_id,
            UserTenant.tenant_id == tenant_id
        ).first()
        
        if user_tenant:
            user_tenant.last_accessed_at = datetime.now()
            self.db.commit()

