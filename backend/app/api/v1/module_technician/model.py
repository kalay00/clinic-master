"""
技师模块 ORM 模型
"""
from sqlalchemy import Column, String, Text
from app.core.database import BaseModel


class Technician(BaseModel):
    """技师模型（用于项目服务核销）"""
    __tablename__ = "technicians"

    name = Column(String(50), nullable=False, comment="技师姓名")
    phone = Column(String(20), comment="联系电话")
    gender = Column(String(10), comment="性别")
    skills = Column(Text, comment="擅长项目/技能（逗号分隔或JSON）")
    status = Column(String(20), default="active", comment="状态 active/inactive")
    remark = Column(Text, comment="备注")

    __table_args__ = (
        {"comment": "技师表"},
    )
