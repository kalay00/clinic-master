"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, computed_field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr


class UserSchema(BaseSchema):
    """User Schema"""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(..., comment="租户ID")
    username: str = Field(..., comment="用户名")
    password_hash: str = Field(..., comment="密码哈希")
    real_name: Optional[str] = Field(default=None, comment="真实姓名")
    phone: Optional[str] = Field(default=None, comment="手机号（加密）")
    email: Optional[str] = Field(default=None, comment="邮箱")
    avatar_url: Optional[str] = Field(default=None, comment="头像URL")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive/locked")
    last_login_at: Optional[DateTimeStr] = Field(default=None, comment="最后登录时间")
    last_login_ip: Optional[str] = Field(default=None, comment="最后登录IP")

    @computed_field
    @property
    def roles(self) -> List[str]:
        # 列表接口会按用户聚合真实角色名注入；此处仅作为序列化占位，不参与 ORM 属性读取
        return []


class UserCreateSchema(BaseModel):
    """User CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., comment="用户名")
    password_hash: str = Field(..., comment="密码哈希")
    real_name: Optional[str] = Field(default=None, comment="真实姓名")
    phone: Optional[str] = Field(default=None, comment="手机号（加密）")
    email: Optional[str] = Field(default=None, comment="邮箱")
    avatar_url: Optional[str] = Field(default=None, comment="头像URL")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive/locked")
    last_login_at: Optional[DateTimeStr] = Field(default=None, comment="最后登录时间")
    last_login_ip: Optional[str] = Field(default=None, comment="最后登录IP")


class UserUpdateSchema(BaseModel):
    """User UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., comment="用户名")
    password_hash: Optional[str] = Field(default=None, comment="密码哈希（编辑时可选，不传则不修改密码）")
    real_name: Optional[str] = Field(default=None, comment="真实姓名")
    phone: Optional[str] = Field(default=None, comment="手机号（加密）")
    email: Optional[str] = Field(default=None, comment="邮箱")
    avatar_url: Optional[str] = Field(default=None, comment="头像URL")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive/locked")
    last_login_at: Optional[DateTimeStr] = Field(default=None, comment="最后登录时间")
    last_login_ip: Optional[str] = Field(default=None, comment="最后登录IP")


class RoleSchema(BaseSchema):
    """Role Schema"""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(..., comment="租户ID")
    name: str = Field(..., comment="角色名称")
    code: str = Field(..., comment="角色编码")
    description: Optional[str] = Field(default=None, comment="角色描述")
    is_system: Optional[bool] = Field(default=None, comment="是否系统角色")


class RoleCreateSchema(BaseModel):
    """Role CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="角色名称")
    code: str = Field(..., comment="角色编码")
    description: Optional[str] = Field(default=None, comment="角色描述")
    is_system: Optional[bool] = Field(default=None, comment="是否系统角色")


class RoleUpdateSchema(BaseModel):
    """Role UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="角色名称")
    code: str = Field(..., comment="角色编码")
    description: Optional[str] = Field(default=None, comment="角色描述")
    is_system: Optional[bool] = Field(default=None, comment="是否系统角色")


class PermissionSchema(BaseSchema):
    """Permission Schema"""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: Optional[UUID] = Field(default=None, comment="租户ID（NULL表示系统权限）")
    name: str = Field(..., comment="权限名称")
    code: str = Field(..., comment="权限编码")
    resource: str = Field(..., comment="资源：patient/registration/treatment等")
    action: str = Field(..., comment="操作：create/read/update/delete")
    description: Optional[str] = Field(default=None, comment="权限描述")


class PermissionCreateSchema(BaseModel):
    """Permission CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="权限名称")
    code: str = Field(..., comment="权限编码")
    resource: str = Field(..., comment="资源：patient/registration/treatment等")
    action: str = Field(..., comment="操作：create/read/update/delete")
    description: Optional[str] = Field(default=None, comment="权限描述")


class PermissionUpdateSchema(BaseModel):
    """Permission UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="权限名称")
    code: str = Field(..., comment="权限编码")
    resource: str = Field(..., comment="资源：patient/registration/treatment等")
    action: str = Field(..., comment="操作：create/read/update/delete")
    description: Optional[str] = Field(default=None, comment="权限描述")


class UserRoleSchema(BaseSchema):
    """UserRole Schema"""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID = Field(..., comment="用户ID")
    role_id: UUID = Field(..., comment="角色ID")


class UserRoleCreateSchema(BaseModel):
    """UserRole CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[UUID] = Field(default=None, comment="用户ID")
    role_id: Optional[UUID] = Field(default=None, comment="角色ID")


class UserRoleUpdateSchema(BaseModel):
    """UserRole UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[UUID] = Field(default=None, comment="用户ID")
    role_id: Optional[UUID] = Field(default=None, comment="角色ID")


class RolePermissionSchema(BaseSchema):
    """RolePermission Schema"""

    model_config = ConfigDict(from_attributes=True)

    role_id: UUID = Field(..., comment="角色ID")
    permission_id: UUID = Field(..., comment="权限ID")


class RolePermissionCreateSchema(BaseModel):
    """RolePermission CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    role_id: Optional[UUID] = Field(default=None, comment="角色ID")
    permission_id: Optional[UUID] = Field(default=None, comment="权限ID")


class RolePermissionUpdateSchema(BaseModel):
    """RolePermission UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    role_id: Optional[UUID] = Field(default=None, comment="角色ID")
    permission_id: Optional[UUID] = Field(default=None, comment="权限ID")
