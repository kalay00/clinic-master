"""
查询参数（对齐 FastapiAdmin: param.py，Python 3.12+）
"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Query

from app.core.base_params import PaginationQueryParam, BaseQueryParam


@dataclass
class RoleQueryParam(PaginationQueryParam, BaseQueryParam):
    """Role 查询参数"""
    name: Optional[str] = Query(None, description="名称")
    code: Optional[str] = Query(None, description="编码")
