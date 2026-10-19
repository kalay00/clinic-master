"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr
from typing import Any


class BillSchema(BaseSchema):
    """Bill Schema"""

    model_config = ConfigDict(from_attributes=True)

    bill_no: str = Field(..., comment="账单号")
    patient_id: UUID = Field(..., comment="患者ID")
    registration_id: Optional[UUID] = Field(default=None, comment="挂号ID")
    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID")
    prescription_id: Optional[UUID] = Field(default=None, comment="处方ID")
    bill_type: str = Field(..., comment="账单类型：registration/treatment/pharmacy")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    paid_amount: Optional[float] = Field(default=None, comment="已支付金额")
    discount_amount: Optional[float] = Field(default=None, comment="优惠金额")
    insurance_amount: Optional[float] = Field(default=None, comment="医保支付金额")
    status: Optional[str] = Field(default=None, comment="状态：unpaid/paid/refunded")
    payment_method: Optional[str] = Field(default=None, comment="支付方式：cash/wechat/alipay/insurance")
    payment_time: Optional[DateTimeStr] = Field(default=None, comment="支付时间")
    items: Optional[Any] = Field(default=None, comment="账单项目（JSON）")
    remark: Optional[str] = Field(default=None, comment="备注")
    balance_deduction: Optional[float] = Field(default=0, comment="本次支付使用余额抵扣金额")
    points_deduction: Optional[int] = Field(default=0, comment="本次支付使用积分抵扣数")

    # 联表富化字段（患者姓名加密存储，需解密，列表/详情展示用）
    patient_name: Optional[str] = Field(default=None, comment="患者姓名（解密后）")


class BillCreateSchema(BaseModel):
    """Bill CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    bill_no: Optional[str] = Field(default=None, comment="账单号（不传则自动生成）")
    patient_id: UUID = Field(..., comment="患者ID")
    registration_id: Optional[UUID] = Field(default=None, comment="挂号ID")
    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID")
    prescription_id: Optional[UUID] = Field(default=None, comment="处方ID")
    bill_type: str = Field(..., comment="账单类型：registration/treatment/pharmacy")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    paid_amount: Optional[float] = Field(default=None, comment="已支付金额")
    discount_amount: Optional[float] = Field(default=None, comment="优惠金额")
    insurance_amount: Optional[float] = Field(default=None, comment="医保支付金额")
    status: Optional[str] = Field(default=None, comment="状态：unpaid/paid/refunded")
    payment_method: Optional[str] = Field(default=None, comment="支付方式：cash/wechat/alipay/insurance")
    payment_time: Optional[DateTimeStr] = Field(default=None, comment="支付时间")
    items: Optional[Any] = Field(default=None, comment="账单项目（JSON）")
    remark: Optional[str] = Field(default=None, comment="备注")


class BillUpdateSchema(BaseModel):
    """Bill UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    bill_no: Optional[str] = Field(default=None, comment="账单号")
    patient_id: UUID = Field(..., comment="患者ID")
    registration_id: Optional[UUID] = Field(default=None, comment="挂号ID")
    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID")
    prescription_id: Optional[UUID] = Field(default=None, comment="处方ID")
    bill_type: str = Field(..., comment="账单类型：registration/treatment/pharmacy")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    paid_amount: Optional[float] = Field(default=None, comment="已支付金额")
    discount_amount: Optional[float] = Field(default=None, comment="优惠金额")
    insurance_amount: Optional[float] = Field(default=None, comment="医保支付金额")
    status: Optional[str] = Field(default=None, comment="状态：unpaid/paid/refunded")
    payment_method: Optional[str] = Field(default=None, comment="支付方式：cash/wechat/alipay/insurance")
    payment_time: Optional[DateTimeStr] = Field(default=None, comment="支付时间")
    items: Optional[Any] = Field(default=None, comment="账单项目（JSON）")
    remark: Optional[str] = Field(default=None, comment="备注")


class PaymentSchema(BaseSchema):
    """Payment Schema"""

    model_config = ConfigDict(from_attributes=True)

    payment_no: str = Field(..., comment="支付单号")
    bill_id: UUID = Field(..., comment="账单ID")
    patient_id: UUID = Field(..., comment="患者ID")
    payment_method: str = Field(..., comment="支付方式")
    amount: float = Field(..., comment="支付金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/success/failed")
    transaction_id: Optional[UUID] = Field(default=None, comment="第三方交易号")
    remark: Optional[str] = Field(default=None, comment="备注")


class PaymentCreateSchema(BaseModel):
    """Payment CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    payment_no: str = Field(..., comment="支付单号")
    bill_id: UUID = Field(..., comment="账单ID")
    patient_id: UUID = Field(..., comment="患者ID")
    payment_method: str = Field(..., comment="支付方式")
    amount: float = Field(..., comment="支付金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/success/failed")
    transaction_id: Optional[UUID] = Field(default=None, comment="第三方交易号")
    remark: Optional[str] = Field(default=None, comment="备注")


class PaymentUpdateSchema(BaseModel):
    """Payment UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    payment_no: str = Field(..., comment="支付单号")
    bill_id: UUID = Field(..., comment="账单ID")
    patient_id: UUID = Field(..., comment="患者ID")
    payment_method: str = Field(..., comment="支付方式")
    amount: float = Field(..., comment="支付金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/success/failed")
    transaction_id: Optional[UUID] = Field(default=None, comment="第三方交易号")
    remark: Optional[str] = Field(default=None, comment="备注")


class BillPayRequest(BaseModel):
    """支付账单请求"""

    model_config = ConfigDict(from_attributes=True)

    payment_method: str = Field(..., comment="支付方式：cash/wechat/alipay/unionpay/medical_insurance")
    amount: float = Field(..., comment="支付金额（现金部分，余额/积分抵扣不计入）")
    transaction_id: Optional[str] = Field(default=None, comment="第三方交易流水号（银联等）")
    use_balance: bool = Field(False, comment="是否使用账户余额抵扣")
    use_points: int = Field(0, comment="使用的积分数量（按系统设置比例抵扣）")


class BillRefundRequest(BaseModel):
    """退费请求"""

    model_config = ConfigDict(from_attributes=True)

    refund_amount: float = Field(..., comment="退费金额")
    reason: Optional[str] = Field(default=None, comment="退费原因")
