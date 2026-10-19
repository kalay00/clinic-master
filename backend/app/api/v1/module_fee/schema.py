"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema


class FeeSchema(BaseSchema):
    """Fee Schema"""

    model_config = ConfigDict(from_attributes=True)

    fee_type: str = Field(..., comment="费用类型：registration/treatment/extra/other")
    name: str = Field(..., comment="费用名称")
    code: Optional[str] = Field(default=None, comment="费用编码")
    amount: float = Field(..., comment="金额")
    cost_price: Optional[float] = Field(default=None, comment="成本价")
    unit: Optional[str] = Field(default=None, comment="计费单位")
    status: bool = Field(..., comment="是否启用")
    sort: int = Field(..., comment="排序")
    remark: Optional[str] = Field(default=None, comment="备注")


class FeeCreateSchema(BaseModel):
    """Fee CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    fee_type: str = Field(..., comment="费用类型：registration/treatment/extra/other")
    name: str = Field(..., comment="费用名称")
    code: Optional[str] = Field(default=None, comment="费用编码")
    amount: float = Field(..., comment="金额")
    cost_price: Optional[float] = Field(default=0, comment="成本价")
    unit: Optional[str] = Field(default=None, comment="计费单位")
    status: Optional[bool] = Field(default=True, comment="是否启用")
    sort: Optional[int] = Field(default=0, comment="排序")
    remark: Optional[str] = Field(default=None, comment="备注")


class FeeUpdateSchema(BaseModel):
    """Fee UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    fee_type: Optional[str] = Field(default=None, comment="费用类型")
    name: Optional[str] = Field(default=None, comment="费用名称")
    code: Optional[str] = Field(default=None, comment="费用编码")
    amount: Optional[float] = Field(default=None, comment="金额")
    cost_price: Optional[float] = Field(default=None, comment="成本价")
    unit: Optional[str] = Field(default=None, comment="计费单位")
    status: Optional[bool] = Field(default=None, comment="是否启用")
    sort: Optional[int] = Field(default=None, comment="排序")
    remark: Optional[str] = Field(default=None, comment="备注")
