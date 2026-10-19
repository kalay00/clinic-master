"""
用户模块 ORM 模型（单一数据源）
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, comment="租户ID")
    username = Column(String(50), nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), comment="真实姓名")
    phone = Column(String(255), comment="手机号")
    email = Column(String(100), comment="邮箱")
    avatar_url = Column(String(255), comment="头像URL")
    status = Column(String(20), default="active", comment="状态：active/inactive/locked")
    last_login_at = Column(DateTime, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")
    
    # 关系
    tenant = relationship("Tenant", backref="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    
    __table_args__ = (
        {"comment": "用户表"},
    )
