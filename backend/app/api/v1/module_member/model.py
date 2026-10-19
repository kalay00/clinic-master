"""
会员模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Numeric, Integer, Boolean, Text
from app.core.database import BaseModel


class MemberLevel(BaseModel):
    """会员等级模型"""
    __tablename__ = "member_levels"

    name = Column(String(50), nullable=False, comment="等级名称（如 普通会员/银卡/金卡）")
    discount_rate = Column(Numeric(5, 2), default=1, nullable=False, comment="会员折扣率(0.90=9折)")
    upgrade_threshold = Column(Numeric(12, 2), default=0, nullable=False, comment="累计消费达到该值自动升级到本等级")
    sort = Column(Integer, default=0, comment="排序（升序）")
    is_default = Column(Boolean, default=False, comment="是否默认等级（新患者默认归属）")
    status = Column(String(20), default="active", comment="状态：active/inactive")
    remark = Column(Text, comment="备注")

    __table_args__ = (
        {"comment": "会员等级表"},
    )


class MemberTransaction(BaseModel):
    """会员交易流水（充值/退款/积分变动/等级变更等）"""
    __tablename__ = "member_transactions"

    patient_id = Column(String(36), nullable=False, index=True, comment="患者ID")
    member_level_id = Column(String(36), comment="关联会员等级ID（等级变更时记录）")
    # 流水类型：recharge 充值 / refund 退款 / points_add 积分增加 / points_deduct 积分扣除 / level_change 等级变更
    type = Column(String(20), nullable=False, index=True, comment="流水类型")
    amount = Column(Numeric(12, 2), default=0, comment="金额变动（充值为正，退款为负）")
    points = Column(Integer, default=0, comment="积分变动（增加为正，扣减为负）")
    before_balance = Column(Numeric(12, 2), default=0, comment="变动前余额")
    after_balance = Column(Numeric(12, 2), default=0, comment="变动后余额")
    before_points = Column(Integer, default=0, comment="变动前积分")
    after_points = Column(Integer, default=0, comment="变动后积分")
    operator_id = Column(String(36), comment="操作人ID")
    remark = Column(Text, comment="备注")

    __table_args__ = (
        {"comment": "会员交易流水表"},
    )
