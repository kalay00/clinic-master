"""
进销存数据仓库
"""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from app.api.v1.module_inventory.model import (
    Supplier, PurchaseOrder, PurchaseOrderItem,
    InventoryTransaction, InventoryCheck, InventoryCheckItem,
    ReturnOrder, ReturnOrderItem
)
from app.api.v1.module_pharmacy.model import Drug, Inventory
from app.core.exceptions import NotFoundException, BusinessException


class SupplierRepository:
    """供应商数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_supplier(self, supplier_data: dict, tenant_id: str) -> Supplier:
        """创建供应商"""
        supplier = Supplier(
            tenant_id=tenant_id,
            name=supplier_data["name"],
            code=supplier_data["code"],
            contact_name=supplier_data.get("contact_name"),
            contact_phone=supplier_data.get("contact_phone"),
            contact_email=supplier_data.get("contact_email"),
            address=supplier_data.get("address"),
            category=supplier_data.get("category"),
            status=supplier_data.get("status", "active"),
            remark=supplier_data.get("remark"),
        )
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier
    
    def get_supplier_by_id(self, supplier_id: str, tenant_id: str) -> Optional[Supplier]:
        """根据ID获取供应商"""
        return self.db.query(Supplier).filter(
            and_(
                Supplier.id == supplier_id,
                Supplier.tenant_id == tenant_id,
                Supplier.deleted_at.is_(None)
            )
        ).first()
    
    def get_suppliers(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[Supplier], int]:
        """获取供应商列表"""
        query = self.db.query(Supplier).filter(
            and_(
                Supplier.tenant_id == tenant_id,
                Supplier.deleted_at.is_(None)
            )
        )
        
        if search:
            query = query.filter(
                (Supplier.name.ilike(f"%{search}%")) |
                (Supplier.code.ilike(f"%{search}%")) |
                (Supplier.contact_name.ilike(f"%{search}%"))
            )
        
        if status:
            query = query.filter(Supplier.status == status)
        
        total = query.count()
        suppliers = query.order_by(Supplier.created_at.desc()).offset(skip).limit(limit).all()
        
        return suppliers, total
    
    def update_supplier(self, supplier_id: str, tenant_id: str, supplier_data: dict) -> Supplier:
        """更新供应商"""
        supplier = self.get_supplier_by_id(supplier_id, tenant_id)
        if not supplier:
            raise NotFoundException("供应商", supplier_id)
        
        for key, value in supplier_data.items():
            setattr(supplier, key, value)
        
        self.db.commit()
        self.db.refresh(supplier)
        return supplier
    
    def delete_supplier(self, supplier_id: str, tenant_id: str) -> bool:
        """删除供应商（软删除）"""
        supplier = self.get_supplier_by_id(supplier_id, tenant_id)
        if not supplier:
            raise NotFoundException("供应商", supplier_id)
        
        supplier.soft_delete()
        self.db.commit()
        return True


class PurchaseOrderRepository:
    """采购单数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_order_no(self, tenant_id: str) -> str:
        """生成采购单号"""
        today = datetime.now().strftime("%Y%m%d")
        count = self.db.query(PurchaseOrder).filter(
            and_(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.order_no.like(f"PO{today}%")
            )
        ).count()
        return f"PO{today}{str(count + 1).zfill(4)}"
    
    def create_purchase_order(self, order_data: dict, tenant_id: str) -> PurchaseOrder:
        """创建采购单"""
        order_no = order_data.get("order_no") or self.generate_order_no(tenant_id)
        
        order = PurchaseOrder(
            tenant_id=tenant_id,
            order_no=order_no,
            supplier_id=order_data["supplier_id"],
            order_date=order_data.get("order_date") or date.today(),
            expected_date=order_data.get("expected_date"),
            total_amount=order_data.get("total_amount", 0),
            status="draft",
            remark=order_data.get("remark"),
        )
        self.db.add(order)
        self.db.flush()
        
        # 创建采购明细
        if "items" in order_data:
            for item_data in order_data["items"]:
                item = PurchaseOrderItem(
                    tenant_id=tenant_id,
                    purchase_order_id=order.id,
                    drug_id=item_data["drug_id"],
                    quantity=item_data["quantity"],
                    unit_price=item_data.get("unit_price", 0),
                    total_amount=item_data.get("total_amount", 0) or (item_data["quantity"] * item_data.get("unit_price", 0)),
                    batch_no=item_data.get("batch_no"),
                    expiry_date=item_data.get("expiry_date"),
                )
                self.db.add(item)
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def get_purchase_order_by_id(self, order_id: str, tenant_id: str) -> Optional[PurchaseOrder]:
        """根据ID获取采购单"""
        return self.db.query(PurchaseOrder).filter(
            and_(
                PurchaseOrder.id == order_id,
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.deleted_at.is_(None)
            )
        ).first()
    
    def get_purchase_orders(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        supplier_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> tuple[List[PurchaseOrder], int]:
        """获取采购单列表"""
        query = self.db.query(PurchaseOrder).filter(
            and_(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.deleted_at.is_(None)
            )
        )
        
        if search:
            query = query.filter(PurchaseOrder.order_no.ilike(f"%{search}%"))
        
        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)
        
        if status:
            query = query.filter(PurchaseOrder.status == status)
        
        if start_date:
            query = query.filter(PurchaseOrder.order_date >= start_date)
        
        if end_date:
            query = query.filter(PurchaseOrder.order_date <= end_date)
        
        total = query.count()
        orders = query.order_by(desc(PurchaseOrder.created_at)).offset(skip).limit(limit).all()
        
        return orders, total
    
    def update_purchase_order(self, order_id: str, tenant_id: str, order_data: dict) -> PurchaseOrder:
        """更新采购单"""
        order = self.get_purchase_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("采购单", order_id)
        
        if order.status != "draft":
            raise BusinessException("只有草稿状态的采购单可以修改", code=400)
        
        # 更新基本信息
        for key in ["expected_date", "remark"]:
            if key in order_data:
                setattr(order, key, order_data[key])
        
        # 更新明细
        if "items" in order_data:
            # 删除旧明细
            self.db.query(PurchaseOrderItem).filter(
                PurchaseOrderItem.purchase_order_id == order_id
            ).delete()
            
            # 添加新明细
            total_amount = 0
            for item_data in order_data["items"]:
                item = PurchaseOrderItem(
                    tenant_id=tenant_id,
                    purchase_order_id=order.id,
                    drug_id=item_data["drug_id"],
                    quantity=item_data["quantity"],
                    unit_price=item_data.get("unit_price", 0),
                    total_amount=item_data.get("total_amount", 0) or (item_data["quantity"] * item_data.get("unit_price", 0)),
                    batch_no=item_data.get("batch_no"),
                    expiry_date=item_data.get("expiry_date"),
                )
                self.db.add(item)
                total_amount += item.total_amount
            
            order.total_amount = total_amount
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def approve_purchase_order(self, order_id: str, tenant_id: str, approver_id: str) -> PurchaseOrder:
        """审核采购单"""
        order = self.get_purchase_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("采购单", order_id)
        
        if order.status != "draft":
            raise BusinessException("只有草稿状态的采购单可以审核", code=400)
        
        order.status = "approved"
        order.approved_by = approver_id
        order.approved_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def receive_purchase_order(self, order_id: str, tenant_id: str, receiver_id: str) -> PurchaseOrder:
        """入库采购单"""
        order = self.get_purchase_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("采购单", order_id)
        
        if order.status != "approved":
            raise BusinessException("只有已审核的采购单可以入库", code=400)
        
        order.status = "received"
        order.received_by = receiver_id
        order.received_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def delete_purchase_order(self, order_id: str, tenant_id: str) -> bool:
        """删除采购单（软删除）"""
        order = self.get_purchase_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("采购单", order_id)
        
        if order.status not in ["draft", "cancelled"]:
            raise BusinessException("只有草稿或已取消的采购单可以删除", code=400)
        
        order.soft_delete()
        self.db.commit()
        return True


class InventoryTransactionRepository:
    """库存流水数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_transaction(self, transaction_data: dict, tenant_id: str) -> InventoryTransaction:
        """创建库存流水"""
        transaction = InventoryTransaction(
            tenant_id=tenant_id,
            drug_id=transaction_data["drug_id"],
            transaction_type=transaction_data["transaction_type"],
            reference_id=transaction_data.get("reference_id"),
            reference_type=transaction_data.get("reference_type"),
            quantity=transaction_data["quantity"],
            unit_price=transaction_data.get("unit_price", 0),
            total_amount=transaction_data.get("total_amount", 0),
            before_quantity=transaction_data.get("before_quantity", 0),
            after_quantity=transaction_data.get("after_quantity", 0),
            operator_id=transaction_data.get("operator_id"),
            transaction_date=transaction_data.get("transaction_date") or datetime.now(),
            remark=transaction_data.get("remark"),
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def get_transactions(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        drug_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[InventoryTransaction], int]:
        """获取库存流水列表"""
        query = self.db.query(InventoryTransaction).filter(
            and_(
                InventoryTransaction.tenant_id == tenant_id,
                InventoryTransaction.deleted_at.is_(None)
            )
        )
        
        if drug_id:
            query = query.filter(InventoryTransaction.drug_id == drug_id)
        
        if transaction_type:
            query = query.filter(InventoryTransaction.transaction_type == transaction_type)
        
        if start_date:
            query = query.filter(InventoryTransaction.transaction_date >= start_date)
        
        if end_date:
            query = query.filter(InventoryTransaction.transaction_date <= end_date)
        
        total = query.count()
        transactions = query.order_by(desc(InventoryTransaction.transaction_date)).offset(skip).limit(limit).all()
        
        return transactions, total


class InventoryCheckRepository:
    """库存盘点数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_check_no(self, tenant_id: str) -> str:
        """生成盘点单号"""
        today = datetime.now().strftime("%Y%m%d")
        count = self.db.query(InventoryCheck).filter(
            and_(
                InventoryCheck.tenant_id == tenant_id,
                InventoryCheck.check_no.like(f"CK{today}%")
            )
        ).count()
        return f"CK{today}{str(count + 1).zfill(4)}"
    
    def create_inventory_check(self, check_data: dict, tenant_id: str) -> InventoryCheck:
        """创建盘点单"""
        check_no = check_data.get("check_no") or self.generate_check_no(tenant_id)
        
        check = InventoryCheck(
            tenant_id=tenant_id,
            check_no=check_no,
            check_date=check_data.get("check_date") or date.today(),
            status="draft",
            operator_id=check_data.get("operator_id"),
            remark=check_data.get("remark"),
        )
        self.db.add(check)
        self.db.flush()
        
        # 创建盘点明细
        if "items" in check_data:
            for item_data in check_data["items"]:
                difference = item_data["actual_quantity"] - item_data["book_quantity"]
                item = InventoryCheckItem(
                    tenant_id=tenant_id,
                    inventory_check_id=check.id,
                    drug_id=item_data["drug_id"],
                    book_quantity=item_data["book_quantity"],
                    actual_quantity=item_data["actual_quantity"],
                    difference=difference,
                    unit_price=item_data.get("unit_price", 0),
                    difference_amount=difference * item_data.get("unit_price", 0),
                    remark=item_data.get("remark"),
                )
                self.db.add(item)
        
        self.db.commit()
        self.db.refresh(check)
        return check
    
    def get_inventory_check_by_id(self, check_id: str, tenant_id: str) -> Optional[InventoryCheck]:
        """根据ID获取盘点单"""
        return self.db.query(InventoryCheck).filter(
            and_(
                InventoryCheck.id == check_id,
                InventoryCheck.tenant_id == tenant_id,
                InventoryCheck.deleted_at.is_(None)
            )
        ).first()
    
    def get_inventory_checks(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> tuple[List[InventoryCheck], int]:
        """获取盘点单列表"""
        query = self.db.query(InventoryCheck).filter(
            and_(
                InventoryCheck.tenant_id == tenant_id,
                InventoryCheck.deleted_at.is_(None)
            )
        )
        
        if status:
            query = query.filter(InventoryCheck.status == status)
        
        if start_date:
            query = query.filter(InventoryCheck.check_date >= start_date)
        
        if end_date:
            query = query.filter(InventoryCheck.check_date <= end_date)
        
        total = query.count()
        checks = query.order_by(desc(InventoryCheck.created_at)).offset(skip).limit(limit).all()
        
        return checks, total
    
    def complete_inventory_check(self, check_id: str, tenant_id: str) -> InventoryCheck:
        """完成盘点"""
        check = self.get_inventory_check_by_id(check_id, tenant_id)
        if not check:
            raise NotFoundException("盘点单", check_id)
        
        if check.status != "draft":
            raise BusinessException("只有草稿状态的盘点单可以完成", code=400)
        
        check.status = "completed"
        
        self.db.commit()
        self.db.refresh(check)
        return check
    
    def delete_inventory_check(self, check_id: str, tenant_id: str) -> bool:
        """删除盘点单（软删除）"""
        check = self.get_inventory_check_by_id(check_id, tenant_id)
        if not check:
            raise NotFoundException("盘点单", check_id)
        
        if check.status != "draft":
            raise BusinessException("只有草稿状态的盘点单可以删除", code=400)
        
        check.soft_delete()
        self.db.commit()
        return True


class ReturnOrderRepository:
    """退货单数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_return_no(self, tenant_id: str) -> str:
        """生成退货单号"""
        from uuid import UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
            
        today = datetime.now().strftime("%Y%m%d")
        count = self.db.query(ReturnOrder).filter(
            and_(
                ReturnOrder.tenant_id == tenant_id_uuid,
                ReturnOrder.return_no.like(f"RO{today}%")
            )
        ).count()
        return f"RO{today}{str(count + 1).zfill(4)}"
    
    def create_return_order(self, order_data: dict, tenant_id: str) -> ReturnOrder:
        """创建退货单"""
        from uuid import UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
            
        return_no = order_data.get("return_no") or self.generate_return_no(tenant_id)
        
        order = ReturnOrder(
            tenant_id=tenant_id_uuid,
            return_no=return_no,
            purchase_order_id=order_data["purchase_order_id"],
            return_date=order_data.get("return_date") or date.today(),
            total_amount=order_data.get("total_amount", 0),
            status="draft",
            remark=order_data.get("remark"),
        )
        self.db.add(order)
        self.db.flush()
        
        # 创建退货明细
        if "items" in order_data:
            for item_data in order_data["items"]:
                item = ReturnOrderItem(
                    tenant_id=tenant_id_uuid,
                    return_order_id=order.id,
                    purchase_order_item_id=item_data["purchase_order_item_id"],
                    drug_id=item_data["drug_id"],
                    quantity=item_data["quantity"],
                    unit_price=item_data.get("unit_price", 0),
                    total_amount=item_data.get("total_amount", 0) or (item_data["quantity"] * item_data.get("unit_price", 0)),
                    batch_no=item_data.get("batch_no"),
                    expiry_date=item_data.get("expiry_date"),
                )
                self.db.add(item)
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def get_return_order_by_id(self, order_id: str, tenant_id: str) -> Optional[ReturnOrder]:
        """根据ID获取退货单"""
        from uuid import UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
            
        if isinstance(order_id, str):
            try:
                order_id_uuid = UUID(order_id)
            except (ValueError, TypeError):
                order_id_uuid = order_id
        else:
            order_id_uuid = order_id
            
        return self.db.query(ReturnOrder).filter(
            and_(
                ReturnOrder.id == order_id_uuid,
                ReturnOrder.tenant_id == tenant_id_uuid,
                ReturnOrder.deleted_at.is_(None)
            )
        ).first()
    
    def get_return_orders(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        purchase_order_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> tuple[List[ReturnOrder], int]:
        """获取退货单列表"""
        from uuid import UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
            
        query = self.db.query(ReturnOrder).filter(
            and_(
                ReturnOrder.tenant_id == tenant_id_uuid,
                ReturnOrder.deleted_at.is_(None)
            )
        )
        
        if search:
            query = query.filter(ReturnOrder.return_no.ilike(f"%{search}%"))
        
        if purchase_order_id:
            if isinstance(purchase_order_id, str):
                try:
                    purchase_order_id_uuid = UUID(purchase_order_id)
                except (ValueError, TypeError):
                    purchase_order_id_uuid = purchase_order_id
            else:
                purchase_order_id_uuid = purchase_order_id
            query = query.filter(ReturnOrder.purchase_order_id == purchase_order_id_uuid)
        
        if status:
            query = query.filter(ReturnOrder.status == status)
        
        if start_date:
            query = query.filter(ReturnOrder.return_date >= start_date)
        
        if end_date:
            query = query.filter(ReturnOrder.return_date <= end_date)
        
        total = query.count()
        orders = query.order_by(desc(ReturnOrder.created_at)).offset(skip).limit(limit).all()
        
        return orders, total
    
    def update_return_order(self, order_id: str, tenant_id: str, order_data: dict) -> ReturnOrder:
        """更新退货单"""
        order = self.get_return_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("退货单", order_id)
        
        if order.status != "draft":
            raise BusinessException("只有草稿状态的退货单可以更新", code=400)
        
        # 更新基本信息
        if "return_date" in order_data:
            order.return_date = order_data["return_date"]
        if "remark" in order_data:
            order.remark = order_data["remark"]
        
        # 更新明细
        if "items" in order_data:
            # 删除旧明细
            for item in order.items:
                self.db.delete(item)
            
            # 创建新明细
            from uuid import UUID
            if isinstance(tenant_id, str):
                try:
                    tenant_id_uuid = UUID(tenant_id)
                except (ValueError, TypeError):
                    tenant_id_uuid = tenant_id
            else:
                tenant_id_uuid = tenant_id
                
            total_amount = 0
            for item_data in order_data["items"]:
                item = ReturnOrderItem(
                    tenant_id=tenant_id_uuid,
                    return_order_id=order.id,
                    purchase_order_item_id=item_data["purchase_order_item_id"],
                    drug_id=item_data["drug_id"],
                    quantity=item_data["quantity"],
                    unit_price=item_data.get("unit_price", 0),
                    total_amount=item_data.get("total_amount", 0) or (item_data["quantity"] * item_data.get("unit_price", 0)),
                    batch_no=item_data.get("batch_no"),
                    expiry_date=item_data.get("expiry_date"),
                )
                self.db.add(item)
                total_amount += item.total_amount
            
            order.total_amount = total_amount
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def approve_return_order(self, order_id: str, tenant_id: str, approver_id: str) -> ReturnOrder:
        """审核退货单"""
        from uuid import UUID
        if isinstance(approver_id, str):
            try:
                approver_id_uuid = UUID(approver_id)
            except (ValueError, TypeError):
                approver_id_uuid = approver_id
        else:
            approver_id_uuid = approver_id
            
        order = self.get_return_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("退货单", order_id)
        
        if order.status != "draft":
            raise BusinessException("只有草稿状态的退货单可以审核", code=400)
        
        order.status = "approved"
        order.approved_by = approver_id_uuid
        order.approved_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def complete_return_order(self, order_id: str, tenant_id: str, completer_id: str) -> ReturnOrder:
        """完成退货单"""
        from uuid import UUID
        if isinstance(completer_id, str):
            try:
                completer_id_uuid = UUID(completer_id)
            except (ValueError, TypeError):
                completer_id_uuid = completer_id
        else:
            completer_id_uuid = completer_id
            
        order = self.get_return_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("退货单", order_id)
        
        if order.status != "approved":
            raise BusinessException("只有已审核的退货单可以完成", code=400)
        
        order.status = "completed"
        order.completed_by = completer_id_uuid
        order.completed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def cancel_return_order(self, order_id: str, tenant_id: str) -> ReturnOrder:
        """取消退货单"""
        order = self.get_return_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("退货单", order_id)
        
        if order.status not in ["draft", "approved"]:
            raise BusinessException("只有草稿或已审核状态的退货单可以取消", code=400)
        
        order.status = "cancelled"
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def delete_return_order(self, order_id: str, tenant_id: str) -> bool:
        """删除退货单（软删除）"""
        order = self.get_return_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("退货单", order_id)
        
        if order.status not in ["draft", "cancelled"]:
            raise BusinessException("只有草稿或已取消的退货单可以删除", code=400)
        
        order.soft_delete()
        self.db.commit()
        return True

