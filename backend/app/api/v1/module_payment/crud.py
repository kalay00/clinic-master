"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Bill, Payment
from .schema import BillSchema, BillCreateSchema, BillUpdateSchema, PaymentSchema, PaymentCreateSchema, PaymentUpdateSchema



class BillCRUD(CRUDBase[Bill, BillCreateSchema, BillUpdateSchema]):
    """Bill 数据层"""

    pass


class PaymentCRUD(CRUDBase[Payment, PaymentCreateSchema, PaymentUpdateSchema]):
    """Payment 数据层"""

    pass

