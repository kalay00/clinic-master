"""
查询参数（对齐 FastapiAdmin: param.py，Python 3.12+）
"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Query

from app.core.base_params import PaginationQueryParam, BaseQueryParam


@dataclass
class FeeQueryParam(PaginationQueryParam, BaseQueryParam):
    """Fee 查询参数"""
    fee_type: Optional[str] = Query(None, description="费用类型")
    name: Optional[str] = Query(None, description="费用名称")
    status: Optional[bool] = Query(None, description="是否启用")
