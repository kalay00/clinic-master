"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Fee
from .schema import FeeSchema, FeeCreateSchema, FeeUpdateSchema


class FeeCRUD(CRUDBase[Fee, FeeCreateSchema, FeeUpdateSchema]):
    """Fee 数据层"""

    pass
