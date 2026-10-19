"""
提成方案模块 ORM 模型
"""
from sqlalchemy import Column, String, Numeric, Text
from app.core.database import BaseModel


class CommissionPlan(BaseModel):
    """提成方案模型"""
    __tablename__ = "commission_plans"

    name = Column(String(50), nullable=False, comment="方案名称")
    # 提成方式：fixed=固定金额, percentage=按比例
    type = Column(String(20), default="percentage", nullable=False, comment="提成方式 fixed/percentage")
    fixed_amount = Column(Numeric(10, 2), default=0, comment="固定金额提成（元）")
    percentage_rate = Column(Numeric(5, 2), default=0, comment="比例提成（0.10=10%）")
    min_amount = Column(Numeric(10, 2), default=0, comment="起提金额（订单金额低于此值不提成）")
    status = Column(String(20), default="active", comment="状态 active/inactive")
    remark = Column(Text, comment="备注")

    __table_args__ = (
        {"comment": "提成方案表"},
    )
