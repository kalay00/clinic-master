"""
数据权限过滤（对齐 FastapiAdmin: app.core.permission 的精简版）
本系统以 tenant_id 租户隔离为核心，数据范围（本人/部门）为可选增强。
"""
from typing import Any, Optional

from sqlalchemy.sql.elements import ColumnElement

from app.common.enums import PermissionFilterStrategy
from app.core.base_schema import AuthSchema


class Permission:
    """为业务模型提供数据权限过滤功能（策略模式）"""

    def __init__(self, model: Any, auth: AuthSchema) -> None:
        self.model = model
        self.auth = auth
        self.conditions: list[ColumnElement] = []

    async def filter_query(self, query: Any) -> Any:
        condition = await self.__permission_condition()
        return query.where(condition) if condition is not None else query

    async def __permission_condition(self) -> Optional[ColumnElement]:
        if not self.auth.user:
            return None
        if not self.auth.check_data_scope:
            return None
        if getattr(self.auth.user, "is_superuser", False):
            return None

        strategy = getattr(
            self.model, "__permission_strategy__", PermissionFilterStrategy.DATA_SCOPE
        )
        if strategy == PermissionFilterStrategy.OWN:
            return self.__filter_by_own()
        return self.__filter_by_tenant()

    def __filter_by_own(self) -> Optional[ColumnElement]:
        created_by = getattr(self.model, "created_by", None)
        if created_by is not None and self.auth.user is not None:
            return created_by == self.auth.user.id
        return None

    def __filter_by_tenant(self) -> Optional[ColumnElement]:
        tenant_id_attr = getattr(self.model, "tenant_id", None)
        if tenant_id_attr is not None and self.auth.tenant_id is not None:
            return tenant_id_attr == self.auth.tenant_id
        return None
