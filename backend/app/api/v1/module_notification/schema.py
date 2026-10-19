"""
Pydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from app.core.base_schema import BaseSchema

from app.core.validator import DateTimeStr


class NotificationSchema(BaseSchema):
    """Notification Schema"""

    model_config = ConfigDict(from_attributes=True)

    notification_type: str = Field(..., comment="类型：sms/wechat/email")
    recipient_type: str = Field(..., comment="接收者类型：patient/user")
    recipient_id: UUID = Field(..., comment="接收者ID")
    recipient_info: Optional[str] = Field(default=None, comment="接收者信息（手机号、微信号等）")
    title: Optional[str] = Field(default=None, comment="标题")
    content: str = Field(..., comment="内容")
    template_id: Optional[UUID] = Field(default=None, comment="模板ID")
    status: Optional[str] = Field(default=None, comment="状态：pending/sent/failed")
    sent_at: Optional[DateTimeStr] = Field(default=None, comment="发送时间")
    error_message: Optional[str] = Field(default=None, comment="错误信息")


class NotificationCreateSchema(BaseModel):
    """Notification CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    notification_type: str = Field(..., comment="类型：sms/wechat/email")
    recipient_type: str = Field(..., comment="接收者类型：patient/user")
    recipient_id: UUID = Field(..., comment="接收者ID")
    recipient_info: Optional[str] = Field(default=None, comment="接收者信息（手机号、微信号等）")
    title: Optional[str] = Field(default=None, comment="标题")
    content: str = Field(..., comment="内容")
    template_id: Optional[UUID] = Field(default=None, comment="模板ID")
    status: Optional[str] = Field(default=None, comment="状态：pending/sent/failed")
    sent_at: Optional[DateTimeStr] = Field(default=None, comment="发送时间")
    error_message: Optional[str] = Field(default=None, comment="错误信息")


class NotificationUpdateSchema(BaseModel):
    """Notification UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    notification_type: str = Field(..., comment="类型：sms/wechat/email")
    recipient_type: str = Field(..., comment="接收者类型：patient/user")
    recipient_id: UUID = Field(..., comment="接收者ID")
    recipient_info: Optional[str] = Field(default=None, comment="接收者信息（手机号、微信号等）")
    title: Optional[str] = Field(default=None, comment="标题")
    content: str = Field(..., comment="内容")
    template_id: Optional[UUID] = Field(default=None, comment="模板ID")
    status: Optional[str] = Field(default=None, comment="状态：pending/sent/failed")
    sent_at: Optional[DateTimeStr] = Field(default=None, comment="发送时间")
    error_message: Optional[str] = Field(default=None, comment="错误信息")
