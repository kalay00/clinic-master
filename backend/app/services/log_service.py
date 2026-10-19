"""
日志服务：操作日志管理
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.log_repository import OperationLogRepository
from app.api.v1.module_log.model import OperationLog
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class LogService:
    """日志服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.log_repo = OperationLogRepository(db)
    
    def create_operation_log(
        self,
        operation_type: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        operation_desc: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> OperationLog:
        """创建操作日志"""
        from uuid import UUID
        
        log_data = {
            "operation_type": operation_type,
            "resource_type": resource_type,
            "status": status,
        }
        
        if resource_id:
            log_data["resource_id"] = UUID(resource_id) if isinstance(resource_id, str) else resource_id
        if tenant_id:
            log_data["tenant_id"] = UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id
        if user_id:
            log_data["user_id"] = UUID(user_id) if isinstance(user_id, str) else user_id
        if operation_desc:
            log_data["operation_desc"] = operation_desc
        if request_data:
            log_data["request_data"] = request_data
        if response_data:
            log_data["response_data"] = response_data
        if ip_address:
            log_data["ip_address"] = ip_address
        if user_agent:
            log_data["user_agent"] = user_agent
        if error_message:
            log_data["error_message"] = error_message
        
        log = self.log_repo.create_operation_log(log_data)
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
        return self.log_repo.get_operation_logs(
            tenant_id, user_id, resource_type, resource_id,
            start_date, end_date, skip, limit
        )
    
    def get_operation_log(self, log_id: str) -> OperationLog:
        """获取操作日志详情"""
        log = self.log_repo.get_operation_log_by_id(log_id)
        if not log:
            raise NotFoundException("操作日志", log_id)
        return log

