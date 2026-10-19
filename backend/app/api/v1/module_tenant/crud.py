"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Tenant
from .schema import TenantSchema, TenantCreateSchema, TenantUpdateSchema



class TenantCRUD(CRUDBase[Tenant, TenantCreateSchema, TenantUpdateSchema]):
    """Tenant 数据层"""

    pass

