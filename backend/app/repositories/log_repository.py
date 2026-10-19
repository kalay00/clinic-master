"""
日志数据仓库：操作日志
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from uuid import UUID

from app.api.v1.module_log.model import OperationLog
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class OperationLogRepository:
    """操作日志数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_operation_log(self, log_data: dict) -> OperationLog:
        """创建操作日志"""
        log = OperationLog(**log_data)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_operation_logs(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[OperationLog], int]:
        """获取操作日志列表"""
        query = self.db.query(OperationLog)
        
        if tenant_id:
            if isinstance(tenant_id, str):
                tenant_id = UUID(tenant_id)
            query = query.filter(OperationLog.tenant_id == tenant_id)
        
        if user_id:
            if isinstance(user_id, str):
                user_id = UUID(user_id)
            query = query.filter(OperationLog.user_id == user_id)
        
        if resource_type:
            query = query.filter(OperationLog.resource_type == resource_type)
        
        if resource_id:
            if isinstance(resource_id, str):
                resource_id = UUID(resource_id)
            query = query.filter(OperationLog.resource_id == resource_id)
        
        if start_date:
            query = query.filter(OperationLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(OperationLog.created_at <= end_date)
        
        # 按创建时间倒序
        query = query.order_by(desc(OperationLog.created_at))
        
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        return logs, total
    
    def get_operation_log_by_id(self, log_id: str) -> Optional[OperationLog]:
        """根据ID获取操作日志"""
        if isinstance(log_id, str):
            log_id = UUID(log_id)
        
        return self.db.query(OperationLog).filter(
            OperationLog.id == log_id
        ).first()

