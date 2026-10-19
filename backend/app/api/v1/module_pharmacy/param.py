"""
查询参数（对齐 FastapiAdmin: param.py，Python 3.12+）
"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Query

from app.core.base_params import PaginationQueryParam, BaseQueryParam


@dataclass
class PharmacyQueryParam(PaginationQueryParam, BaseQueryParam):
    """Pharmacy 查询参数"""
    name: Optional[str] = Query(None, description="名称")
    status: Optional[str] = Query(None, description="状态")
    category: Optional[str] = Query(None, description="药品分类")
