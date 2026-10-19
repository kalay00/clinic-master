"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import PlatformAdmin
from .schema import PlatformAdminSchema, PlatformAdminCreateSchema, PlatformAdminUpdateSchema



class PlatformAdminCRUD(CRUDBase[PlatformAdmin, PlatformAdminCreateSchema, PlatformAdminUpdateSchema]):
    """PlatformAdmin 数据层"""

    pass

