"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Drug, Inventory, Dispense
from .schema import DrugSchema, DrugCreateSchema, DrugUpdateSchema, InventorySchema, InventoryCreateSchema, InventoryUpdateSchema, DispenseSchema, DispenseCreateSchema, DispenseUpdateSchema



class DrugCRUD(CRUDBase[Drug, DrugCreateSchema, DrugUpdateSchema]):
    """Drug 数据层"""

    pass


class InventoryCRUD(CRUDBase[Inventory, InventoryCreateSchema, InventoryUpdateSchema]):
    """Inventory 数据层"""

    pass


class DispenseCRUD(CRUDBase[Dispense, DispenseCreateSchema, DispenseUpdateSchema]):
    """Dispense 数据层"""

    pass

