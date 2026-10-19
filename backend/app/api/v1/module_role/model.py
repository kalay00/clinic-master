"""
角色权限模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel
from app.core.database import Base


class Role(BaseModel):
    """角色模型"""
    __tablename__ = "roles"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, comment="租户ID")
    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), nullable=False, comment="角色编码")
    description = Column(Text, comment="角色描述")
    is_system = Column(Boolean, default=False, comment="是否系统角色")
    
    # 关系
    tenant = relationship("Tenant", backref="roles")
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    
    __table_args__ = (
        {"comment": "角色表"},
    )


class Permission(BaseModel):
    """权限模型"""
    __tablename__ = "permissions"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, comment="租户ID（NULL表示系统权限）")
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), nullable=False, unique=True, comment="权限编码")
    resource = Column(String(50), nullable=False, comment="资源：patient/registration/treatment等")
    action = Column(String(50), nullable=False, comment="操作：create/read/update/delete")
    description = Column(Text, comment="权限描述")
    
    # 关系
    tenant = relationship("Tenant", backref="permissions")
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    __table_args__ = (
        {"comment": "权限表"},
    )


class UserRole(Base):
    """用户角色关联模型（关联表，不继承BaseModel）"""
    __tablename__ = "user_roles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, primary_key=True, comment="用户ID")
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, primary_key=True, comment="角色ID")
    
    __table_args__ = (
        {"comment": "用户角色关联表"},
    )


class RolePermission(Base):
    """角色权限关联模型（关联表，不继承BaseModel）"""
    __tablename__ = "role_permissions"
    
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False, primary_key=True, comment="角色ID")
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False, primary_key=True, comment="权限ID")
    
    __table_args__ = (
        {"comment": "角色权限关联表"},
    )
