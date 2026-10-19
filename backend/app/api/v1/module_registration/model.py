"""
挂号模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Date, Time, DateTime, Integer, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class Schedule(BaseModel):
    """排班模型"""
    __tablename__ = "schedules"
    
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False, comment="医生ID")
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), comment="科室ID")
    schedule_date = Column(Date, nullable=False, comment="排班日期")
    time_slot = Column(String(20), nullable=False, comment="时段：morning/afternoon/evening")
    start_time = Column(Time, nullable=False, comment="开始时间")
    end_time = Column(Time, nullable=False, comment="结束时间")
    total_quota = Column(Integer, default=0, comment="总号源")
    used_quota = Column(Integer, default=0, comment="已用号源")
    price = Column(Numeric(10, 2), default=0, comment="挂号费")
    status = Column(String(20), default="active", comment="状态：active正常、paused暂停、cancelled取消")
    
    # 关系
    doctor = relationship("Doctor", backref="schedules")
    department = relationship("Department", backref="schedules")
    
    __table_args__ = (
        {"comment": "排班表"},
    )


class Registration(BaseModel):
    """挂号模型"""
    __tablename__ = "registrations"
    
    registration_no = Column(String(50), nullable=False, comment="挂号单号")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, comment="患者ID")
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), comment="医生ID")
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), comment="科室ID")
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("schedules.id"), comment="排班ID")
    registration_date = Column(Date, nullable=False, comment="挂号日期")
    registration_time = Column(Time, comment="挂号时间")
    visit_time = Column(DateTime, comment="就诊时间")
    registration_type = Column(String(20), nullable=False, comment="类型：onsite/appointment/wechat")
    status = Column(String(20), default="pending", comment="状态：pending/completed/cancelled")
    price = Column(Numeric(10, 2), default=0, comment="挂号费")
    paid_amount = Column(Numeric(10, 2), default=0, comment="已支付金额")
    payment_status = Column(String(20), default="unpaid", comment="支付状态")
    remark = Column(Text, comment="备注")
    
    # 关系
    patient = relationship("Patient", backref="registrations")
    doctor = relationship("Doctor", backref="registrations")
    department = relationship("Department", backref="registrations")
    schedule = relationship("Schedule", backref="registrations")
    bills = relationship("Bill", back_populates="registration")
    
    __table_args__ = (
        {"comment": "挂号表"},
    )
