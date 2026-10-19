"""
项目模块 Schema
"""
from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator
from app.core.base_schema import BaseSchema
from datetime import date

# 前端可能传空字符串 "" 而非 null，Pydantic v2 会尝试解析日期而失败；
# 这里在解析前把空串/None 统一转成 None。
def _empty_str_to_none(v):
    return None if v in ("", None) else v


OptionalDate = Annotated[Optional[date], BeforeValidator(_empty_str_to_none)]


# ---------- 项目分类 ----------
class ProjectCategorySchema(BaseSchema):
    name: str = Field(..., description="分类名称")
    sort: int = Field(0, description="排序")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class ProjectCategoryCreateSchema(BaseModel):
    name: str = Field(..., description="分类名称")
    sort: int = Field(0, description="排序")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class ProjectCategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="分类名称")
    sort: Optional[int] = Field(None, description="排序")
    status: Optional[str] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


# ---------- 项目 ----------
class ProjectSchema(BaseSchema):
    name: str = Field(..., description="项目名称")
    category_id: Optional[str] = Field(None, description="项目分类ID")
    category_name: Optional[str] = Field(None, description="分类名称")
    main_image: Optional[str] = Field(None, description="主图URL")
    price: float = Field(0, description="项目价")
    cost: float = Field(0, description="成本")
    service_fee: float = Field(0, description="服务费用")
    service_count: int = Field(1, description="服务次数")
    participate_member_discount: bool = Field(True, description="是否参与会员折扣")
    participate_commission: bool = Field(False, description="是否参与提成")
    service_type: str = Field("count", description="服务方式 count/period")
    period_type: Optional[str] = Field(None, description="周期类型 year/month/custom")
    period_start: OptionalDate = Field(None, description="周期开始")
    period_end: OptionalDate = Field(None, description="周期结束")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")
    deductible_points: int = Field(0, description="每次服务可抵扣积分（0 表示不可抵扣）")


class ProjectCreateSchema(BaseModel):
    name: str = Field(..., description="项目名称")
    category_id: Optional[str] = Field(None, description="项目分类ID")
    main_image: Optional[str] = Field(None, description="主图URL")
    price: float = Field(0, description="项目价")
    cost: float = Field(0, description="成本")
    service_fee: float = Field(0, description="服务费用")
    service_count: int = Field(1, description="服务次数")
    participate_member_discount: bool = Field(True, description="是否参与会员折扣")
    participate_commission: bool = Field(False, description="是否参与提成")
    service_type: str = Field("count", description="服务方式 count/period")
    period_type: Optional[str] = Field(None, description="周期类型")
    period_start: OptionalDate = Field(None, description="周期开始")
    period_end: OptionalDate = Field(None, description="周期结束")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")
    deductible_points: int = Field(0, description="每次服务可抵扣积分（0 表示不可抵扣）")


class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="项目名称")
    category_id: Optional[str] = Field(None, description="项目分类ID")
    main_image: Optional[str] = Field(None, description="主图URL")
    price: Optional[float] = Field(None, description="项目价")
    cost: Optional[float] = Field(None, description="成本")
    service_fee: Optional[float] = Field(None, description="服务费用")
    service_count: Optional[int] = Field(None, description="服务次数")
    participate_member_discount: Optional[bool] = Field(None, description="是否参与会员折扣")
    participate_commission: Optional[bool] = Field(None, description="是否参与提成")
    service_type: Optional[str] = Field(None, description="服务方式")
    period_type: Optional[str] = Field(None, description="周期类型")
    period_start: OptionalDate = Field(None, description="周期开始")
    period_end: OptionalDate = Field(None, description="周期结束")
    status: Optional[str] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")
    deductible_points: int = Field(0, description="每次服务可抵扣积分（0 表示不可抵扣）")


# ---------- 购买 / 核销 ----------
class PurchaseCreateSchema(BaseModel):
    patient_id: str = Field(..., description="患者ID")
    project_id: str = Field(..., description="项目ID")
    quantity: int = Field(1, description="购买数量")


class VerificationCreateSchema(BaseModel):
    patient_project_id: str = Field(..., description="患者项目ID")
    technician_id: Optional[str] = Field(None, description="服务技师ID")
