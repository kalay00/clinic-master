"""
提成方案模块 Schema
"""
from typing import Optional
from pydantic import BaseModel, Field
from app.core.base_schema import BaseSchema


class CommissionPlanSchema(BaseSchema):
    name: str = Field(..., description="方案名称")
    type: str = Field("percentage", description="提成方式 fixed/percentage")
    fixed_amount: float = Field(0, description="固定金额提成")
    percentage_rate: float = Field(0, description="比例提成(0.10=10%)")
    min_amount: float = Field(0, description="起提金额")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class CommissionPlanCreateSchema(BaseModel):
    name: str = Field(..., description="方案名称")
    type: str = Field("percentage", description="提成方式 fixed/percentage")
    fixed_amount: float = Field(0, description="固定金额提成")
    percentage_rate: float = Field(0, description="比例提成")
    min_amount: float = Field(0, description="起提金额")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class CommissionPlanUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="方案名称")
    type: Optional[str] = Field(None, description="提成方式")
    fixed_amount: Optional[float] = Field(None, description="固定金额提成")
    percentage_rate: Optional[float] = Field(None, description="比例提成")
    min_amount: Optional[float] = Field(None, description="起提金额")
    status: Optional[str] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")
