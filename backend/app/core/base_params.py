"""
查询参数基类（对齐 FastapiAdmin: app.core.base_params，适配 Python 3.9）
"""
import json
from dataclasses import dataclass
from typing import List, Optional

from fastapi import Query

from app.common.enums import QueueEnum
from app.core.validator import DateTimeStr


@dataclass
class QueryParam:
    """公共基类 —— 自动按 MRO 链式调用所有 __post_init__"""

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        hooks = [_unwrap_query_defaults]
        for base in cls.__mro__:
            fn = base.__dict__.get("__post_init__")
            if callable(fn) and fn is not QueryParam.__post_init__:
                hooks.append(fn)
        hooks.reverse()

        def chained_post_init(self) -> None:
            for hook in hooks:
                hook(self)

        cls.__post_init__ = chained_post_init

    def __post_init__(self) -> None:
        pass


def _unwrap_query_defaults(self) -> None:
    """将 @dataclass 字段中残留的 FastAPI Query(...) 默认值替换为 None"""
    for f in self.__dataclass_fields__:
        raw = getattr(self, f)
        if raw is not None and type(raw).__name__ == "Query":
            setattr(self, f, None)


@dataclass
class PaginationQueryParam(QueryParam):
    """分页 —— 自动继承 page_no / page_size / order_by"""

    page_no: int = Query(default=1, description="当前页码", ge=1)
    page_size: int = Query(default=20, description="每页数量", ge=1, le=100)
    order_by: Optional[str] = Query(
        default=None,
        description="排序字段,格式:[{'field1': 'asc'}, {'field2': 'desc'}]",
    )

    def __post_init__(self) -> None:
        if self.order_by and isinstance(self.order_by, str):
            try:
                self.order_by = json.loads(self.order_by)
            except ValueError:
                self.order_by = [{"created_at": "desc"}]
        else:
            self.order_by = [{"created_at": "desc"}]


@dataclass
class BaseQueryParam(QueryParam):
    """created_at + updated_at —— 子类自动继承"""

    created_at: Optional[List[DateTimeStr]] = Query(None, description="创建时间范围")
    updated_at: Optional[List[DateTimeStr]] = Query(None, description="更新时间范围")

    def __post_init__(self) -> None:
        ct = self.created_at
        if isinstance(ct, list) and len(ct) == 2:
            self.created_at = (QueueEnum.between.value, (ct[0], ct[1]))
        ut = self.updated_at
        if isinstance(ut, list) and len(ut) == 2:
            self.updated_at = (QueueEnum.between.value, (ut[0], ut[1]))


@dataclass
class TenantByQueryParam(QueryParam):
    """tenant_id —— 子类自动继承"""

    tenant_id: object = Query(None, description="租户ID")

    def __post_init__(self) -> None:
        if self.tenant_id is not None:
            self.tenant_id = (QueueEnum.eq.value, self.tenant_id)
