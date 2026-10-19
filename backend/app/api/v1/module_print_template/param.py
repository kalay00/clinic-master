"""
查询参数（对齐 FastapiAdmin: param.py，Python 3.12+）
"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Query

from app.core.base_params import PaginationQueryParam, BaseQueryParam


@dataclass
class Print_templateQueryParam(PaginationQueryParam, BaseQueryParam):
    """Print_template 查询参数"""
    name: Optional[str] = Query(None, description="名称")
    type: Optional[str] = Query(None, description="类型")
