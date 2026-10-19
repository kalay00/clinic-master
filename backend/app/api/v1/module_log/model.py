"""
日志模块 ORM 模型（单一数据源）
"""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.database import BaseModel


class OperationLog(Base):
    """
    操作日志表
    注意：此表不继承BaseModel，因为tenant_id可为NULL（系统级日志）
    """
    __tablename__ = "operation_logs"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="主键ID"
    )
    
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=True,
        index=True,
        comment="租户ID（可为NULL，表示系统级日志）"
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="用户ID"
    )
    
    operation_type = Column(String(50), nullable=False, comment="操作类型：create/update/delete/query")
    resource_type = Column(String(50), nullable=False, comment="资源类型：patient/registration等")
    resource_id = Column(UUID(as_uuid=True), nullable=True, comment="资源ID")
    operation_desc = Column(Text, comment="操作描述")
    request_data = Column(JSONB, comment="请求数据")
    response_data = Column(JSONB, comment="响应数据")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    status = Column(String(20), comment="状态：success/failed")
    error_message = Column(Text, comment="错误信息")
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        comment="创建时间"
    )
    
    # 关系
    tenant = relationship("Tenant", backref="operation_logs")
    user = relationship("User", backref="operation_logs")
    
    __table_args__ = (
        {"comment": "操作日志表"},
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<OperationLog(id={self.id}, operation_type={self.operation_type})>"


class AuditLog(BaseModel):
    """审计日志模型（敏感操作，v2.0增强）"""
    __tablename__ = "audit_logs"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment="操作用户ID")
    audit_type = Column(String(50), nullable=False, index=True, comment="审计类型：login/logout/delete/export/regulatory等")
    resource_type = Column(String(50), nullable=False, index=True, comment="资源类型")
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True, comment="资源ID")
    audit_desc = Column(Text, nullable=False, comment="审计描述")
    before_data = Column(JSONB, comment="操作前数据")
    after_data = Column(JSONB, comment="操作后数据")
    request_ip = Column(String(50), index=True, comment="请求IP")
    user_agent = Column(Text, comment="用户代理")
    risk_level = Column(String(20), default="low", index=True, comment="风险级别：low/medium/high")
    
    # v2.0新增：监管相关字段
    regulatory_type = Column(String(50), index=True, comment="监管类型：medical_insurance/drug_regulatory/health_regulatory")
    regulatory_operation = Column(String(50), comment="监管操作类型：data_report/violation_detection等")
    regulatory_status = Column(String(20), comment="监管操作状态：success/failed/pending")
    
    __table_args__ = (
        {"comment": "审计日志表（v2.0增强：支持监管操作记录）"},
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<AuditLog(id={self.id}, audit_type={self.audit_type}, risk_level={self.risk_level})>"
