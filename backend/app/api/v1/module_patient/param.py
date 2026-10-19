"""
患者查询参数（对齐 FastapiAdmin: 将 QueryParam 拆分到 param.py）
"""
from dataclasses import dataclass
from typing import Optional

from app.core.base_params import PaginationQueryParam


@dataclass
class PatientQueryParam(PaginationQueryParam):
    """患者查询参数"""

    patient_no: Optional[str] = None
    name: Optional[str] = None
    id_card: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    search: Optional[str] = None
