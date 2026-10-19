"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import OperationLog
from .schema import OperationLogSchema, OperationLogCreateSchema, OperationLogUpdateSchema



class OperationLogCRUD(CRUDBase[OperationLog, OperationLogCreateSchema, OperationLogUpdateSchema]):
    """OperationLog 数据层"""

    pass

