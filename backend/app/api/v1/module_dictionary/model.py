"""
通用字典模块 ORM 模型（单一数据源）

一张 dictionaries 表覆盖系统设置中大量“选项类”数据：
- 病历信息：诊断/医嘱/主诉/现病史/既往史/过敏史/个人史/辅助检查/治疗意见
- 药品信息：药品用法/用药频次/药品单位
- 检查项目：检查项目/检查部位
- 患者信息：患者来源/患者类型
以及其它业务页面下拉选项来源。
"""
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class Dictionary(BaseModel):
    """通用字典模型"""
    __tablename__ = "dictionaries"

    # 一级分类（如 medical_record / drug / inspection / patient）
    category = Column(String(50), nullable=False, index=True, comment="一级分类 key")
    # 二级子类型（如 diagnosis / drug_usage / patient_source）
    sub_type = Column(String(50), nullable=False, index=True, comment="二级子类型 key")
    # 主文本内容（字典项展示值）
    content = Column(String(200), nullable=False, comment="字典内容")
    # 可选编码（如 ICD 编码等）
    code = Column(String(50), comment="编码")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(String(20), default="active", comment="状态 active/inactive")
    remark = Column(Text, comment="备注")

    created_by_user = relationship(
        "User",
        primaryjoin="Dictionary.created_by == User.id",
        foreign_keys="[Dictionary.created_by]",
        uselist=False,
        lazy="joined",
    )

    __table_args__ = ({"comment": "通用字典表"},)
