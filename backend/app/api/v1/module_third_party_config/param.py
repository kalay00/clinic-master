"""
查询参数（对齐 FastapiAdmin: param.py，Python 3.12+）
"""
from dataclasses import dataclass
from typing import Optional

from fastapi import Query

from app.core.base_params import PaginationQueryParam, BaseQueryParam


@dataclass
class Third_party_configQueryParam(PaginationQueryParam, BaseQueryParam):
    """Third_party_config 查询参数"""
    pass
