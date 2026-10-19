"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from typing import Any


class PrintTemplateSchema(BaseSchema):
    """PrintTemplate Schema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="模板名称")
    type: str = Field(..., comment="模板类型：bill/prescription/medical_record")
    template_config: Any = Field(..., comment="模板配置（JSON），包含页面设置、区域、字段等信息")
    is_default: bool = Field(..., comment="是否默认模板")


class PrintTemplateCreateSchema(BaseModel):
    """PrintTemplate CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="模板名称")
    type: str = Field(..., comment="模板类型：bill/prescription/medical_record")
    template_config: Any = Field(..., comment="模板配置（JSON），包含页面设置、区域、字段等信息")
    is_default: Optional[bool] = Field(default=None, comment="是否默认模板")


class PrintTemplateUpdateSchema(BaseModel):
    """PrintTemplate UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="模板名称")
    type: str = Field(..., comment="模板类型：bill/prescription/medical_record")
    template_config: Any = Field(..., comment="模板配置（JSON），包含页面设置、区域、字段等信息")
    is_default: Optional[bool] = Field(default=None, comment="是否默认模板")
