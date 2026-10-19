"""
租户模块 ORM 模型（单一数据源）
"""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.db_types import JSONBType


class Tenant(Base):
    """
    租户表（机构表）
    注意：租户表不需要tenant_id字段，因为它是租户本身
    """
    __tablename__ = "tenants"
    
    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="主键ID"
    )
    
    # 机构名称
    name = Column(
        String(100),
        nullable=False,
        comment="机构名称"
    )
    
    # 机构编码（唯一）
    code = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="机构编码"
    )
    
    # 机构类型
    type = Column(
        String(20),
        nullable=False,
        comment="机构类型：clinic/hospital"
    )
    
    # 联系人
    contact_name = Column(
        String(50),
        nullable=True,
        comment="联系人"
    )
    
    # 联系电话
    contact_phone = Column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    
    # 联系邮箱
    contact_email = Column(
        String(100),
        nullable=True,
        comment="联系邮箱"
    )
    
    # 地址
    address = Column(
        Text,
        nullable=True,
        comment="地址"
    )
    
    # 状态
    status = Column(
        String(20),
        nullable=False,
        default="active",
        index=True,
        comment="状态：active/inactive"
    )
    
    # 订阅计划
    subscription_plan = Column(
        String(20),
        nullable=True,
        comment="订阅计划"
    )
    
    # 到期时间
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="到期时间"
    )
    
    # 配置信息（JSON）
    config = Column(
        JSONBType,
        nullable=True,
        comment="配置信息（JSON）"
    )
    
    # 租户域名（用于域名识别）
    domain = Column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
        comment="租户域名（如：test001.his.example.com）"
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
    
    # 删除时间（软删除）
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )


class UserTenant(Base):
    """用户租户关联模型"""
    __tablename__ = "user_tenants"
    
    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="主键ID"
    )
    
    # 用户ID
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    
    # 租户ID
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="租户ID"
    )
    
    # 是否为主要租户
    is_primary = Column(
        Boolean,
        default=False,
        comment="是否为主要租户"
    )
    
    # 最后访问时间
    last_accessed_at = Column(
        DateTime(timezone=True),
        comment="最后访问时间"
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
    
    # 唯一约束：用户和租户组合唯一
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant"),
        {"comment": "用户租户关联表"},
    )
