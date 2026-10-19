"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr
from typing import Any


class ThirdPartyConfigSchema(BaseSchema):
    """ThirdPartyConfig Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, comment="主键ID")
    tenant_id: UUID = Field(..., comment="租户ID")
    service_type: str = Field(..., comment="服务类型")
    service_name: str = Field(..., comment="服务名称")
    is_enabled: bool = Field(..., comment="是否启用")
    config_data: Any = Field(..., comment="配置数据（JSON）")
    encrypted_fields: Optional[Any] = Field(default=None, comment="需要加密的字段名列表")
    created_at: DateTimeStr = Field(..., comment="创建时间")
    updated_at: DateTimeStr = Field(..., comment="更新时间")
    created_by: Optional[str] = Field(default=None, comment="创建人ID")
    updated_by: Optional[str] = Field(default=None, comment="更新人ID")


class ThirdPartyConfigCreateSchema(BaseModel):
    """ThirdPartyConfig CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    service_type: str = Field(..., comment="服务类型")
    service_name: str = Field(..., comment="服务名称")
    is_enabled: Optional[bool] = Field(default=None, comment="是否启用")
    config_data: Any = Field(..., comment="配置数据（JSON）")
    encrypted_fields: Optional[Any] = Field(default=None, comment="需要加密的字段名列表")


class ThirdPartyConfigUpdateSchema(BaseModel):
    """ThirdPartyConfig UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    service_type: str = Field(..., comment="服务类型")
    service_name: str = Field(..., comment="服务名称")
    is_enabled: Optional[bool] = Field(default=None, comment="是否启用")
    config_data: Any = Field(..., comment="配置数据（JSON）")
    encrypted_fields: Optional[Any] = Field(default=None, comment="需要加密的字段名列表")
