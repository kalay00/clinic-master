"""
患者 Pydantic 模型（对齐 FastapiAdmin: module_hospital/patient/schema.py）
schema.py: 创建 / 更新 / 响应模型
"""
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Any

from app.core.base_schema import BaseSchema
from app.core.validator import DateStr


class FamilyMemberSchema(BaseSchema):
    """家庭成员输出模型"""
    patient_id: Optional[Any] = Field(default=None, description="患者ID")
    relation: Optional[str] = Field(default=None, description="家庭关系")
    name: Optional[str] = Field(default=None, description="姓名")
    gender: Optional[str] = Field(default=None, description="性别：male/female")
    birthday: Optional[DateStr] = Field(default=None, description="出生日期")
    age: Optional[int] = Field(default=None, description="年龄")
    phone: Optional[str] = Field(default=None, description="手机号码")


class FamilyMemberCreateSchema(BaseModel):
    """家庭成员创建模型"""
    relation: str = Field(..., description="家庭关系")
    name: str = Field(..., description="姓名")
    gender: Optional[str] = Field(default=None, description="性别：male/female")
    birthday: Optional[str] = Field(default=None, description="出生日期")
    age: Optional[int] = Field(default=None, description="年龄")
    phone: Optional[str] = Field(default=None, description="手机号码")


class FamilyMemberUpdateSchema(BaseModel):
    """家庭成员更新模型"""
    relation: Optional[str] = Field(default=None, description="家庭关系")
    name: Optional[str] = Field(default=None, description="姓名")
    gender: Optional[str] = Field(default=None, description="性别：male/female")
    birthday: Optional[str] = Field(default=None, description="出生日期")
    age: Optional[int] = Field(default=None, description="年龄")
    phone: Optional[str] = Field(default=None, description="手机号码")


class PatientCreateSchema(BaseModel):
    """创建患者请求模型"""

    patient_no: Optional[str] = Field(default=None, max_length=50, description="档案号（可选，系统自动生成）")
    name: str = Field(..., min_length=1, max_length=50, description="患者姓名")
    id_card: str = Field(..., min_length=15, max_length=18, description="身份证号")
    gender: Optional[str] = Field(default=None, description="性别：male/female/other")
    birthday: Optional[date] = Field(default=None, description="出生日期")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    address: Optional[str] = Field(default=None, description="地址")
    emergency_contact: Optional[str] = Field(default=None, max_length=50, description="紧急联系人")
    emergency_phone: Optional[str] = Field(default=None, max_length=20, description="紧急联系电话")
    blood_type: Optional[str] = Field(default=None, description="血型：A/B/AB/O")
    allergy_history: Optional[str] = Field(default=None, description="过敏史")
    chronic_disease: Optional[str] = Field(default=None, description="慢性病史")
    remark: Optional[str] = Field(default=None, description="备注")
    member_level_id: Optional[str] = Field(default=None, description="会员等级ID")

    @model_validator(mode="before")
    @classmethod
    def _empty_str_to_none(cls, data):
        # 前端未填写的可选字段常以空字符串发送，统一转为 None，避免可选字段校验失败
        if isinstance(data, dict):
            for key, value in data.items():
                if value == "":
                    data[key] = None
        return data

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("性别必须是以下值之一: male, female, other")
        return v

    @field_validator("blood_type")
    @classmethod
    def validate_blood_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["A", "B", "AB", "O"]:
            raise ValueError("血型必须是以下值之一: A, B, AB, O")
        return v

    @field_validator("id_card")
    @classmethod
    def validate_id_card(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("身份证号不能为空")
        if len(v) not in [15, 18]:
            raise ValueError("身份证号必须是15位或18位")
        return v


class PatientUpdateSchema(BaseModel):
    """更新患者请求模型"""

    patient_no: Optional[str] = Field(default=None, max_length=50, description="档案号")
    name: Optional[str] = Field(default=None, min_length=1, max_length=50, description="患者姓名")
    id_card: Optional[str] = Field(default=None, min_length=15, max_length=18, description="身份证号")
    gender: Optional[str] = Field(default=None, description="性别：male/female/other")
    birthday: Optional[date] = Field(default=None, description="出生日期")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    address: Optional[str] = Field(default=None, description="地址")
    emergency_contact: Optional[str] = Field(default=None, max_length=50, description="紧急联系人")
    emergency_phone: Optional[str] = Field(default=None, max_length=20, description="紧急联系电话")
    blood_type: Optional[str] = Field(default=None, description="血型：A/B/AB/O")
    allergy_history: Optional[str] = Field(default=None, description="过敏史")
    chronic_disease: Optional[str] = Field(default=None, description="慢性病史")
    remark: Optional[str] = Field(default=None, description="备注")
    member_level_id: Optional[str] = Field(default=None, description="会员等级ID")

    @model_validator(mode="before")
    @classmethod
    def _empty_str_to_none(cls, data):
        # 前端未填写的可选字段常以空字符串发送，统一转为 None，避免可选字段校验失败
        if isinstance(data, dict):
            for key, value in data.items():
                if value == "":
                    data[key] = None
        return data

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("性别必须是以下值之一: male, female, other")
        return v

    @field_validator("blood_type")
    @classmethod
    def validate_blood_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["A", "B", "AB", "O"]:
            raise ValueError("血型必须是以下值之一: A, B, AB, O")
        return v

    @field_validator("id_card")
    @classmethod
    def validate_id_card(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) not in [15, 18]:
                raise ValueError("身份证号必须是15位或18位")
        return v


class PatientSchema(BaseSchema):
    """患者响应模型"""

    model_config = ConfigDict(from_attributes=True)

    patient_no: str = Field(..., description="档案号")
    name: Optional[str] = Field(default=None, description="患者姓名")
    id_card: Optional[str] = Field(default=None, description="身份证号")
    gender: Optional[str] = Field(default=None, description="性别")
    birthday: Optional[date] = Field(default=None, description="出生日期")
    birth_date: Optional[str] = Field(default=None, description="出生日期（ISO 字符串，兼容前端）")
    phone: Optional[str] = Field(default=None, description="手机号")
    address: Optional[str] = Field(default=None, description="地址")
    emergency_contact: Optional[str] = Field(default=None, description="紧急联系人")
    emergency_phone: Optional[str] = Field(default=None, description="紧急联系电话")
    blood_type: Optional[str] = Field(default=None, description="血型")
    allergy_history: Optional[str] = Field(default=None, description="过敏史")
    chronic_disease: Optional[str] = Field(default=None, description="慢性病史")
    remark: Optional[str] = Field(default=None, description="备注")
    member_level_id: Optional[str] = Field(default=None, description="会员等级ID")
    age: Optional[int] = Field(default=None, description="年龄")
    balance: float = Field(0, description="账户余额")
    points: int = Field(0, description="积分")

    @model_validator(mode="before")
    @classmethod
    def prepare(cls, data: dict) -> dict:
        if isinstance(data, dict) and data.get("birthday") and not data.get("birth_date"):
            b = data["birthday"]
            data["birth_date"] = b.isoformat() if hasattr(b, "isoformat") else str(b)
        if isinstance(data, dict) and data.get("birthday"):
            from datetime import date as _date

            b = data["birthday"]
            if isinstance(b, str):
                try:
                    b = _date.fromisoformat(b)
                except ValueError:
                    b = None
            if isinstance(b, _date):
                today = _date.today()
                age = today.year - b.year
                if (today.month, today.day) < (b.month, b.day):
                    age -= 1
                data["age"] = age
        return data


class PatientRechargeSchema(BaseModel):
    """患者余额充值请求（含赠送计算）"""

    model_config = ConfigDict(from_attributes=True)

    amount: float = Field(..., gt=0, description="充值金额")
    method: Optional[str] = Field(default=None, description="支付方式：cash/wechat/alipay/bank")
    remark: Optional[str] = Field(default=None, description="备注")
