"""
科室模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class Department(BaseModel):
    """科室模型"""
    __tablename__ = "departments"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, comment="租户ID")
    name = Column(String(50), nullable=False, comment="科室名称")
    code = Column(String(50), nullable=False, comment="科室编码")
    description = Column(Text, comment="科室描述")
    status = Column(String(20), default="active", comment="状态：active/inactive")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 关系
    tenant = relationship("Tenant", backref="departments")
    doctors = relationship("Doctor", back_populates="department")
    
    __table_args__ = (
        {"comment": "科室表"},
    )
