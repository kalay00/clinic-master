"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from typing import Any


class MedicalRecordSchema(BaseSchema):
    """MedicalRecord Schema"""

    model_config = ConfigDict(from_attributes=True)

    registration_id: UUID = Field(..., comment="挂号ID")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: UUID = Field(..., comment="医生ID")
    chief_complaint: Optional[str] = Field(default=None, comment="主诉")
    present_illness: Optional[str] = Field(default=None, comment="现病史")
    past_history: Optional[str] = Field(default=None, comment="既往史")
    physical_examination: Optional[str] = Field(default=None, comment="体格检查")
    diagnosis: Optional[str] = Field(default=None, comment="诊断")
    treatment_plan: Optional[str] = Field(default=None, comment="治疗方案")
    remark: Optional[str] = Field(default=None, comment="备注")


class MedicalRecordCreateSchema(BaseModel):
    """MedicalRecord CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    registration_id: UUID = Field(..., comment="挂号ID")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: UUID = Field(..., comment="医生ID")
    chief_complaint: Optional[str] = Field(default=None, comment="主诉")
    present_illness: Optional[str] = Field(default=None, comment="现病史")
    past_history: Optional[str] = Field(default=None, comment="既往史")
    physical_examination: Optional[str] = Field(default=None, comment="体格检查")
    diagnosis: Optional[str] = Field(default=None, comment="诊断")
    treatment_plan: Optional[str] = Field(default=None, comment="治疗方案")
    remark: Optional[str] = Field(default=None, comment="备注")


class MedicalRecordUpdateSchema(BaseModel):
    """MedicalRecord UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    registration_id: UUID = Field(..., comment="挂号ID")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: UUID = Field(..., comment="医生ID")
    chief_complaint: Optional[str] = Field(default=None, comment="主诉")
    present_illness: Optional[str] = Field(default=None, comment="现病史")
    past_history: Optional[str] = Field(default=None, comment="既往史")
    physical_examination: Optional[str] = Field(default=None, comment="体格检查")
    diagnosis: Optional[str] = Field(default=None, comment="诊断")
    treatment_plan: Optional[str] = Field(default=None, comment="治疗方案")
    remark: Optional[str] = Field(default=None, comment="备注")


class PrescriptionSchema(BaseSchema):
    """Prescription Schema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID（可不关联病历独立开方）")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: UUID = Field(..., comment="医生ID")
    prescription_no: str = Field(..., comment="处方单号")
    prescription_type: Optional[str] = Field(default=None, comment="处方类型：western/traditional/chinese_medicine")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/dispensed/cancelled")
    items: Optional[Any] = Field(default=None, comment="处方项目（JSON）")
    remark: Optional[str] = Field(default=None, comment="备注")

    # 以下为联表富化字段（患者姓名需解密，不在 ORM 模型上）
    patient_name: Optional[str] = Field(default=None, comment="患者姓名（解密后）")
    patient_no: Optional[str] = Field(default=None, comment="患者档案号")
    doctor_name: Optional[str] = Field(default=None, comment="医生姓名")


class PrescriptionCreateSchema(BaseModel):
    """Prescription CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID（可不关联病历独立开方）")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: UUID = Field(..., comment="医生ID")
    prescription_no: Optional[str] = Field(default=None, comment="处方单号（不传则自动生成）")
    prescription_type: Optional[str] = Field(default=None, comment="处方类型：western/traditional/chinese_medicine")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/dispensed/cancelled")
    items: Optional[Any] = Field(default=None, comment="处方项目（JSON）")
    remark: Optional[str] = Field(default=None, comment="备注")


class PrescriptionUpdateSchema(BaseModel):
    """Prescription UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID（可不关联病历独立开方）")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: UUID = Field(..., comment="医生ID")
    prescription_no: Optional[str] = Field(default=None, comment="处方单号")
    prescription_type: Optional[str] = Field(default=None, comment="处方类型：western/traditional/chinese_medicine")
    total_amount: Optional[float] = Field(default=None, comment="总金额")
    status: Optional[str] = Field(default=None, comment="状态：pending/dispensed/cancelled")
    items: Optional[Any] = Field(default=None, comment="处方项目（JSON）")
    remark: Optional[str] = Field(default=None, comment="备注")
