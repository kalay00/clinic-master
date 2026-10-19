"""
ORM 模型基类（对齐 FastapiAdmin: app.core.base_model，适配 Python 3.9）
适配 outpatient 现状：UUID 主键、tenant_id(UUID) 租户隔离、deleted_at 软删除、
created_by/updated_by(UUID) 审计字段。
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MappedBase(AsyncAttrs, Base):
    """声明式基类（异步）"""

    __abstract__ = True


class ModelMixin(MappedBase):
    """通用字段 Mixin：主键 / 租户 / 时间 / 软删除 / 审计"""

    __abstract__ = True

    id: Mapped[object] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="主键ID",
    )
    tenant_id: Mapped[object] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
        comment="租户ID",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="创建时间",
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="更新时间",
        index=True,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True,
        comment="删除时间（软删除）",
        index=True,
    )
    created_by: Mapped[Optional[object]] = mapped_column(
        Uuid(as_uuid=True),
        default=None,
        nullable=True,
        index=True,
        comment="创建人ID",
    )
    updated_by: Mapped[Optional[object]] = mapped_column(
        Uuid(as_uuid=True),
        default=None,
        nullable=True,
        index=True,
        comment="更新人ID",
    )


class TenantMixin(MappedBase):
    """仅租户隔离字段的 Mixin（部分关联表使用）"""

    __abstract__ = True

    tenant_id: Mapped[object] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
        comment="租户ID",
    )
