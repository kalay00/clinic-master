"""
技师模块 Schema
"""
from typing import Optional
from pydantic import BaseModel, Field
from app.core.base_schema import BaseSchema


class TechnicianSchema(BaseSchema):
    name: str = Field(..., description="技师姓名")
    phone: Optional[str] = Field(None, description="联系电话")
    gender: Optional[str] = Field(None, description="性别")
    skills: Optional[str] = Field(None, description="擅长项目/技能")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class TechnicianCreateSchema(BaseModel):
    name: str = Field(..., description="技师姓名")
    phone: Optional[str] = Field(None, description="联系电话")
    gender: Optional[str] = Field(None, description="性别")
    skills: Optional[str] = Field(None, description="擅长项目/技能")
    status: str = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class TechnicianUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, description="技师姓名")
    phone: Optional[str] = Field(None, description="联系电话")
    gender: Optional[str] = Field(None, description="性别")
    skills: Optional[str] = Field(None, description="擅长项目/技能")
    status: Optional[str] = Field(None, description="状态")
    remark: Optional[str] = Field(None, description="备注")
