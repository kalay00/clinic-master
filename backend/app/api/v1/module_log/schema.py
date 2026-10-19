"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr
from typing import Any


class OperationLogSchema(BaseSchema):
    """OperationLog Schema"""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = Field(default=None, comment="主键ID")
    tenant_id: Optional[UUID] = Field(default=None, comment="租户ID（可为NULL，表示系统级日志）")
    user_id: Optional[UUID] = Field(default=None, comment="用户ID")
    operation_type: str = Field(..., comment="操作类型：create/update/delete/query")
    resource_type: str = Field(..., comment="资源类型：patient/registration等")
    resource_id: Optional[UUID] = Field(default=None, comment="资源ID")
    operation_desc: Optional[str] = Field(default=None, comment="操作描述")
    request_data: Optional[Any] = Field(default=None, comment="请求数据")
    response_data: Optional[Any] = Field(default=None, comment="响应数据")
    ip_address: Optional[str] = Field(default=None, comment="IP地址")
    user_agent: Optional[str] = Field(default=None, comment="用户代理")
    status: Optional[str] = Field(default=None, comment="状态：success/failed")
    error_message: Optional[str] = Field(default=None, comment="错误信息")
    created_at: DateTimeStr = Field(..., comment="创建时间")


class OperationLogCreateSchema(BaseModel):
    """OperationLog CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[UUID] = Field(default=None, comment="用户ID")
    operation_type: str = Field(..., comment="操作类型：create/update/delete/query")
    resource_type: str = Field(..., comment="资源类型：patient/registration等")
    resource_id: Optional[UUID] = Field(default=None, comment="资源ID")
    operation_desc: Optional[str] = Field(default=None, comment="操作描述")
    request_data: Optional[Any] = Field(default=None, comment="请求数据")
    response_data: Optional[Any] = Field(default=None, comment="响应数据")
    ip_address: Optional[str] = Field(default=None, comment="IP地址")
    user_agent: Optional[str] = Field(default=None, comment="用户代理")
    status: Optional[str] = Field(default=None, comment="状态：success/failed")
    error_message: Optional[str] = Field(default=None, comment="错误信息")


class OperationLogUpdateSchema(BaseModel):
    """OperationLog UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    user_id: Optional[UUID] = Field(default=None, comment="用户ID")
    operation_type: str = Field(..., comment="操作类型：create/update/delete/query")
    resource_type: str = Field(..., comment="资源类型：patient/registration等")
    resource_id: Optional[UUID] = Field(default=None, comment="资源ID")
    operation_desc: Optional[str] = Field(default=None, comment="操作描述")
    request_data: Optional[Any] = Field(default=None, comment="请求数据")
    response_data: Optional[Any] = Field(default=None, comment="响应数据")
    ip_address: Optional[str] = Field(default=None, comment="IP地址")
    user_agent: Optional[str] = Field(default=None, comment="用户代理")
    status: Optional[str] = Field(default=None, comment="状态：success/failed")
    error_message: Optional[str] = Field(default=None, comment="错误信息")
