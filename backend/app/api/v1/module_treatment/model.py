"""
诊疗模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Text, JSON, Numeric, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class MedicalRecord(BaseModel):
    """病历模型"""
    __tablename__ = "medical_records"
    
    registration_id = Column(UUID(as_uuid=True), ForeignKey("registrations.id"), nullable=False, comment="挂号ID")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, comment="患者ID")
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False, comment="医生ID")
    chief_complaint = Column(Text, comment="主诉")
    present_illness = Column(Text, comment="现病史")
    past_history = Column(Text, comment="既往史")
    physical_examination = Column(Text, comment="体格检查")
    diagnosis = Column(Text, comment="诊断")
    treatment_plan = Column(Text, comment="治疗方案")
    remark = Column(Text, comment="备注")
    
    # 关系
    patient = relationship("Patient", backref="medical_records")
    doctor = relationship("Doctor", backref="medical_records")
    registration = relationship("Registration", backref="medical_records")
    
    __table_args__ = (
        {"comment": "病历表"},
    )


class Prescription(BaseModel):
    """处方模型"""
    __tablename__ = "prescriptions"
    
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=True, comment="病历ID（可不关联病历独立开方）")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, comment="患者ID")
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False, comment="医生ID")
    prescription_no = Column(String(50), nullable=False, comment="处方单号")
    prescription_type = Column(String(20), default="western", comment="处方类型：western/traditional/chinese_medicine")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    status = Column(String(20), default="pending", comment="状态：pending/paid/dispensed/cancelled")
    # 关联收费账单：处方创建后自动生成账单，收费完成(status=paid)后方可发药
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), comment="关联收费账单ID")
    items = Column(JSON, comment="处方项目（JSON）")
    remark = Column(Text, comment="备注")
    
    # 关系
    patient = relationship("Patient", backref="prescriptions")
    doctor = relationship("Doctor", backref="prescriptions")
    medical_record = relationship("MedicalRecord", backref="prescriptions")
    
    __table_args__ = (
        {"comment": "处方表"},
    )


class PrescriptionServiceItem(BaseModel):
    """处方服务项目（诊疗结束后开具处方时选择的项目）"""
    __tablename__ = "prescription_service_items"

    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False, comment="处方ID")
    project_id = Column(String(36), comment="项目ID")
    project_name = Column(String(100), comment="项目名称快照")
    quantity = Column(Integer, default=1, comment="数量")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价（折后）")
    total_amount = Column(Numeric(10, 2), default=0, comment="小计")
    technician_id = Column(String(36), comment="服务技师ID")
    participate_member_discount = Column(Boolean, default=True, comment="参与会员折扣")
    participate_commission = Column(Boolean, default=False, comment="参与提成")
    commission_amount = Column(Numeric(10, 2), default=0, comment="提成金额")
    status = Column(String(20), default="pending", comment="状态")

    __table_args__ = (
        {"comment": "处方服务项目表"},
    )
