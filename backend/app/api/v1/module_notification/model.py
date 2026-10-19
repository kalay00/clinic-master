"""
通知模块 ORM 模型（单一数据源）
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func

from app.core.database import BaseModel


class Notification(BaseModel):
    """通知表"""
    __tablename__ = "notifications"
    
    notification_type = Column(String(50), nullable=False, comment="类型：sms/wechat/email")
    recipient_type = Column(String(20), nullable=False, comment="接收者类型：patient/user")
    recipient_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment="接收者ID")
    recipient_info = Column(String(255), comment="接收者信息（手机号、微信号等）")
    title = Column(String(200), comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    template_id = Column(String(50), comment="模板ID")
    status = Column(String(20), default="pending", index=True, comment="状态：pending/sent/failed")
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="发送时间")
    error_message = Column(Text, comment="错误信息")
    
    __table_args__ = (
        {"comment": "通知表"},
    )
