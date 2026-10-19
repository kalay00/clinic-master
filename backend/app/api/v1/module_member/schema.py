"""
会员模块 Schema
"""
from typing import Optional
from pydantic import BaseModel, Field
from app.core.base_schema import BaseSchema


class MemberLevelSchema(BaseSchema):
    name: str = Field(..., description="等级名称")
    discount_rate: float = Field(1, description="会员折扣率(0.90=9折)")
    upgrade_threshold: float = Field(0, description="累计消费达到该值自动升级")
    sort: int = Field(0, description="排序")
    is_default: bool = Field(False, description="是否默认等级")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")
    member_count: int = Field(0, description="该等级会员数量")


class MemberLevelCreateSchema(BaseModel):
    name: str = Field(..., description="等级名称")
    discount_rate: float = Field(1, description="会员折扣率(0.90=9折)")
    upgrade_threshold: float = Field(0, description="累计消费达到该值自动升级")
    sort: int = Field(0, description="排序")
    is_default: bool = Field(False, description="是否默认等级")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class MemberLevelUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="等级名称")
    discount_rate: Optional[float] = Field(None, description="会员折扣率")
    upgrade_threshold: Optional[float] = Field(None, description="累计消费阈值")
    sort: Optional[int] = Field(None, description="排序")
    is_default: Optional[bool] = Field(None, description="是否默认等级")
    status: Optional[str] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")


class MemberSchema(BaseSchema):
    """会员（患者）列表项"""
    patient_no: Optional[str] = Field(None, description="会员卡号")
    name: str = Field(..., description="姓名")
    gender: Optional[str] = Field(None, description="性别")
    phone: Optional[str] = Field(None, description="手机号")
    member_level_id: Optional[str] = Field(None, description="会员等级ID")
    member_level_name: Optional[str] = Field(None, description="会员等级名称")
    balance: float = Field(0, description="账户余额")
    points: int = Field(0, description="积分")
    consumption_total: float = Field(0, description="累计消费")
    stored_total: float = Field(0, description="累计储值")
    gift_total: float = Field(0, description="累计赠送")
    member_status: str = Field("active", description="会员状态")
    expire_date: Optional[str] = Field(None, description="到期时间")
    created_at: Optional[str] = Field(None, description="开卡时间")


class MemberTransactionSchema(BaseSchema):
    """会员交易流水"""
    patient_id: str = Field(..., description="患者ID")
    type: str = Field(..., description="流水类型")
    amount: float = Field(0, description="金额变动")
    points: int = Field(0, description="积分变动")
    before_balance: float = Field(0, description="变动前余额")
    after_balance: float = Field(0, description="变动后余额")
    before_points: int = Field(0, description="变动前积分")
    after_points: int = Field(0, description="变动后积分")
    operator_id: Optional[str] = Field(None, description="操作人ID")
    remark: Optional[str] = Field(None, description="备注")
    created_at: Optional[str] = Field(None, description="时间")


class MemberRechargeSchema(BaseModel):
    amount: float = Field(..., gt=0, description="充值金额")
    method: Optional[str] = Field("cash", description="支付方式")
    remark: Optional[str] = Field(None, description="备注")


class MemberRefundSchema(BaseModel):
    amount: float = Field(..., gt=0, description="退款金额")
    method: Optional[str] = Field("cash", description="退款方式")
    remark: Optional[str] = Field(None, description="备注")


class MemberPointsSchema(BaseModel):
    points: int = Field(..., description="积分变动（正为增，负为减）")
    remark: Optional[str] = Field(None, description="备注")


class MemberLevelSetSchema(BaseModel):
    member_level_id: str = Field(..., description="目标会员等级ID")
    remark: Optional[str] = Field(None, description="备注")


class MemberUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="姓名")
    gender: Optional[str] = Field(None, description="性别")
    phone: Optional[str] = Field(None, description="手机号")
    member_level_id: Optional[str] = Field(None, description="会员等级ID（空字符串表示清除等级）")
    member_status: Optional[str] = Field(None, description="会员状态 active|inactive|expired")
    expire_date: Optional[str] = Field(None, description="到期时间(YYYY-MM-DD)，空字符串表示永久")
    remark: Optional[str] = Field(None, description="备注")
