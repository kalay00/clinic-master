"""
打印模板模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import BaseModel
from app.core.db_types import JSONBType


class PrintTemplate(BaseModel):
    """
    打印模板模型
    
    用于存储各种打印场景的模板配置，支持账单、处方、病历等打印模板。
    模板配置以JSON格式存储，包含字段定义、布局、样式等信息。
    """
    __tablename__ = "print_templates"
    
    # 模板名称
    name = Column(
        String(100),
        nullable=False,
        comment="模板名称"
    )
    
    # 模板类型：bill（账单）、prescription（处方）、medical_record（病历）
    type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="模板类型：bill/prescription/medical_record"
    )
    
    # 模板配置（JSON格式）
    # 包含页面设置、区域划分、字段定义等信息
    template_config = Column(
        JSONBType,
        nullable=False,
        comment="模板配置（JSON），包含页面设置、区域、字段等信息"
    )
    
    # 是否默认模板
    # 每个类型只能有一个默认模板
    is_default = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="是否默认模板"
    )
    
    __table_args__ = (
        {"comment": "打印模板表"},
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<PrintTemplate(id={self.id}, name={self.name}, type={self.type})>"
