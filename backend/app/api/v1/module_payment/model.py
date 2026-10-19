"""
收费模块 ORM 模型（单一数据源）
"""
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Text, ForeignKey, JSON, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class Bill(BaseModel):
    """账单模型"""
    __tablename__ = "bills"
    
    bill_no = Column(String(50), nullable=False, comment="账单号")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, comment="患者ID")
    registration_id = Column(UUID(as_uuid=True), ForeignKey("registrations.id"), comment="挂号ID")
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), comment="病历ID")
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), comment="处方ID")
    bill_type = Column(String(20), nullable=False, comment="账单类型：registration/treatment/pharmacy")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    paid_amount = Column(Numeric(10, 2), default=0, comment="已支付金额")
    discount_amount = Column(Numeric(10, 2), default=0, comment="优惠金额")
    insurance_amount = Column(Numeric(10, 2), default=0, comment="医保支付金额")
    status = Column(String(20), default="unpaid", comment="状态：unpaid/paid/refunded")
    payment_method = Column(String(20), comment="支付方式：cash/wechat/alipay/insurance")
    payment_time = Column(DateTime, comment="支付时间")
    items = Column(JSON, comment="账单项目（JSON）")
    remark = Column(Text, comment="备注")
    # 会员资产抵扣
    balance_deduction = Column(Numeric(12, 2), default=0, comment="本次支付使用余额抵扣金额")
    points_deduction = Column(Integer, default=0, comment="本次支付使用积分抵扣数")
    
    # 关系
    patient = relationship("Patient", backref="bills")
    registration = relationship("Registration", back_populates="bills")
    
    __table_args__ = (
        {"comment": "账单表"},
    )


class Payment(BaseModel):
    """支付记录模型"""
    __tablename__ = "payments"
    
    payment_no = Column(String(50), nullable=False, comment="支付单号")
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=False, comment="账单ID")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, comment="患者ID")
    payment_method = Column(String(20), nullable=False, comment="支付方式")
    amount = Column(Numeric(10, 2), nullable=False, comment="支付金额")
    status = Column(String(20), default="pending", comment="状态：pending/success/failed")
    transaction_id = Column(String(100), comment="第三方交易号")
    remark = Column(Text, comment="备注")
    
    __table_args__ = (
        {"comment": "支付记录表"},
    )


class BillItem(BaseModel):
    """账单明细表"""
    __tablename__ = "bill_items"
    
    bill_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="账单ID"
    )
    charge_item_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="收费项目ID"
    )
    item_name = Column(String(100), nullable=False, comment="项目名称")
    quantity = Column(Numeric(10, 2), nullable=False, comment="数量")
    unit_price = Column(Numeric(10, 2), nullable=False, comment="单价")
    total_price = Column(Numeric(10, 2), nullable=False, comment="总价")
    
    # 关系
    bill = relationship("Bill", backref="bill_items")
    
    __table_args__ = (
        {"comment": "账单明细表"},
    )
