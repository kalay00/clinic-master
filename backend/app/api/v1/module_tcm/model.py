"""
中医模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Text, Integer, Numeric, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import BaseModel


class Diagnosis(BaseModel):
    """诊断表"""
    __tablename__ = "diagnoses"
    
    medical_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medical_records.id"),
        nullable=False,
        index=True,
        comment="病历ID"
    )
    icd_code = Column(String(20), comment="ICD编码")
    diagnosis_name = Column(String(200), nullable=False, comment="诊断名称")
    diagnosis_type = Column(String(20), comment="类型：primary/secondary")
    description = Column(Text, comment="描述")
    
    # 关系
    medical_record = relationship("MedicalRecord", backref="diagnoses")
    
    __table_args__ = (
        {"comment": "诊断表"},
    )


class TCMDiagnosis(BaseModel):
    """中医诊断表"""
    __tablename__ = "tcm_diagnosis"
    
    medical_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medical_records.id"),
        nullable=False,
        index=True,
        comment="病历ID"
    )
    syndrome_type = Column(String(100), comment="证型")
    pathogenesis = Column(Text, comment="病机")
    disease_name = Column(String(100), comment="病名")
    constitution_type = Column(String(50), comment="体质类型（九种体质）")
    constitution_desc = Column(Text, comment="体质描述")
    tongue_state = Column(Text, comment="舌象")
    pulse_state = Column(Text, comment="脉象")
    tcm_diagnosis = Column(Text, comment="中医诊断")
    treatment_principle = Column(Text, comment="治则")
    treatment_method = Column(Text, comment="治法")
    
    # 关系
    medical_record = relationship("MedicalRecord", backref="tcm_diagnosis")
    
    __table_args__ = (
        {"comment": "中医诊断表"},
    )


class TCMFourExaminations(BaseModel):
    """中医四诊表"""
    __tablename__ = "tcm_four_examinations"
    
    medical_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medical_records.id"),
        nullable=False,
        index=True,
        comment="病历ID"
    )
    inspection = Column(Text, comment="望诊")
    listening_smelling = Column(Text, comment="闻诊")
    inquiry = Column(Text, comment="问诊")
    pulse_feeling = Column(Text, comment="切诊（脉诊）")
    
    # 关系
    medical_record = relationship("MedicalRecord", backref="tcm_four_examinations")
    
    __table_args__ = (
        {"comment": "中医四诊表"},
    )


class TCMTreatment(BaseModel):
    """中医治疗方法表"""
    __tablename__ = "tcm_treatments"
    
    medical_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medical_records.id"),
        nullable=False,
        index=True,
        comment="病历ID"
    )
    treatment_type = Column(String(50), nullable=False, comment="治疗类型：acupuncture/massage/cupping/moxibustion")
    treatment_name = Column(String(100), nullable=False, comment="治疗方法名称")
    treatment_points = Column(Text, comment="治疗穴位/部位")
    treatment_duration = Column(Integer, comment="治疗时长（分钟）")
    treatment_frequency = Column(String(50), comment="治疗频次")
    treatment_course = Column(Integer, comment="疗程（次数）")
    remark = Column(Text, comment="备注")
    
    # 关系
    medical_record = relationship("MedicalRecord", backref="tcm_treatments")
    
    __table_args__ = (
        {"comment": "中医治疗方法表"},
    )


class TCMPrescription(BaseModel):
    """中药处方表"""
    __tablename__ = "tcm_prescriptions"
    
    prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prescriptions.id"),
        nullable=True,
        index=True,
        comment="关联通用处方"
    )
    medical_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("medical_records.id"),
        nullable=True,
        index=True,
        comment="病历ID"
    )
    prescription_no = Column(String(50), nullable=False, comment="处方号")
    prescription_type = Column(String(50), comment="处方类型：classical/empirical/agreed")
    prescription_name = Column(String(100), comment="方剂名称")
    decoction_method = Column(Text, comment="煎服法")
    dosage_days = Column(Integer, comment="服药天数")
    total_dose = Column(Numeric(10, 2), comment="总剂量")
    decoction_service = Column(Boolean, default=False, comment="是否代煎")
    
    # 关系
    prescription = relationship("Prescription", backref="tcm_prescription")
    medical_record = relationship("MedicalRecord", backref="tcm_prescriptions")
    items = relationship("TCMPrescriptionItem", back_populates="tcm_prescription", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"comment": "中药处方表"},
    )


class TCMPrescriptionItem(BaseModel):
    """中药处方明细表"""
    __tablename__ = "tcm_prescription_items"
    
    tcm_prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tcm_prescriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="中药处方ID"
    )
    drug_id = Column(
        UUID(as_uuid=True),
        ForeignKey("drugs.id"),
        nullable=False,
        index=True,
        comment="药品ID"
    )
    drug_name = Column(String(100), nullable=False, comment="药品名称")
    specification = Column(String(50), comment="规格")
    unit = Column(String(20), comment="单位（克、两、钱等）")
    quantity = Column(Numeric(10, 2), nullable=False, comment="数量")
    dosage_unit = Column(String(20), comment="剂量单位")
    processing_method = Column(String(50), comment="炮制方法")
    role_in_prescription = Column(String(50), comment="方中作用（君、臣、佐、使）")
    remark = Column(Text, comment="备注")
    
    # 关系
    tcm_prescription = relationship("TCMPrescription", back_populates="items")
    drug = relationship("Drug", backref="tcm_prescription_items")
    
    __table_args__ = (
        {"comment": "中药处方明细表"},
    )


class TCMFormula(BaseModel):
    """中医方剂表"""
    __tablename__ = "tcm_formulas"
    
    # tenant_id可为NULL，表示系统方剂
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=True,
        index=True,
        comment="租户ID（NULL表示系统方剂）"
    )
    formula_name = Column(String(100), nullable=False, comment="方剂名称")
    formula_type = Column(String(50), comment="方剂类型：classical/empirical/agreed")
    source = Column(String(200), comment="来源")
    composition = Column(Text, comment="组成")
    functions = Column(Text, comment="功效")
    indications = Column(Text, comment="主治")
    contraindications = Column(Text, comment="禁忌")
    usage_method = Column(Text, comment="用法")
    
    __table_args__ = (
        {"comment": "中医方剂表"},
    )


class TCMDecoctionService(BaseModel):
    """中药煎药服务表"""
    __tablename__ = "tcm_decoction_service"
    
    tcm_prescription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tcm_prescriptions.id"),
        nullable=False,
        index=True,
        comment="中药处方ID"
    )
    service_type = Column(String(20), default="decoction", comment="服务类型：decoction/grinding")
    status = Column(String(20), default="pending", comment="状态：pending/processing/completed")
    decoction_method = Column(String(50), comment="煎药方法")
    decoction_start_time = Column(DateTime(timezone=True), comment="开始煎药时间")
    decoction_complete_time = Column(DateTime(timezone=True), comment="完成煎药时间")
    operator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        comment="操作人ID"
    )
    remark = Column(Text, comment="备注")
    
    # 关系
    tcm_prescription = relationship("TCMPrescription", backref="decoction_services")
    operator = relationship("User", backref="decoction_services")
    
    __table_args__ = (
        {"comment": "中药煎药服务表"},
    )
