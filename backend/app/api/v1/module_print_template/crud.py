"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import PrintTemplate
from .schema import PrintTemplateSchema, PrintTemplateCreateSchema, PrintTemplateUpdateSchema



class PrintTemplateCRUD(CRUDBase[PrintTemplate, PrintTemplateCreateSchema, PrintTemplateUpdateSchema]):
    """PrintTemplate 数据层"""

    pass

