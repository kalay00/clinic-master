"""
第三方服务配置模块 ORM 模型（单一数据源）
"""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.db_types import JSONBType, ArrayType


class ThirdPartyConfig(Base):
    """
    第三方服务配置表
    每个租户可以为每种服务类型配置自己的参数
    """
    __tablename__ = "third_party_configs"
    
    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="主键ID"
    )
    
    # 租户ID
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="租户ID"
    )
    
    # 服务类型（aliyun_sms, alipay, wechat_pay, unionpay）
    service_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="服务类型"
    )
    
    # 服务名称（显示名称）
    service_name = Column(
        String(100),
        nullable=False,
        comment="服务名称"
    )
    
    # 是否启用
    is_enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用"
    )
    
    # 配置数据（JSON格式，敏感字段已加密）
    config_data = Column(
        JSONBType,
        nullable=False,
        comment="配置数据（JSON）"
    )
    
    # 需要加密的字段名列表（用于标识哪些字段需要加密存储）
    encrypted_fields = Column(
        ArrayType(String),
        nullable=True,
        comment="需要加密的字段名列表"
    )
    
    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="创建时间"
    )
    
    # 更新时间
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="更新时间"
    )
    
    # 创建人ID
    created_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="创建人ID"
    )
    
    # 更新人ID
    updated_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="更新人ID"
    )
    
    # 关系
    tenant = relationship("Tenant", backref="third_party_configs")
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "service_type", name="uq_tenant_service"),
        {"comment": "第三方服务配置表"},
    )
