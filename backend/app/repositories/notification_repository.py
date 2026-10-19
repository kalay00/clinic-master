"""
通知数据仓库
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from uuid import UUID

from app.api.v1.module_notification.model import Notification
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class NotificationRepository:
    """通知数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(self, notification_data: dict, tenant_id: str) -> Notification:
        """创建通知"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        notification = Notification(
            tenant_id=tenant_id,
            **notification_data
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def get_notification_by_id(
        self,
        notification_id: str,
        tenant_id: str
    ) -> Optional[Notification]:
        """根据ID获取通知"""
        if isinstance(notification_id, str):
            notification_id = UUID(notification_id)
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        return self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.tenant_id == tenant_id,
                Notification.deleted_at.is_(None)
            )
        ).first()
    
    def get_notifications(
        self,
        tenant_id: str,
        recipient_type: Optional[str] = None,
        recipient_id: Optional[str] = None,
        status: Optional[str] = None,
        notification_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Notification], int]:
        """获取通知列表"""
        if isinstance(tenant_id, str):
            tenant_id = UUID(tenant_id)
        
        query = self.db.query(Notification).filter(
            and_(
                Notification.tenant_id == tenant_id,
                Notification.deleted_at.is_(None)
            )
        )
        
        if recipient_type:
            query = query.filter(Notification.recipient_type == recipient_type)
        
        if recipient_id:
            if isinstance(recipient_id, str):
                recipient_id = UUID(recipient_id)
            query = query.filter(Notification.recipient_id == recipient_id)
        
        if status:
            query = query.filter(Notification.status == status)
        
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        
        query = query.order_by(desc(Notification.created_at))
        
        total = query.count()
        notifications = query.offset(skip).limit(limit).all()
        return notifications, total
    
    def update_notification(
        self,
        notification_id: str,
        tenant_id: str,
        notification_data: dict
    ) -> Notification:
        """更新通知"""
        notification = self.get_notification_by_id(notification_id, tenant_id)
        if not notification:
            raise NotFoundException("通知", notification_id)
        
        for key, value in notification_data.items():
            if hasattr(notification, key):
                setattr(notification, key, value)
        
        self.db.commit()
        self.db.refresh(notification)
        return notification

