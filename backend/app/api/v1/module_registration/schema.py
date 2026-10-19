"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr
from datetime import date
from datetime import time


class ScheduleSchema(BaseSchema):
    """Schedule Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., comment="排班ID")
    doctor_id: UUID = Field(..., comment="医生ID")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    schedule_date: date = Field(..., comment="排班日期")
    time_slot: str = Field(..., comment="时段：morning/afternoon/evening")
    start_time: time = Field(..., comment="开始时间")
    end_time: time = Field(..., comment="结束时间")
    total_quota: Optional[int] = Field(default=None, comment="总号源")
    used_quota: Optional[int] = Field(default=None, comment="已用号源")
    price: Optional[float] = Field(default=None, comment="挂号费")
    status: Optional[str] = Field(default=None, comment="状态：active正常、paused暂停、cancelled取消")


class ScheduleCreateSchema(BaseModel):
    """Schedule CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    doctor_id: UUID = Field(..., comment="医生ID")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    schedule_date: date = Field(..., comment="排班日期")
    time_slot: str = Field(..., comment="时段：morning/afternoon/evening")
    start_time: time = Field(..., comment="开始时间")
    end_time: time = Field(..., comment="结束时间")
    total_quota: Optional[int] = Field(default=None, comment="总号源")
    used_quota: Optional[int] = Field(default=None, comment="已用号源")
    price: Optional[float] = Field(default=None, comment="挂号费")
    status: Optional[str] = Field(default=None, comment="状态：active正常、paused暂停、cancelled取消")


class ScheduleUpdateSchema(BaseModel):
    """Schedule UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    doctor_id: UUID = Field(..., comment="医生ID")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    schedule_date: date = Field(..., comment="排班日期")
    time_slot: str = Field(..., comment="时段：morning/afternoon/evening")
    start_time: time = Field(..., comment="开始时间")
    end_time: time = Field(..., comment="结束时间")
    total_quota: Optional[int] = Field(default=None, comment="总号源")
    used_quota: Optional[int] = Field(default=None, comment="已用号源")
    price: Optional[float] = Field(default=None, comment="挂号费")
    status: Optional[str] = Field(default=None, comment="状态：active正常、paused暂停、cancelled取消")


class RegistrationSchema(BaseSchema):
    """Registration Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., comment="挂号ID")
    registration_no: str = Field(..., comment="挂号单号")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: Optional[UUID] = Field(default=None, comment="医生ID")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    schedule_id: Optional[UUID] = Field(default=None, comment="排班ID")
    registration_date: date = Field(..., comment="挂号日期")
    registration_time: Optional[time] = Field(default=None, comment="挂号时间")
    visit_time: Optional[DateTimeStr] = Field(default=None, comment="就诊时间")
    registration_type: str = Field(..., comment="类型：onsite/appointment/wechat")
    status: Optional[str] = Field(default=None, comment="状态：pending/completed/cancelled")
    price: Optional[float] = Field(default=None, comment="挂号费")
    paid_amount: Optional[float] = Field(default=None, comment="已支付金额")
    payment_status: Optional[str] = Field(default=None, comment="支付状态")
    remark: Optional[str] = Field(default=None, comment="备注")

    # 以下为联表富化字段（患者姓名需解密，不在 ORM 模型上）
    patient_name: Optional[str] = Field(default=None, comment="患者姓名（解密后）")
    patient_no: Optional[str] = Field(default=None, comment="患者档案号")
    patient_phone: Optional[str] = Field(default=None, comment="患者手机号")
    doctor_name: Optional[str] = Field(default=None, comment="医生姓名")
    department_name: Optional[str] = Field(default=None, comment="科室名称")
    appointment_time: Optional[str] = Field(default=None, comment="预约时间（就诊时间或挂号日期）")


class RegistrationCreateSchema(BaseModel):
    """Registration CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    registration_no: Optional[str] = Field(default=None, comment="挂号单号（不传则自动生成）")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: Optional[UUID] = Field(default=None, comment="医生ID")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    schedule_id: Optional[UUID] = Field(default=None, comment="排班ID")
    registration_date: date = Field(..., comment="挂号日期")
    registration_time: Optional[time] = Field(default=None, comment="挂号时间")
    visit_time: Optional[DateTimeStr] = Field(default=None, comment="就诊时间")
    registration_type: str = Field(..., comment="类型：onsite/appointment/wechat")
    status: Optional[str] = Field(default=None, comment="状态：pending/completed/cancelled")
    price: Optional[float] = Field(default=None, comment="挂号费")
    paid_amount: Optional[float] = Field(default=None, comment="已支付金额")
    payment_status: Optional[str] = Field(default=None, comment="支付状态")
    remark: Optional[str] = Field(default=None, comment="备注")


class RegistrationUpdateSchema(BaseModel):
    """Registration UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    registration_no: Optional[str] = Field(default=None, comment="挂号单号")
    patient_id: UUID = Field(..., comment="患者ID")
    doctor_id: Optional[UUID] = Field(default=None, comment="医生ID")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    schedule_id: Optional[UUID] = Field(default=None, comment="排班ID")
    registration_date: date = Field(..., comment="挂号日期")
    registration_time: Optional[time] = Field(default=None, comment="挂号时间")
    visit_time: Optional[DateTimeStr] = Field(default=None, comment="就诊时间")
    registration_type: str = Field(..., comment="类型：onsite/appointment/wechat")
    status: Optional[str] = Field(default=None, comment="状态：pending/completed/cancelled")
    price: Optional[float] = Field(default=None, comment="挂号费")
    paid_amount: Optional[float] = Field(default=None, comment="已支付金额")
    payment_status: Optional[str] = Field(default=None, comment="支付状态")
    remark: Optional[str] = Field(default=None, comment="备注")
