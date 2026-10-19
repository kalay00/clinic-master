"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import ThirdPartyConfig
from .schema import ThirdPartyConfigSchema, ThirdPartyConfigCreateSchema, ThirdPartyConfigUpdateSchema



class ThirdPartyConfigCRUD(CRUDBase[ThirdPartyConfig, ThirdPartyConfigCreateSchema, ThirdPartyConfigUpdateSchema]):
    """ThirdPartyConfig 数据层"""

    pass

