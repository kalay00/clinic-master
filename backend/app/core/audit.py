"""
日志审计组件：操作日志和审计日志
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import BaseModel
from app.core.logger import logger


class OperationLog(BaseModel):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, comment="操作用户ID")
    operation_type = Column(String(50), nullable=False, comment="操作类型：create/update/delete/query")
    resource_type = Column(String(50), nullable=False, comment="资源类型：user/patient/registration等")
    resource_id = Column(String(50), comment="资源ID")
    operation_desc = Column(Text, comment="操作描述")
    request_method = Column(String(10), comment="HTTP方法")
    request_path = Column(String(255), comment="请求路径")
    request_ip = Column(String(50), comment="请求IP")
    request_params = Column(JSON, comment="请求参数")
    response_status = Column(String(10), comment="响应状态码")
    response_data = Column(JSON, comment="响应数据")
    duration_ms = Column(String(20), comment="耗时（毫秒）")


class AuditLog(BaseModel):
    """审计日志模型（敏感操作）"""
    __tablename__ = "audit_logs"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, comment="操作用户ID")
    audit_type = Column(String(50), nullable=False, comment="审计类型：login/logout/delete/export等")
    resource_type = Column(String(50), nullable=False, comment="资源类型")
    resource_id = Column(String(50), comment="资源ID")
    audit_desc = Column(Text, nullable=False, comment="审计描述")
    before_data = Column(JSON, comment="操作前数据")
    after_data = Column(JSON, comment="操作后数据")
    request_ip = Column(String(50), comment="请求IP")
    user_agent = Column(String(255), comment="用户代理")
    risk_level = Column(String(20), default="low", comment="风险级别：low/medium/high")


class AuditService:
    """审计服务类"""
    
    @staticmethod
    async def log_operation(
        user_id: str,
        operation_type: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        operation_desc: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        request_ip: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None,
        response_status: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[str] = None,
        db=None
    ):
        """
        记录操作日志
        
        Args:
            user_id: 用户ID
            operation_type: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            operation_desc: 操作描述
            request_method: HTTP方法
            request_path: 请求路径
            request_ip: 请求IP
            request_params: 请求参数
            response_status: 响应状态码
            response_data: 响应数据
            duration_ms: 耗时
            db: 数据库会话
        """
        try:
            # TODO: 实现数据库保存逻辑
            # 这里先记录到日志文件
            logger.info(
                f"操作日志: user={user_id}, type={operation_type}, "
                f"resource={resource_type}/{resource_id}, desc={operation_desc}"
            )
        except Exception as e:
            logger.error(f"记录操作日志失败: {str(e)}")
    
    @staticmethod
    async def log_audit(
        user_id: str,
        audit_type: str,
        resource_type: str,
        audit_desc: str,
        resource_id: Optional[str] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        request_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        risk_level: str = "low",
        db=None
    ):
        """
        记录审计日志
        
        Args:
            user_id: 用户ID
            audit_type: 审计类型
            resource_type: 资源类型
            audit_desc: 审计描述
            resource_id: 资源ID
            before_data: 操作前数据
            after_data: 操作后数据
            request_ip: 请求IP
            user_agent: 用户代理
            risk_level: 风险级别
            db: 数据库会话
        """
        try:
            # TODO: 实现数据库保存逻辑
            # 这里先记录到日志文件
            logger.warning(
                f"审计日志: user={user_id}, type={audit_type}, "
                f"resource={resource_type}/{resource_id}, desc={audit_desc}, "
                f"risk={risk_level}"
            )
        except Exception as e:
            logger.error(f"记录审计日志失败: {str(e)}")


# 创建全局审计服务实例
audit_service = AuditService()

