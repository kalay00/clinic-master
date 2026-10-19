"""
医保局监管模块 ORM 模型（单一数据源）
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Numeric, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class MedicalInsuranceSettlement(BaseModel):
    """医保结算数据模型"""
    __tablename__ = "medical_insurance_settlements"
    
    # 关联业务数据
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=False, index=True, comment="账单ID")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True, comment="患者ID")
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=True, index=True, comment="病历ID")
    
    # 医保结算信息
    settlement_no = Column(String(100), nullable=False, unique=True, index=True, comment="医保结算单号")
    insurance_card_no = Column(String(50), index=True, comment="医保卡号")
    insurance_type = Column(String(50), comment="医保类型：职工医保/居民医保/新农合")
    total_amount = Column(Numeric(10, 2), nullable=False, comment="总金额")
    insurance_amount = Column(Numeric(10, 2), default=0, comment="医保支付金额")
    personal_amount = Column(Numeric(10, 2), default=0, comment="个人支付金额")
    reimbursement_ratio = Column(Numeric(5, 2), comment="报销比例")
    
    # 结算状态
    status = Column(String(20), default="pending", nullable=False, index=True, comment="结算状态：pending/success/failed")
    settlement_time = Column(DateTime(timezone=True), comment="结算时间")
    settlement_result = Column(Text, comment="结算结果")
    error_message = Column(Text, comment="错误信息")
    
    # 上报信息
    reported_at = Column(DateTime(timezone=True), comment="上报时间")
    report_status = Column(String(20), default="pending", index=True, comment="上报状态：pending/success/failed")
    report_error = Column(Text, comment="上报错误信息")
    
    # 结算明细（JSON格式）
    settlement_details = Column(JSON, comment="结算明细")
    
    # 关系
    bill = relationship("Bill", backref="medical_insurance_settlements")
    patient = relationship("Patient", backref="medical_insurance_settlements")
    medical_record = relationship("MedicalRecord", backref="medical_insurance_settlements")
    
    __table_args__ = (
        {"comment": "医保结算数据表（v2.0新增）"},
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<MedicalInsuranceSettlement(id={self.id}, settlement_no={self.settlement_no}, status={self.status})>"


class MedicalInsuranceViolation(BaseModel):
    """医保违规记录模型"""
    __tablename__ = "medical_insurance_violations"
    
    # 关联业务数据
    bill_id = Column(UUID(as_uuid=True), ForeignKey("bills.id"), nullable=True, index=True, comment="账单ID")
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True, index=True, comment="患者ID")
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=True, index=True, comment="病历ID")
    
    # 违规信息
    violation_no = Column(String(100), nullable=False, unique=True, index=True, comment="违规记录编号")
    violation_type = Column(String(50), nullable=False, index=True, comment="违规类型：over_limit/duplicate/unauthorized等")
    violation_level = Column(String(20), default="medium", nullable=False, index=True, comment="违规级别：low/medium/high")
    violation_desc = Column(Text, nullable=False, comment="违规描述")
    violation_amount = Column(Numeric(10, 2), comment="违规金额")
    
    # 违规规则
    policy_id = Column(UUID(as_uuid=True), ForeignKey("medical_insurance_policies.id"), nullable=True, index=True, comment="关联政策ID")
    rule_name = Column(String(100), comment="违规规则名称")
    rule_description = Column(Text, comment="违规规则描述")
    
    # 违规数据
    violation_data = Column(JSON, comment="违规数据详情")
    
    # 处理状态
    status = Column(String(20), default="detected", nullable=False, index=True, comment="处理状态：detected/confirmed/handled/closed")
    detected_at = Column(DateTime(timezone=True), nullable=False, comment="检测时间")
    confirmed_at = Column(DateTime(timezone=True), comment="确认时间")
    handled_at = Column(DateTime(timezone=True), comment="处理时间")
    handled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), comment="处理人ID")
    handling_result = Column(Text, comment="处理结果")
    
    # 关系
    bill = relationship("Bill", backref="medical_insurance_violations")
    patient = relationship("Patient", backref="medical_insurance_violations")
    medical_record = relationship("MedicalRecord", backref="medical_insurance_violations")
    policy = relationship("MedicalInsurancePolicy", backref="violations")
    handler = relationship("User", foreign_keys=[handled_by], backref="handled_violations")
    
    __table_args__ = (
        {"comment": "医保违规记录表（v2.0新增）"},
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<MedicalInsuranceViolation(id={self.id}, violation_no={self.violation_no}, violation_type={self.violation_type})>"


class MedicalInsurancePolicy(BaseModel):
    """医保政策配置模型"""
    __tablename__ = "medical_insurance_policies"
    
    # 政策基本信息
    policy_name = Column(String(200), nullable=False, comment="政策名称")
    policy_code = Column(String(50), nullable=False, unique=True, index=True, comment="政策代码")
    policy_type = Column(String(50), nullable=False, index=True, comment="政策类型：reimbursement/limit/restriction等")
    
    # 政策内容
    policy_content = Column(Text, nullable=False, comment="政策内容")
    policy_rules = Column(JSON, nullable=False, comment="政策规则（JSON格式）")
    
    # 政策生效信息
    effective_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="生效日期")
    expiry_date = Column(DateTime(timezone=True), index=True, comment="失效日期")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="是否生效")
    
    # 政策版本
    version = Column(String(20), default="1.0", nullable=False, comment="政策版本")
    previous_version_id = Column(UUID(as_uuid=True), ForeignKey("medical_insurance_policies.id"), comment="上一版本ID")
    
    # 政策适用范围
    applicable_regions = Column(JSON, comment="适用地区（JSON数组）")
    applicable_insurance_types = Column(JSON, comment="适用医保类型（JSON数组）")
    
    # 备注
    remark = Column(Text, comment="备注")
    
    # 关系
    previous_version = relationship("MedicalInsurancePolicy", remote_side="MedicalInsurancePolicy.id", backref="next_versions")
    
    __table_args__ = (
        {"comment": "医保政策配置表（v2.0新增）"},
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<MedicalInsurancePolicy(id={self.id}, policy_name={self.policy_name}, version={self.version})>"
