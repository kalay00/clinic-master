"""
数据库连接管理（对齐 FastapiAdmin: app.core.database，Python 3.12+）
- 异步引擎（asyncpg / aiosqlite）用于新的 module_* 模块与依赖注入
- 同步引擎（psycopg2 / sqlite3）保留给历史消费者（v2 API、后台任务、脚本、测试）
- Base 为统一的 DeclarativeBase，旧模型（Column 风格）与新模型（Mapped 风格）共用同一 metadata
"""
from collections.abc import AsyncGenerator, Generator, Iterator
from datetime import datetime, timezone
from typing import AsyncIterator
from uuid import uuid4

from sqlalchemy import Column, DateTime, create_engine, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def _async_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url


# ── 异步（新架构 module_*）──
_async_connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _async_connect_args["check_same_thread"] = False

async_engine = create_async_engine(
    _async_url(settings.DATABASE_URL),
    echo=False,
    pool_pre_ping=True,
    connect_args=_async_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """统一声明式基类。所有模型共用此 metadata。"""


def _utcnow() -> datetime:
    """返回带时区的当前 UTC 时间，供 async ORM 客户端默认值使用。

    注意：客户端默认值会在 Python 对象内直接写入 created_at/updated_at，
    避免 async 会话下因服务端函数（func.now()）导致的属性过期，从而在
    pydantic model_validate 时触发惰性 SELECT -> MissingGreenlet 错误。
    """
    return datetime.now(timezone.utc)


class BaseModel(Base):
    """
    基础模型类
    所有业务模型都继承此类
    """
    __abstract__ = True

    # 主键
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        comment="主键ID"
    )

    # 租户ID（多租户隔离）
    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="租户ID"
    )

    # 创建时间（客户端默认值，避免 async 下惰性加载）
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=_utcnow,
        nullable=False,
        comment="创建时间"
    )

    # 更新时间（客户端默认值，避免 async 下惰性加载）
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
        comment="更新时间"
    )

    # 删除时间（软删除）
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="删除时间"
    )

    # 创建人ID
    created_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="创建人ID"
    )

    # 更新人ID
    updated_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="更新人ID"
    )

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def soft_delete(self) -> None:
        """软删除"""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """恢复删除"""
        self.deleted_at = None


class async_db_session:
    """后台任务/脚本使用的独立异步会话上下文管理器。"""

    def __init__(self) -> None:
        self._session = AsyncSessionLocal()

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self._session.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """请求级异步数据库会话依赖（新架构使用）。"""
    async with AsyncSessionLocal() as session:
        yield session


# ── 同步（历史消费者：v2 / 任务 / 脚本 / 测试）──
_sync_connect_args: dict = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _sync_connect_args["check_same_thread"] = False

sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=_sync_connect_args,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
    autoflush=False,
)


def get_db() -> Generator:
    """请求级同步数据库会话依赖（历史消费者使用）。"""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── 向后兼容别名（历史消费者 / 脚本仍引用 engine / SessionLocal）──
engine = async_engine
SessionLocal = SyncSessionLocal


# ── 自动建表（对齐 FastapiAdmin: app.core.database.create_tables）──
# 模型有变更（新增表/新增列）时，应用启动即自动创建，无需手工迁移。
# 注意：create_all 只建“不存在的表”，不会 ALTER 已存在表结构。
async def create_tables() -> None:
    """根据 ORM metadata 异步自动创建所有表（模型变更自动建新表）。"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """根据 ORM metadata 异步删除所有表（谨慎使用）。"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
