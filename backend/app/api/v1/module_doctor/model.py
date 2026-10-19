"""
医生模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class Doctor(BaseModel):
    """医生模型"""
    __tablename__ = "doctors"
    
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, comment="租户ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), comment="关联用户ID")
    name = Column(String(50), nullable=False, comment="医生姓名")
    employee_no = Column(String(50), nullable=False, comment="工号")
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), comment="科室ID")
    title = Column(String(50), comment="职称：主任医师/副主任医师/主治医师/住院医师")
    specialty = Column(String(100), comment="专业特长")
    phone = Column(String(20), comment="联系电话")
    email = Column(String(100), comment="邮箱")
    registration_fee = Column(Numeric(10, 2), default=0, comment="默认挂号费")
    bio = Column(Text, comment="医生简介")
    photo_url = Column(String(500), comment="医生照片URL")
    # 提成方案：医生可设置提成方式
    commission_plan_id = Column(String(36), comment="提成方案ID")
    status = Column(String(20), default="active", comment="状态：active/inactive")
    
    # 关系
    tenant = relationship("Tenant", backref="doctors")
    department = relationship("Department", back_populates="doctors")
    user = relationship("User", backref="doctor_profile")
    
    __table_args__ = (
        {"comment": "医生表"},
    )
