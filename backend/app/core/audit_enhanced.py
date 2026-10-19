"""
审计日志增强组件：监管操作记录
v2.0新增功能
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logger import logger


class RegulatoryAuditService:
    """监管审计服务"""
    
    @staticmethod
    async def log_regulatory_operation(
        user_id: UUID,
        regulatory_type: str,
        operation_type: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        operation_desc: Optional[str] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None,
        request_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        risk_level: str = "medium",
        db: Optional[Session] = None
    ):
        """
        记录监管相关操作日志
        
        Args:
            user_id: 用户ID
            regulatory_type: 监管类型（medical_insurance/drug_regulatory/health_regulatory）
            operation_type: 操作类型（report/monitor/violation等）
            resource_type: 资源类型
            resource_id: 资源ID
            operation_desc: 操作描述
            before_data: 操作前数据
            after_data: 操作后数据
            request_ip: 请求IP
            user_agent: 用户代理
            risk_level: 风险级别（low/medium/high）
            db: 数据库会话
        """
        try:
            # 构建审计描述
            audit_desc = f"[监管操作] {regulatory_type}/{operation_type}: {operation_desc or '无描述'}"
            
            # 记录到审计日志
            await AuditService.log_audit(
                user_id=user_id,
                audit_type=f"regulatory_{regulatory_type}_{operation_type}",
                resource_type=resource_type,
                audit_desc=audit_desc,
                resource_id=resource_id,
                before_data=before_data,
                after_data=after_data,
                request_ip=request_ip,
                user_agent=user_agent,
                risk_level=risk_level,
                db=db
            )
            
            # 记录到日志文件（用于监管上报）
            logger.warning(
                f"监管审计日志: user={user_id}, regulatory={regulatory_type}, "
                f"operation={operation_type}, resource={resource_type}/{resource_id}, "
                f"risk={risk_level}"
            )
            
        except Exception as e:
            logger.error(f"记录监管操作日志失败: {str(e)}")
    
    @staticmethod
    async def log_data_report(
        user_id: UUID,
        regulatory_type: str,
        report_type: str,
        report_data: Dict[str, Any],
        report_status: str,
        request_ip: Optional[str] = None,
        db: Optional[Session] = None
    ):
        """
        记录数据上报日志
        
        Args:
            user_id: 用户ID
            regulatory_type: 监管类型
            report_type: 上报类型（settlement/quality/infectious等）
            report_data: 上报数据
            report_status: 上报状态（success/failed）
            request_ip: 请求IP
            db: 数据库会话
        """
        try:
            operation_desc = f"数据上报: {report_type}, 状态: {report_status}"
            risk_level = "high" if report_status == "failed" else "medium"
            
            await RegulatoryAuditService.log_regulatory_operation(
                user_id=user_id,
                regulatory_type=regulatory_type,
                operation_type="data_report",
                resource_type="regulatory_report",
                operation_desc=operation_desc,
                after_data=report_data,
                request_ip=request_ip,
                risk_level=risk_level,
                db=db
            )
            
        except Exception as e:
            logger.error(f"记录数据上报日志失败: {str(e)}")
    
    @staticmethod
    async def log_violation_detection(
        user_id: UUID,
        regulatory_type: str,
        violation_type: str,
        violation_data: Dict[str, Any],
        request_ip: Optional[str] = None,
        db: Optional[Session] = None
    ):
        """
        记录违规检测日志
        
        Args:
            user_id: 用户ID
            regulatory_type: 监管类型
            violation_type: 违规类型
            violation_data: 违规数据
            request_ip: 请求IP
            db: 数据库会话
        """
        try:
            operation_desc = f"违规检测: {violation_type}"
            
            await RegulatoryAuditService.log_regulatory_operation(
                user_id=user_id,
                regulatory_type=regulatory_type,
                operation_type="violation_detection",
                resource_type="regulatory_violation",
                operation_desc=operation_desc,
                after_data=violation_data,
                request_ip=request_ip,
                risk_level="high",
                db=db
            )
            
        except Exception as e:
            logger.error(f"记录违规检测日志失败: {str(e)}")


# 导入AuditService（需要从audit.py导入）
from app.core.audit import AuditService

# 创建全局监管审计服务实例
regulatory_audit_service = RegulatoryAuditService()

