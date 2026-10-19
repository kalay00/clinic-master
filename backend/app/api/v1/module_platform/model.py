"""
平台管理模块 ORM 模型（单一数据源）
"""
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base
from app.core.database import BaseModel


class PlatformAdmin(Base):
    """平台管理员模型"""
    __tablename__ = "platform_admins"
    
    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="主键ID"
    )
    
    # 用户名（唯一）
    username = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="用户名"
    )
    
    # 密码哈希
    password_hash = Column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    
    # 真实姓名
    real_name = Column(
        String(50),
        comment="真实姓名"
    )
    
    # 邮箱
    email = Column(
        String(100),
        comment="邮箱"
    )
    
    # 手机号（加密）
    phone = Column(
        String(20),
        comment="手机号（加密）"
    )
    
    # 状态
    status = Column(
        String(20),
        default="active",
        index=True,
        comment="状态：active/inactive/locked"
    )
    
    # 最后登录时间
    last_login_at = Column(
        DateTime,
        comment="最后登录时间"
    )
    
    # 最后登录IP
    last_login_ip = Column(
        String(50),
        comment="最后登录IP"
    )
    
    # 创建时间
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="创建时间"
    )
    
    # 更新时间
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="更新时间"
    )
    
    # 删除时间（软删除）
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )
    
    __table_args__ = (
        {"comment": "平台管理员表"},
    )


class BackupRecord(BaseModel):
    """备份记录模型"""
    __tablename__ = "backup_records"
    
    backup_id = Column(String(100), nullable=False, unique=True, index=True, comment="备份ID")
    backup_type = Column(String(20), nullable=False, comment="备份类型：full/incremental")
    backup_path = Column(Text, nullable=False, comment="备份文件路径")
    backup_size = Column(Integer, nullable=False, comment="备份文件大小（字节）")
    description = Column(Text, comment="备份描述")
    status = Column(String(20), default="success", comment="备份状态：success/failed/in_progress")
    error_message = Column(Text, comment="错误信息")
    
    # 备份时间（使用created_at字段）
    # 恢复时间
    restored_at = Column(DateTime(timezone=True), comment="恢复时间")
    restored_by = Column(UUID(as_uuid=True), comment="恢复操作人ID")
    
    __table_args__ = (
        {"comment": "备份记录表"},
    )
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<BackupRecord(id={self.id}, backup_id={self.backup_id}, status={self.status})>"
