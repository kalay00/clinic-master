"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr
from typing import Any


class TenantSchema(BaseSchema):
    """Tenant Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, comment="主键ID")
    name: str = Field(..., comment="机构名称")
    code: str = Field(..., comment="机构编码")
    type: str = Field(..., comment="机构类型：clinic/hospital")
    contact_name: Optional[str] = Field(default=None, comment="联系人")
    contact_phone: Optional[str] = Field(default=None, comment="联系电话")
    contact_email: Optional[str] = Field(default=None, comment="联系邮箱")
    address: Optional[str] = Field(default=None, comment="地址")
    status: str = Field(..., comment="状态：active/inactive")
    subscription_plan: Optional[str] = Field(default=None, comment="订阅计划")
    expires_at: Optional[DateTimeStr] = Field(default=None, comment="到期时间")
    config: Optional[Any] = Field(default=None, comment="配置信息（JSON）")
    domain: Optional[str] = Field(default=None, comment="租户域名（如：test001.his.example.com）")
    created_at: DateTimeStr = Field(..., comment="创建时间")
    updated_at: DateTimeStr = Field(..., comment="更新时间")
    deleted_at: Optional[DateTimeStr] = Field(default=None, comment="删除时间")


class TenantCreateSchema(BaseModel):
    """Tenant CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="机构名称")
    code: str = Field(..., comment="机构编码")
    type: str = Field(..., comment="机构类型：clinic/hospital")
    contact_name: Optional[str] = Field(default=None, comment="联系人")
    contact_phone: Optional[str] = Field(default=None, comment="联系电话")
    contact_email: Optional[str] = Field(default=None, comment="联系邮箱")
    address: Optional[str] = Field(default=None, comment="地址")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    subscription_plan: Optional[str] = Field(default=None, comment="订阅计划")
    expires_at: Optional[DateTimeStr] = Field(default=None, comment="到期时间")
    config: Optional[Any] = Field(default=None, comment="配置信息（JSON）")
    domain: Optional[str] = Field(default=None, comment="租户域名（如：test001.his.example.com）")


class TenantUpdateSchema(BaseModel):
    """Tenant UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="机构名称")
    code: str = Field(..., comment="机构编码")
    type: str = Field(..., comment="机构类型：clinic/hospital")
    contact_name: Optional[str] = Field(default=None, comment="联系人")
    contact_phone: Optional[str] = Field(default=None, comment="联系电话")
    contact_email: Optional[str] = Field(default=None, comment="联系邮箱")
    address: Optional[str] = Field(default=None, comment="地址")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    subscription_plan: Optional[str] = Field(default=None, comment="订阅计划")
    expires_at: Optional[DateTimeStr] = Field(default=None, comment="到期时间")
    config: Optional[Any] = Field(default=None, comment="配置信息（JSON）")
    domain: Optional[str] = Field(default=None, comment="租户域名（如：test001.his.example.com）")


class TenantCurrentSchema(BaseModel):
    """当前诊所信息（用于诊所信息维护页面）"""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, comment="主键ID")
    code: str = Field(..., comment="机构编码")
    name: str = Field(..., comment="机构名称")
    contact_name: Optional[str] = Field(default=None, comment="诊所所有人")
    contact_phone: Optional[str] = Field(default=None, comment="诊所所有人电话")
    contact_email: Optional[str] = Field(default=None, comment="诊所所有人邮箱")
    address: Optional[str] = Field(default=None, comment="地址")
    status: str = Field(..., comment="状态：active/inactive")
    expires_at: Optional[DateTimeStr] = Field(default=None, comment="到期时间")
    logo: Optional[str] = Field(default=None, comment="诊所Logo（来自 config.logo）")
    introduction: Optional[str] = Field(default=None, comment="诊所介绍（来自 config.introduction）")
    user_count: int = Field(default=0, comment="总用户数")


class TenantCurrentUpdateSchema(BaseModel):
    """更新当前诊所信息"""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None, comment="机构名称")
    contact_name: Optional[str] = Field(default=None, comment="诊所所有人")
    contact_phone: Optional[str] = Field(default=None, comment="诊所所有人电话")
    contact_email: Optional[str] = Field(default=None, comment="诊所所有人邮箱")
    address: Optional[str] = Field(default=None, comment="地址")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    logo: Optional[str] = Field(default=None, comment="诊所Logo")
    introduction: Optional[str] = Field(default=None, comment="诊所介绍")
