"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr


class DiagnosisSchema(BaseSchema):
    """Diagnosis Schema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    icd_code: Optional[str] = Field(default=None, comment="ICD编码")
    diagnosis_name: str = Field(..., comment="诊断名称")
    diagnosis_type: Optional[str] = Field(default=None, comment="类型：primary/secondary")
    description: Optional[str] = Field(default=None, comment="描述")


class DiagnosisCreateSchema(BaseModel):
    """Diagnosis CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    icd_code: Optional[str] = Field(default=None, comment="ICD编码")
    diagnosis_name: str = Field(..., comment="诊断名称")
    diagnosis_type: Optional[str] = Field(default=None, comment="类型：primary/secondary")
    description: Optional[str] = Field(default=None, comment="描述")


class DiagnosisUpdateSchema(BaseModel):
    """Diagnosis UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    icd_code: Optional[str] = Field(default=None, comment="ICD编码")
    diagnosis_name: str = Field(..., comment="诊断名称")
    diagnosis_type: Optional[str] = Field(default=None, comment="类型：primary/secondary")
    description: Optional[str] = Field(default=None, comment="描述")


class TCMDiagnosisSchema(BaseSchema):
    """TCMDiagnosis Schema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    syndrome_type: Optional[str] = Field(default=None, comment="证型")
    pathogenesis: Optional[str] = Field(default=None, comment="病机")
    disease_name: Optional[str] = Field(default=None, comment="病名")
    constitution_type: Optional[str] = Field(default=None, comment="体质类型（九种体质）")
    constitution_desc: Optional[str] = Field(default=None, comment="体质描述")
    tongue_state: Optional[str] = Field(default=None, comment="舌象")
    pulse_state: Optional[str] = Field(default=None, comment="脉象")
    tcm_diagnosis: Optional[str] = Field(default=None, comment="中医诊断")
    treatment_principle: Optional[str] = Field(default=None, comment="治则")
    treatment_method: Optional[str] = Field(default=None, comment="治法")


class TCMDiagnosisCreateSchema(BaseModel):
    """TCMDiagnosis CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    syndrome_type: Optional[str] = Field(default=None, comment="证型")
    pathogenesis: Optional[str] = Field(default=None, comment="病机")
    disease_name: Optional[str] = Field(default=None, comment="病名")
    constitution_type: Optional[str] = Field(default=None, comment="体质类型（九种体质）")
    constitution_desc: Optional[str] = Field(default=None, comment="体质描述")
    tongue_state: Optional[str] = Field(default=None, comment="舌象")
    pulse_state: Optional[str] = Field(default=None, comment="脉象")
    tcm_diagnosis: Optional[str] = Field(default=None, comment="中医诊断")
    treatment_principle: Optional[str] = Field(default=None, comment="治则")
    treatment_method: Optional[str] = Field(default=None, comment="治法")


class TCMDiagnosisUpdateSchema(BaseModel):
    """TCMDiagnosis UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    syndrome_type: Optional[str] = Field(default=None, comment="证型")
    pathogenesis: Optional[str] = Field(default=None, comment="病机")
    disease_name: Optional[str] = Field(default=None, comment="病名")
    constitution_type: Optional[str] = Field(default=None, comment="体质类型（九种体质）")
    constitution_desc: Optional[str] = Field(default=None, comment="体质描述")
    tongue_state: Optional[str] = Field(default=None, comment="舌象")
    pulse_state: Optional[str] = Field(default=None, comment="脉象")
    tcm_diagnosis: Optional[str] = Field(default=None, comment="中医诊断")
    treatment_principle: Optional[str] = Field(default=None, comment="治则")
    treatment_method: Optional[str] = Field(default=None, comment="治法")


class TCMFourExaminationsSchema(BaseSchema):
    """TCMFourExaminations Schema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    inspection: Optional[str] = Field(default=None, comment="望诊")
    listening_smelling: Optional[str] = Field(default=None, comment="闻诊")
    inquiry: Optional[str] = Field(default=None, comment="问诊")
    pulse_feeling: Optional[str] = Field(default=None, comment="切诊（脉诊）")


class TCMFourExaminationsCreateSchema(BaseModel):
    """TCMFourExaminations CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    inspection: Optional[str] = Field(default=None, comment="望诊")
    listening_smelling: Optional[str] = Field(default=None, comment="闻诊")
    inquiry: Optional[str] = Field(default=None, comment="问诊")
    pulse_feeling: Optional[str] = Field(default=None, comment="切诊（脉诊）")


class TCMFourExaminationsUpdateSchema(BaseModel):
    """TCMFourExaminations UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    inspection: Optional[str] = Field(default=None, comment="望诊")
    listening_smelling: Optional[str] = Field(default=None, comment="闻诊")
    inquiry: Optional[str] = Field(default=None, comment="问诊")
    pulse_feeling: Optional[str] = Field(default=None, comment="切诊（脉诊）")


class TCMTreatmentSchema(BaseSchema):
    """TCMTreatment Schema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    treatment_type: str = Field(..., comment="治疗类型：acupuncture/massage/cupping/moxibustion")
    treatment_name: str = Field(..., comment="治疗方法名称")
    treatment_points: Optional[str] = Field(default=None, comment="治疗穴位/部位")
    treatment_duration: Optional[int] = Field(default=None, comment="治疗时长（分钟）")
    treatment_frequency: Optional[str] = Field(default=None, comment="治疗频次")
    treatment_course: Optional[int] = Field(default=None, comment="疗程（次数）")
    remark: Optional[str] = Field(default=None, comment="备注")


class TCMTreatmentCreateSchema(BaseModel):
    """TCMTreatment CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    treatment_type: str = Field(..., comment="治疗类型：acupuncture/massage/cupping/moxibustion")
    treatment_name: str = Field(..., comment="治疗方法名称")
    treatment_points: Optional[str] = Field(default=None, comment="治疗穴位/部位")
    treatment_duration: Optional[int] = Field(default=None, comment="治疗时长（分钟）")
    treatment_frequency: Optional[str] = Field(default=None, comment="治疗频次")
    treatment_course: Optional[int] = Field(default=None, comment="疗程（次数）")
    remark: Optional[str] = Field(default=None, comment="备注")


class TCMTreatmentUpdateSchema(BaseModel):
    """TCMTreatment UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    medical_record_id: UUID = Field(..., comment="病历ID")
    treatment_type: str = Field(..., comment="治疗类型：acupuncture/massage/cupping/moxibustion")
    treatment_name: str = Field(..., comment="治疗方法名称")
    treatment_points: Optional[str] = Field(default=None, comment="治疗穴位/部位")
    treatment_duration: Optional[int] = Field(default=None, comment="治疗时长（分钟）")
    treatment_frequency: Optional[str] = Field(default=None, comment="治疗频次")
    treatment_course: Optional[int] = Field(default=None, comment="疗程（次数）")
    remark: Optional[str] = Field(default=None, comment="备注")


class TCMPrescriptionSchema(BaseSchema):
    """TCMPrescription Schema"""

    model_config = ConfigDict(from_attributes=True)

    prescription_id: Optional[UUID] = Field(default=None, comment="关联通用处方")
    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID")
    prescription_no: str = Field(..., comment="处方号")
    prescription_type: Optional[str] = Field(default=None, comment="处方类型：classical/empirical/agreed")
    prescription_name: Optional[str] = Field(default=None, comment="方剂名称")
    decoction_method: Optional[str] = Field(default=None, comment="煎服法")
    dosage_days: Optional[int] = Field(default=None, comment="服药天数")
    total_dose: Optional[float] = Field(default=None, comment="总剂量")
    decoction_service: Optional[bool] = Field(default=None, comment="是否代煎")


class TCMPrescriptionCreateSchema(BaseModel):
    """TCMPrescription CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    prescription_id: Optional[UUID] = Field(default=None, comment="关联通用处方")
    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID")
    prescription_no: str = Field(..., comment="处方号")
    prescription_type: Optional[str] = Field(default=None, comment="处方类型：classical/empirical/agreed")
    prescription_name: Optional[str] = Field(default=None, comment="方剂名称")
    decoction_method: Optional[str] = Field(default=None, comment="煎服法")
    dosage_days: Optional[int] = Field(default=None, comment="服药天数")
    total_dose: Optional[float] = Field(default=None, comment="总剂量")
    decoction_service: Optional[bool] = Field(default=None, comment="是否代煎")


class TCMPrescriptionUpdateSchema(BaseModel):
    """TCMPrescription UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    prescription_id: Optional[UUID] = Field(default=None, comment="关联通用处方")
    medical_record_id: Optional[UUID] = Field(default=None, comment="病历ID")
    prescription_no: str = Field(..., comment="处方号")
    prescription_type: Optional[str] = Field(default=None, comment="处方类型：classical/empirical/agreed")
    prescription_name: Optional[str] = Field(default=None, comment="方剂名称")
    decoction_method: Optional[str] = Field(default=None, comment="煎服法")
    dosage_days: Optional[int] = Field(default=None, comment="服药天数")
    total_dose: Optional[float] = Field(default=None, comment="总剂量")
    decoction_service: Optional[bool] = Field(default=None, comment="是否代煎")


class TCMPrescriptionItemSchema(BaseSchema):
    """TCMPrescriptionItem Schema"""

    model_config = ConfigDict(from_attributes=True)

    tcm_prescription_id: UUID = Field(..., comment="中药处方ID")
    drug_id: UUID = Field(..., comment="药品ID")
    drug_name: str = Field(..., comment="药品名称")
    specification: Optional[str] = Field(default=None, comment="规格")
    unit: Optional[str] = Field(default=None, comment="单位（克、两、钱等）")
    quantity: float = Field(..., comment="数量")
    dosage_unit: Optional[str] = Field(default=None, comment="剂量单位")
    processing_method: Optional[str] = Field(default=None, comment="炮制方法")
    role_in_prescription: Optional[str] = Field(default=None, comment="方中作用（君、臣、佐、使）")
    remark: Optional[str] = Field(default=None, comment="备注")


class TCMPrescriptionItemCreateSchema(BaseModel):
    """TCMPrescriptionItem CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    tcm_prescription_id: UUID = Field(..., comment="中药处方ID")
    drug_id: UUID = Field(..., comment="药品ID")
    drug_name: str = Field(..., comment="药品名称")
    specification: Optional[str] = Field(default=None, comment="规格")
    unit: Optional[str] = Field(default=None, comment="单位（克、两、钱等）")
    quantity: float = Field(..., comment="数量")
    dosage_unit: Optional[str] = Field(default=None, comment="剂量单位")
    processing_method: Optional[str] = Field(default=None, comment="炮制方法")
    role_in_prescription: Optional[str] = Field(default=None, comment="方中作用（君、臣、佐、使）")
    remark: Optional[str] = Field(default=None, comment="备注")


class TCMPrescriptionItemUpdateSchema(BaseModel):
    """TCMPrescriptionItem UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    tcm_prescription_id: UUID = Field(..., comment="中药处方ID")
    drug_id: UUID = Field(..., comment="药品ID")
    drug_name: str = Field(..., comment="药品名称")
    specification: Optional[str] = Field(default=None, comment="规格")
    unit: Optional[str] = Field(default=None, comment="单位（克、两、钱等）")
    quantity: float = Field(..., comment="数量")
    dosage_unit: Optional[str] = Field(default=None, comment="剂量单位")
    processing_method: Optional[str] = Field(default=None, comment="炮制方法")
    role_in_prescription: Optional[str] = Field(default=None, comment="方中作用（君、臣、佐、使）")
    remark: Optional[str] = Field(default=None, comment="备注")


class TCMFormulaSchema(BaseSchema):
    """TCMFormula Schema"""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: Optional[UUID] = Field(default=None, comment="租户ID（NULL表示系统方剂）")
    formula_name: str = Field(..., comment="方剂名称")
    formula_type: Optional[str] = Field(default=None, comment="方剂类型：classical/empirical/agreed")
    source: Optional[str] = Field(default=None, comment="来源")
    composition: Optional[str] = Field(default=None, comment="组成")
    functions: Optional[str] = Field(default=None, comment="功效")
    indications: Optional[str] = Field(default=None, comment="主治")
    contraindications: Optional[str] = Field(default=None, comment="禁忌")
    usage_method: Optional[str] = Field(default=None, comment="用法")


class TCMFormulaCreateSchema(BaseModel):
    """TCMFormula CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    formula_name: str = Field(..., comment="方剂名称")
    formula_type: Optional[str] = Field(default=None, comment="方剂类型：classical/empirical/agreed")
    source: Optional[str] = Field(default=None, comment="来源")
    composition: Optional[str] = Field(default=None, comment="组成")
    functions: Optional[str] = Field(default=None, comment="功效")
    indications: Optional[str] = Field(default=None, comment="主治")
    contraindications: Optional[str] = Field(default=None, comment="禁忌")
    usage_method: Optional[str] = Field(default=None, comment="用法")


class TCMFormulaUpdateSchema(BaseModel):
    """TCMFormula UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    formula_name: str = Field(..., comment="方剂名称")
    formula_type: Optional[str] = Field(default=None, comment="方剂类型：classical/empirical/agreed")
    source: Optional[str] = Field(default=None, comment="来源")
    composition: Optional[str] = Field(default=None, comment="组成")
    functions: Optional[str] = Field(default=None, comment="功效")
    indications: Optional[str] = Field(default=None, comment="主治")
    contraindications: Optional[str] = Field(default=None, comment="禁忌")
    usage_method: Optional[str] = Field(default=None, comment="用法")


class TCMDecoctionServiceSchema(BaseSchema):
    """TCMDecoctionService Schema"""

    model_config = ConfigDict(from_attributes=True)

    tcm_prescription_id: UUID = Field(..., comment="中药处方ID")
    service_type: Optional[str] = Field(default=None, comment="服务类型：decoction/grinding")
    status: Optional[str] = Field(default=None, comment="状态：pending/processing/completed")
    decoction_method: Optional[str] = Field(default=None, comment="煎药方法")
    decoction_start_time: Optional[DateTimeStr] = Field(default=None, comment="开始煎药时间")
    decoction_complete_time: Optional[DateTimeStr] = Field(default=None, comment="完成煎药时间")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    remark: Optional[str] = Field(default=None, comment="备注")


class TCMDecoctionServiceCreateSchema(BaseModel):
    """TCMDecoctionService CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    tcm_prescription_id: UUID = Field(..., comment="中药处方ID")
    service_type: Optional[str] = Field(default=None, comment="服务类型：decoction/grinding")
    status: Optional[str] = Field(default=None, comment="状态：pending/processing/completed")
    decoction_method: Optional[str] = Field(default=None, comment="煎药方法")
    decoction_start_time: Optional[DateTimeStr] = Field(default=None, comment="开始煎药时间")
    decoction_complete_time: Optional[DateTimeStr] = Field(default=None, comment="完成煎药时间")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    remark: Optional[str] = Field(default=None, comment="备注")


class TCMDecoctionServiceUpdateSchema(BaseModel):
    """TCMDecoctionService UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    tcm_prescription_id: UUID = Field(..., comment="中药处方ID")
    service_type: Optional[str] = Field(default=None, comment="服务类型：decoction/grinding")
    status: Optional[str] = Field(default=None, comment="状态：pending/processing/completed")
    decoction_method: Optional[str] = Field(default=None, comment="煎药方法")
    decoction_start_time: Optional[DateTimeStr] = Field(default=None, comment="开始煎药时间")
    decoction_complete_time: Optional[DateTimeStr] = Field(default=None, comment="完成煎药时间")
    operator_id: Optional[UUID] = Field(default=None, comment="操作人ID")
    remark: Optional[str] = Field(default=None, comment="备注")
