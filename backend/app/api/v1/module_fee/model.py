"""
费用设置模块 ORM 模型（单一数据源）

费用类型通过 fee_type 区分：
- registration（挂号费）
- treatment（治疗费）
- extra（附加费）
- other（其它费用）
"""
from sqlalchemy import Column, String, Numeric, Boolean, Text, Integer

from app.core.database import BaseModel


class Fee(BaseModel):
    """
    费用设置模型

    统一管理诊所各类收费项目（挂号费、治疗费、附加费等），
    通过 fee_type 进行归类，前端各页面按 fee_type 过滤展示。
    """
    __tablename__ = "fees"

    # 费用类型：registration / treatment / extra / other
    fee_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="费用类型：registration/treatment/extra/other",
    )

    # 费用名称
    name = Column(
        String(100),
        nullable=False,
        comment="费用名称",
    )

    # 费用编码
    code = Column(
        String(50),
        nullable=True,
        index=True,
        comment="费用编码",
    )

    # 金额
    amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=0,
        comment="金额",
    )

    # 成本价（用于利润统计：利润 = 金额 - 成本价）
    cost_price = Column(
        Numeric(10, 2),
        nullable=True,
        default=0,
        comment="成本价",
    )

    # 计费单位（次/人/项等）
    unit = Column(
        String(20),
        nullable=True,
        comment="计费单位",
    )

    # 是否启用
    status = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="是否启用",
    )

    # 排序
    sort = Column(
        Integer,
        default=0,
        nullable=False,
        comment="排序",
    )

    # 备注
    remark = Column(
        Text,
        nullable=True,
        comment="备注",
    )

    __table_args__ = (
        {"comment": "费用设置表"},
    )

    def __repr__(self) -> str:
        return f"<Fee(id={self.id}, fee_type={self.fee_type}, name={self.name})>"
