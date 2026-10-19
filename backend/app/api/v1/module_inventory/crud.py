"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Supplier, PurchaseOrder, PurchaseOrderItem, InventoryTransaction, InventoryCheck, InventoryCheckItem, ReturnOrder, ReturnOrderItem
from .schema import SupplierSchema, SupplierCreateSchema, SupplierUpdateSchema, PurchaseOrderSchema, PurchaseOrderCreateSchema, PurchaseOrderUpdateSchema, PurchaseOrderItemSchema, PurchaseOrderItemCreateSchema, PurchaseOrderItemUpdateSchema, InventoryTransactionSchema, InventoryTransactionCreateSchema, InventoryTransactionUpdateSchema, InventoryCheckSchema, InventoryCheckCreateSchema, InventoryCheckUpdateSchema, InventoryCheckItemSchema, InventoryCheckItemCreateSchema, InventoryCheckItemUpdateSchema, ReturnOrderSchema, ReturnOrderCreateSchema, ReturnOrderUpdateSchema, ReturnOrderItemSchema, ReturnOrderItemCreateSchema, ReturnOrderItemUpdateSchema



class SupplierCRUD(CRUDBase[Supplier, SupplierCreateSchema, SupplierUpdateSchema]):
    """Supplier 数据层"""

    pass


class PurchaseOrderCRUD(CRUDBase[PurchaseOrder, PurchaseOrderCreateSchema, PurchaseOrderUpdateSchema]):
    """PurchaseOrder 数据层"""

    pass


class PurchaseOrderItemCRUD(CRUDBase[PurchaseOrderItem, PurchaseOrderItemCreateSchema, PurchaseOrderItemUpdateSchema]):
    """PurchaseOrderItem 数据层"""

    pass


class InventoryTransactionCRUD(CRUDBase[InventoryTransaction, InventoryTransactionCreateSchema, InventoryTransactionUpdateSchema]):
    """InventoryTransaction 数据层"""

    pass


class InventoryCheckCRUD(CRUDBase[InventoryCheck, InventoryCheckCreateSchema, InventoryCheckUpdateSchema]):
    """InventoryCheck 数据层"""

    pass


class InventoryCheckItemCRUD(CRUDBase[InventoryCheckItem, InventoryCheckItemCreateSchema, InventoryCheckItemUpdateSchema]):
    """InventoryCheckItem 数据层"""

    pass


class ReturnOrderCRUD(CRUDBase[ReturnOrder, ReturnOrderCreateSchema, ReturnOrderUpdateSchema]):
    """ReturnOrder 数据层"""

    pass


class ReturnOrderItemCRUD(CRUDBase[ReturnOrderItem, ReturnOrderItemCreateSchema, ReturnOrderItemUpdateSchema]):
    """ReturnOrderItem 数据层"""

    pass

