"""
Schema 基类（对齐 FastapiAdmin: app.core.base_schema，Python 3.12+ / PEP 695）
- BaseSchema: 通用输出模型
- AuthSchema: 认证上下文（注入 Service / CRUD）
- PageResultSchema[T]: 分页结果
"""
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.validator import DateTimeStr


class BaseSchema(BaseModel):
    """通用输出模型，包含基础字段和审计字段"""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[Any] = Field(default=None, description="主键ID")
    tenant_id: Optional[Any] = Field(default=None, description="租户ID")
    created_at: Optional[DateTimeStr] = Field(default=None, description="创建时间")
    updated_at: Optional[DateTimeStr] = Field(default=None, description="更新时间")
    deleted_at: Optional[DateTimeStr] = Field(default=None, description="删除时间")


class AuthSchema(BaseModel):
    """
    权限认证模型。

    ``user`` 运行时为 Any（避免与 SQLAlchemy 懒加载/循环依赖冲突），
    业务方通过 ``auth.get_user()`` 获得类型提示。
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    user: Any = Field(default=None, description="用户信息（ORM 对象）", exclude=True)
    check_data_scope: bool = Field(default=True, description="是否检查数据权限")
    db: Optional[AsyncSession] = Field(default=None, description="数据库会话", exclude=True)
    tenant_id: Optional[Any] = Field(default=None, description="租户ID")

    def get_user(self) -> Any:
        return self.user


class PageResultSchema[T](BaseModel):
    """分页查询结果模型"""

    model_config = ConfigDict(from_attributes=True)

    page_no: Optional[int] = Field(default=None, ge=1, description="页码，默认为1")
    page_size: Optional[int] = Field(default=None, ge=1, description="页面大小，默认为10")
    total: int = Field(default=0, ge=0, description="总记录数")
    has_next: Optional[bool] = Field(default=False, description="是否有下一页")
    items: list[T] = Field(default_factory=list, description="分页后的数据列表")
