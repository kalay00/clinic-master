"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema


class DepartmentSchema(BaseSchema):
    """Department Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., comment="科室ID")
    tenant_id: UUID = Field(..., comment="租户ID")
    name: str = Field(..., comment="科室名称")
    code: str = Field(..., comment="科室编码")
    description: Optional[str] = Field(default=None, comment="科室描述")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    sort_order: Optional[int] = Field(default=None, comment="排序")


class DepartmentCreateSchema(BaseModel):
    """Department CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="科室名称")
    code: str = Field(..., comment="科室编码")
    description: Optional[str] = Field(default=None, comment="科室描述")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    sort_order: Optional[int] = Field(default=None, comment="排序")


class DepartmentUpdateSchema(BaseModel):
    """Department UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., comment="科室名称")
    code: str = Field(..., comment="科室编码")
    description: Optional[str] = Field(default=None, comment="科室描述")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
    sort_order: Optional[int] = Field(default=None, comment="排序")


class DoctorSchema(BaseSchema):
    """Doctor Schema"""

    model_config = ConfigDict(from_attributes=True)

    tenant_id: UUID = Field(..., comment="租户ID")
    user_id: Optional[UUID] = Field(default=None, comment="关联用户ID")
    name: str = Field(..., comment="医生姓名")
    employee_no: str = Field(..., comment="工号")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    title: Optional[str] = Field(default=None, comment="职称：主任医师/副主任医师/主治医师/住院医师")
    specialty: Optional[str] = Field(default=None, comment="专业特长")
    phone: Optional[str] = Field(default=None, comment="联系电话")
    email: Optional[str] = Field(default=None, comment="邮箱")
    registration_fee: Optional[float] = Field(default=None, comment="默认挂号费")
    bio: Optional[str] = Field(default=None, comment="医生简介")
    photo_url: Optional[str] = Field(default=None, comment="医生照片URL")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")


class DoctorCreateSchema(BaseModel):
    """Doctor CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[UUID] = Field(default=None, comment="关联用户ID")
    name: str = Field(..., comment="医生姓名")
    employee_no: str = Field(..., comment="工号")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    title: Optional[str] = Field(default=None, comment="职称：主任医师/副主任医师/主治医师/住院医师")
    specialty: Optional[str] = Field(default=None, comment="专业特长")
    phone: Optional[str] = Field(default=None, comment="联系电话")
    email: Optional[str] = Field(default=None, comment="邮箱")
    registration_fee: Optional[float] = Field(default=None, comment="默认挂号费")
    bio: Optional[str] = Field(default=None, comment="医生简介")
    photo_url: Optional[str] = Field(default=None, comment="医生照片URL")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")


class DoctorUpdateSchema(BaseModel):
    """Doctor UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[UUID] = Field(default=None, comment="关联用户ID")
    name: str = Field(..., comment="医生姓名")
    employee_no: str = Field(..., comment="工号")
    department_id: Optional[UUID] = Field(default=None, comment="科室ID")
    title: Optional[str] = Field(default=None, comment="职称：主任医师/副主任医师/主治医师/住院医师")
    specialty: Optional[str] = Field(default=None, comment="专业特长")
    phone: Optional[str] = Field(default=None, comment="联系电话")
    email: Optional[str] = Field(default=None, comment="邮箱")
    registration_fee: Optional[float] = Field(default=None, comment="默认挂号费")
    bio: Optional[str] = Field(default=None, comment="医生简介")
    photo_url: Optional[str] = Field(default=None, comment="医生照片URL")
    status: Optional[str] = Field(default=None, comment="状态：active/inactive")
