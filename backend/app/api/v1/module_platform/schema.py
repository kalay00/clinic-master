"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr


class PlatformAdminSchema(BaseSchema):
    """PlatformAdmin Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, comment="主键ID")
    username: str = Field(..., comment="用户名")
    password_hash: str = Field(..., comment="密码哈希")
    real_name: Optional[str] = Field(default=None, comment="真实姓名")
    email: Optional[str] = Field(default=None, comment="邮箱")
    phone: Optional[str] = Field(default=None, comment="手机号（加密）")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive/locked")
    last_login_at: Optional[DateTimeStr] = Field(default=None, comment="最后登录时间")
    last_login_ip: Optional[str] = Field(default=None, comment="最后登录IP")
    created_at: DateTimeStr = Field(..., comment="创建时间")
    updated_at: DateTimeStr = Field(..., comment="更新时间")
    deleted_at: Optional[DateTimeStr] = Field(default=None, comment="删除时间")


class PlatformAdminCreateSchema(BaseModel):
    """PlatformAdmin CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., comment="用户名")
    password_hash: str = Field(..., comment="密码哈希")
    real_name: Optional[str] = Field(default=None, comment="真实姓名")
    email: Optional[str] = Field(default=None, comment="邮箱")
    phone: Optional[str] = Field(default=None, comment="手机号（加密）")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive/locked")
    last_login_at: Optional[DateTimeStr] = Field(default=None, comment="最后登录时间")
    last_login_ip: Optional[str] = Field(default=None, comment="最后登录IP")


class PlatformAdminUpdateSchema(BaseModel):
    """PlatformAdmin UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(..., comment="用户名")
    password_hash: str = Field(..., comment="密码哈希")
    real_name: Optional[str] = Field(default=None, comment="真实姓名")
    email: Optional[str] = Field(default=None, comment="邮箱")
    phone: Optional[str] = Field(default=None, comment="手机号（加密）")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive/locked")
    last_login_at: Optional[DateTimeStr] = Field(default=None, comment="最后登录时间")
    last_login_ip: Optional[str] = Field(default=None, comment="最后登录IP")
