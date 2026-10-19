"""
进销存服务：供应商管理、采购管理、库存流水、库存盘点
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.repositories.inventory_repository import (
    SupplierRepository,
    PurchaseOrderRepository,
    InventoryTransactionRepository,
    InventoryCheckRepository,
    ReturnOrderRepository
)
from app.repositories.pharmacy_repository import InventoryRepository
from app.api.v1.module_pharmacy.model import Inventory
from app.api.v1.module_inventory.model import Supplier
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class InventoryService:
    """进销存服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.supplier_repo = SupplierRepository(db)
        self.purchase_repo = PurchaseOrderRepository(db)
        self.transaction_repo = InventoryTransactionRepository(db)
        self.check_repo = InventoryCheckRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.return_repo = ReturnOrderRepository(db)
    
    # 供应商管理
    def create_supplier(self, supplier_data: Dict[str, Any], tenant_id: str, creator_id: str) -> Supplier:
        """创建供应商"""
        supplier = self.supplier_repo.create_supplier(supplier_data, tenant_id)
        supplier.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建供应商: {supplier.id} by {creator_id}")
        return supplier
    
    def get_supplier(self, supplier_id: str, tenant_id: str):
        """获取供应商详情"""
        supplier = self.supplier_repo.get_supplier_by_id(supplier_id, tenant_id)
        if not supplier:
            raise NotFoundException("供应商", supplier_id)
        return supplier
    
    def list_suppliers(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List, int]:
        """获取供应商列表"""
        return self.supplier_repo.get_suppliers(tenant_id, skip, limit, search, status)
    
    def update_supplier(
        self,
        supplier_id: str,
        tenant_id: str,
        supplier_data: Dict[str, Any],
        updater_id: str
    ):
        """更新供应商"""
        supplier = self.supplier_repo.update_supplier(supplier_id, tenant_id, supplier_data)
        supplier.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新供应商: {supplier_id} by {updater_id}")
        return supplier
    
    def delete_supplier(self, supplier_id: str, tenant_id: str, deleter_id: str) -> bool:
        """删除供应商"""
        result = self.supplier_repo.delete_supplier(supplier_id, tenant_id)
        logger.info(f"删除供应商: {supplier_id} by {deleter_id}")
        return result
    
    # 采购管理
    def create_purchase_order(
        self,
        order_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ):
        """创建采购单"""
        # 计算总金额
        if "items" in order_data:
            total_amount = sum(
                item.get("total_amount", 0) or (item["quantity"] * item.get("unit_price", 0))
                for item in order_data["items"]
            )
            order_data["total_amount"] = total_amount
        
        order = self.purchase_repo.create_purchase_order(order_data, tenant_id)
        order.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建采购单: {order.id} by {creator_id}")
        return order
    
    def get_purchase_order(self, order_id: str, tenant_id: str):
        """获取采购单详情"""
        order = self.purchase_repo.get_purchase_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("采购单", order_id)
        return order
    
    def list_purchase_orders(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        supplier_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> tuple[List, int]:
        """获取采购单列表"""
        return self.purchase_repo.get_purchase_orders(
            tenant_id, skip, limit, search, supplier_id, status, start_date, end_date
        )
    
    def update_purchase_order(
        self,
        order_id: str,
        tenant_id: str,
        order_data: Dict[str, Any],
        updater_id: str
    ):
        """更新采购单"""
        order = self.purchase_repo.update_purchase_order(order_id, tenant_id, order_data)
        order.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新采购单: {order_id} by {updater_id}")
        return order
    
    def approve_purchase_order(self, order_id: str, tenant_id: str, approver_id: str):
        """审核采购单"""
        order = self.purchase_repo.approve_purchase_order(order_id, tenant_id, approver_id)
        logger.info(f"审核采购单: {order_id} by {approver_id}")
        return order
    
    def receive_purchase_order(self, order_id: str, tenant_id: str, receiver_id: str):
        """入库采购单"""
        order = self.purchase_repo.get_purchase_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("采购单", order_id)
        
        if order.status != "approved":
            raise BusinessException("只有已审核的采购单可以入库", code=400)
        
        # 入库并记录库存流水
        for item in order.items:
            # 获取当前库存
            inventory = self.inventory_repo.get_inventory_by_drug(str(item.drug_id), tenant_id)
            before_quantity = inventory.quantity if inventory else 0
            
            # 更新库存
            self.inventory_repo.update_inventory(
                str(item.drug_id),
                tenant_id,
                item.quantity
            )
            
            # 获取更新后的库存
            inventory = self.inventory_repo.get_inventory_by_drug(str(item.drug_id), tenant_id)
            after_quantity = inventory.quantity if inventory else item.quantity
            
            # 记录库存流水
            self.transaction_repo.create_transaction({
                "drug_id": str(item.drug_id),
                "transaction_type": "purchase",
                "reference_id": order_id,
                "reference_type": "purchase_order",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_amount": item.total_amount,
                "before_quantity": before_quantity,
                "after_quantity": after_quantity,
                "operator_id": receiver_id,
                "transaction_date": datetime.now(),
                "remark": f"采购入库：{order.order_no}",
            }, tenant_id)
            
            # 更新已入库数量
            item.received_quantity = item.quantity
        
        # 更新采购单状态
        order = self.purchase_repo.receive_purchase_order(order_id, tenant_id, receiver_id)
        
        logger.info(f"入库采购单: {order_id} by {receiver_id}")
        return order
    
    def delete_purchase_order(self, order_id: str, tenant_id: str, deleter_id: str) -> bool:
        """删除采购单"""
        result = self.purchase_repo.delete_purchase_order(order_id, tenant_id)
        logger.info(f"删除采购单: {order_id} by {deleter_id}")
        return result
    
    # 库存流水
    def list_transactions(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        drug_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List, int]:
        """获取库存流水列表"""
        return self.transaction_repo.get_transactions(
            tenant_id, skip, limit, drug_id, transaction_type, start_date, end_date
        )
    
    # 库存盘点
    def create_inventory_check(
        self,
        check_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ):
        """创建盘点单"""
        # 获取账面数量
        if "items" in check_data:
            for item_data in check_data["items"]:
                inventory = self.inventory_repo.get_inventory_by_drug(
                    str(item_data["drug_id"]),
                    tenant_id
                )
                item_data["book_quantity"] = inventory.quantity if inventory else 0
        
        check = self.check_repo.create_inventory_check(check_data, tenant_id)
        check.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建盘点单: {check.id} by {creator_id}")
        return check
    
    def get_inventory_check(self, check_id: str, tenant_id: str):
        """获取盘点单详情"""
        check = self.check_repo.get_inventory_check_by_id(check_id, tenant_id)
        if not check:
            raise NotFoundException("盘点单", check_id)
        return check
    
    def list_inventory_checks(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> tuple[List, int]:
        """获取盘点单列表"""
        return self.check_repo.get_inventory_checks(
            tenant_id, skip, limit, status, start_date, end_date
        )
    
    def complete_inventory_check(self, check_id: str, tenant_id: str, operator_id: str):
        """完成盘点"""
        check = self.check_repo.get_inventory_check_by_id(check_id, tenant_id)
        if not check:
            raise NotFoundException("盘点单", check_id)
        
        if check.status != "draft":
            raise BusinessException("只有草稿状态的盘点单可以完成", code=400)
        
        # 调整库存并记录流水
        for item in check.items:
            if item.difference == 0:
                continue
            
            # 获取当前库存
            inventory = self.inventory_repo.get_inventory_by_drug(str(item.drug_id), tenant_id)
            before_quantity = inventory.quantity if inventory else 0
            
            # 调整库存
            self.inventory_repo.update_inventory(
                str(item.drug_id),
                tenant_id,
                item.difference
            )
            
            # 获取调整后的库存
            inventory = self.inventory_repo.get_inventory_by_drug(str(item.drug_id), tenant_id)
            after_quantity = inventory.quantity if inventory else item.actual_quantity
            
            # 记录库存流水
            self.transaction_repo.create_transaction({
                "drug_id": str(item.drug_id),
                "transaction_type": "check",
                "reference_id": check_id,
                "reference_type": "inventory_check",
                "quantity": item.difference,
                "unit_price": item.unit_price,
                "total_amount": abs(item.difference_amount),
                "before_quantity": before_quantity,
                "after_quantity": after_quantity,
                "operator_id": operator_id,
                "transaction_date": datetime.now(),
                "remark": f"盘点调整：{check.check_no}",
            }, tenant_id)
        
        # 更新盘点单状态
        check = self.check_repo.complete_inventory_check(check_id, tenant_id)
        
        logger.info(f"完成盘点单: {check_id} by {operator_id}")
        return check
    
    def delete_inventory_check(self, check_id: str, tenant_id: str, deleter_id: str) -> bool:
        """删除盘点单"""
        result = self.check_repo.delete_inventory_check(check_id, tenant_id)
        logger.info(f"删除盘点单: {check_id} by {deleter_id}")
        return result
    
    # 退货单管理
    def create_return_order(
        self,
        order_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ):
        """创建退货单"""
        from app.api.v1.module_inventory.model import PurchaseOrder, PurchaseOrderItem
        
        # 验证采购单
        purchase_order = self.purchase_repo.get_purchase_order_by_id(
            order_data["purchase_order_id"], tenant_id
        )
        if not purchase_order:
            raise NotFoundException("采购单", order_data["purchase_order_id"])
        
        if purchase_order.status != "received":
            raise BusinessException("只能对已入库的采购单进行退货", code=400)
        
        # 验证退货明细
        if "items" not in order_data or not order_data["items"]:
            raise BusinessException("退货明细不能为空", code=400)
        
        total_amount = 0
        purchase_item_map = {str(item.id): item for item in purchase_order.items}
        
        for item_data in order_data["items"]:
            purchase_item_id = item_data["purchase_order_item_id"]
            purchase_item = purchase_item_map.get(str(purchase_item_id))
            
            if not purchase_item:
                raise NotFoundException("采购明细", purchase_item_id)
            
            return_quantity = item_data["quantity"]
            if return_quantity <= 0:
                raise BusinessException("退货数量必须大于0", code=400)
            
            # 计算该明细已退货数量
            from app.api.v1.module_inventory.model import ReturnOrderItem
            returned_quantity = self.db.query(ReturnOrderItem).join(
                ReturnOrderItem.return_order
            ).filter(
                ReturnOrderItem.purchase_order_item_id == purchase_item_id,
                ReturnOrderItem.return_order.has(status="completed"),
                ReturnOrderItem.deleted_at.is_(None)
            ).with_entities(
                func.sum(ReturnOrderItem.quantity)
            ).scalar() or 0
            
            available_quantity = purchase_item.received_quantity - returned_quantity
            if return_quantity > available_quantity:
                raise BusinessException(
                    f"退货数量({return_quantity})超过可退货数量({available_quantity})", code=400
                )
            
            # 计算金额
            unit_price = item_data.get("unit_price") or purchase_item.unit_price
            item_total = return_quantity * unit_price
            item_data["unit_price"] = unit_price
            item_data["total_amount"] = item_total
            item_data["drug_id"] = str(purchase_item.drug_id)
            item_data["batch_no"] = item_data.get("batch_no") or purchase_item.batch_no
            item_data["expiry_date"] = item_data.get("expiry_date") or purchase_item.expiry_date
            total_amount += item_total
        
        order_data["total_amount"] = total_amount
        
        # 创建退货单
        order = self.return_repo.create_return_order(order_data, tenant_id)
        order.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建退货单: {order.id} by {creator_id}")
        return order
    
    def get_return_order(self, order_id: str, tenant_id: str):
        """获取退货单详情"""
        order = self.return_repo.get_return_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("退货单", order_id)
        return order
    
    def list_return_orders(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        purchase_order_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> tuple[List, int]:
        """获取退货单列表"""
        return self.return_repo.get_return_orders(
            tenant_id, skip, limit, search, purchase_order_id, status, start_date, end_date
        )
    
    def update_return_order(
        self,
        order_id: str,
        tenant_id: str,
        order_data: Dict[str, Any],
        updater_id: str
    ):
        """更新退货单"""
        order = self.return_repo.get_return_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("退货单", order_id)
        
        if order.status != "draft":
            raise BusinessException("只有草稿状态的退货单可以更新", code=400)
        
        # 验证退货明细（如果更新明细）
        if "items" in order_data and order_data["items"]:
            purchase_order = self.purchase_repo.get_purchase_order_by_id(
                str(order.purchase_order_id), tenant_id
            )
            purchase_item_map = {str(item.id): item for item in purchase_order.items}
            
            total_amount = 0
            for item_data in order_data["items"]:
                purchase_item_id = item_data["purchase_order_item_id"]
                purchase_item = purchase_item_map.get(str(purchase_item_id))
                
                if not purchase_item:
                    raise NotFoundException("采购明细", purchase_item_id)
                
                return_quantity = item_data["quantity"]
                if return_quantity <= 0:
                    raise BusinessException("退货数量必须大于0", code=400)
                
                # 计算该明细已退货数量（排除当前退货单）
                from app.api.v1.module_inventory.model import ReturnOrderItem
                returned_quantity = self.db.query(ReturnOrderItem).join(
                    ReturnOrderItem.return_order
                ).filter(
                    ReturnOrderItem.purchase_order_item_id == purchase_item_id,
                    ReturnOrderItem.return_order_id != order.id,
                    ReturnOrderItem.return_order.has(status="completed"),
                    ReturnOrderItem.deleted_at.is_(None)
                ).with_entities(
                    func.sum(ReturnOrderItem.quantity)
                ).scalar() or 0
                
                available_quantity = purchase_item.received_quantity - returned_quantity
                if return_quantity > available_quantity:
                    raise BusinessException(
                        f"退货数量({return_quantity})超过可退货数量({available_quantity})", code=400
                    )
                
                unit_price = item_data.get("unit_price") or purchase_item.unit_price
                item_total = return_quantity * unit_price
                item_data["unit_price"] = unit_price
                item_data["total_amount"] = item_total
                item_data["drug_id"] = str(purchase_item.drug_id)
                item_data["batch_no"] = item_data.get("batch_no") or purchase_item.batch_no
                item_data["expiry_date"] = item_data.get("expiry_date") or purchase_item.expiry_date
                total_amount += item_total
            
            order_data["total_amount"] = total_amount
        
        order = self.return_repo.update_return_order(order_id, tenant_id, order_data)
        order.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新退货单: {order_id} by {updater_id}")
        return order
    
    def approve_return_order(self, order_id: str, tenant_id: str, approver_id: str):
        """审核退货单"""
        order = self.return_repo.approve_return_order(order_id, tenant_id, approver_id)
        logger.info(f"审核退货单: {order_id} by {approver_id}")
        return order
    
    def _get_or_create_system_patient(self, tenant_id: str) -> str:
        """
        获取或创建系统虚拟患者（用于系统内部账单，如退货单、采购单等）
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            str: 系统患者ID
        """
        from app.repositories.patient_repository import PatientRepository
        from app.core.encryption import encrypt_data, hash_for_query
        from app.utils.common import generate_id
        
        patient_repo = PatientRepository(self.db)
        
        # 尝试查找系统患者（病历号为SYSTEM）
        from app.api.v1.module_patient.model import Patient
        from uuid import UUID
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        system_patient = self.db.query(Patient).filter(
            Patient.tenant_id == tenant_id_uuid,
            Patient.patient_no == "SYSTEM",
            Patient.deleted_at.is_(None)
        ).first()
        
        if system_patient:
            return str(system_patient.id)
        
        # 创建系统患者
        generated_id = generate_id()
        clean_id = generated_id.replace("-", "")[:8]
        patient_data = {
            "patient_no": "SYSTEM",
            "name_encrypted": encrypt_data("系统账户"),
            "remark": "系统虚拟患者，用于系统内部账单（如退货单、采购单等）"
        }
        
        system_patient = patient_repo.create_patient(patient_data, tenant_id)
        logger.info(f"创建系统虚拟患者: {system_patient.id} for tenant {tenant_id}")
        return str(system_patient.id)
    
    def complete_return_order(self, order_id: str, tenant_id: str, completer_id: str):
        """完成退货单（执行退货）"""
        from app.api.v1.module_inventory.model import PurchaseOrderItem
        from app.repositories.payment_repository import BillRepository
        from app.utils.common import generate_id
        from decimal import Decimal
        from sqlalchemy import func
        
        order = self.return_repo.get_return_order_by_id(order_id, tenant_id)
        if not order:
            raise NotFoundException("退货单", order_id)
        
        if order.status != "approved":
            raise BusinessException("只有已审核的退货单可以完成", code=400)
        
        # 使用事务处理
        try:
            # 1. 更新库存和创建库存流水
            for item in order.items:
                # 获取当前库存
                inventory = self.inventory_repo.get_inventory_by_drug(str(item.drug_id), tenant_id)
                before_quantity = inventory.quantity if inventory else 0
                
                # 扣减库存（退货数量为负数）
                return_quantity = -item.quantity
                self.inventory_repo.update_inventory(
                    str(item.drug_id),
                    tenant_id,
                    return_quantity
                )
                
                # 获取更新后的库存
                inventory = self.inventory_repo.get_inventory_by_drug(str(item.drug_id), tenant_id)
                after_quantity = inventory.quantity if inventory else 0
                
                # 记录库存流水
                self.transaction_repo.create_transaction({
                    "drug_id": str(item.drug_id),
                    "transaction_type": "return",
                    "reference_id": order_id,
                    "reference_type": "return_order",
                    "quantity": return_quantity,  # 负数
                    "unit_price": item.unit_price,
                    "total_amount": item.total_amount,
                    "before_quantity": before_quantity,
                    "after_quantity": after_quantity,
                    "operator_id": completer_id,
                    "transaction_date": datetime.now(),
                    "remark": f"退货出库：{order.return_no}",
                }, tenant_id)
                
                # 2. 更新采购单明细的已入库数量
                purchase_item = self.db.query(PurchaseOrderItem).filter(
                    PurchaseOrderItem.id == item.purchase_order_item_id
                ).first()
                if purchase_item:
                    purchase_item.received_quantity -= item.quantity
                    if purchase_item.received_quantity < 0:
                        purchase_item.received_quantity = 0
            
            # 3. 创建财务记录
            system_patient_id = self._get_or_create_system_patient(tenant_id)
            bill_repo = BillRepository(self.db)
            
            # 生成账单号
            generated_id = generate_id()
            bill_no = f"BILL{generated_id[:8].upper()}"
            
            # 准备账单明细项
            from app.api.v1.module_pharmacy.model import Drug
            
            bill_items = []
            for item in order.items:
                # 查询药品信息
                drug = self.db.query(Drug).filter(Drug.id == item.drug_id).first()
                drug_name = drug.name if drug else ""
                
                bill_items.append({
                    "drug_name": drug_name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "amount": float(item.total_amount)
                })
            
            # 创建账单（退货金额为负数，表示退款）
            bill_data = {
                "bill_no": bill_no,
                "patient_id": system_patient_id,
                "bill_type": "purchase_return",
                "total_amount": Decimal(str(order.total_amount)),
                "paid_amount": Decimal("0"),
                "discount_amount": Decimal("0"),
                "insurance_amount": Decimal("0"),
                "status": "paid",  # 退货单完成即视为已支付（退款）
                "payment_method": "system",
                "payment_time": datetime.now(),
                "items": bill_items,
                "remark": f"退货单：{order.return_no}，关联采购单：{order.purchase_order.order_no if order.purchase_order else ''}"
            }
            
            bill = bill_repo.create_bill(bill_data, tenant_id)
            from uuid import UUID
            if isinstance(completer_id, str):
                try:
                    completer_id_uuid = UUID(completer_id)
                except (ValueError, TypeError):
                    completer_id_uuid = completer_id
            else:
                completer_id_uuid = completer_id
            bill.created_by = completer_id_uuid
            logger.info(f"创建退货单财务记录: {bill.id} for return order {order_id}")
            
            # 4. 更新退货单状态
            order = self.return_repo.complete_return_order(order_id, tenant_id, completer_id)
            
            self.db.commit()
            logger.info(f"完成退货单: {order_id} by {completer_id}")
            return order
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"完成退货单失败: {order_id}, 错误: {str(e)}", exc_info=True)
            raise BusinessException(f"完成退货单失败: {str(e)}", code=500)
    
    def cancel_return_order(self, order_id: str, tenant_id: str):
        """取消退货单"""
        order = self.return_repo.cancel_return_order(order_id, tenant_id)
        logger.info(f"取消退货单: {order_id}")
        return order
    
    def delete_return_order(self, order_id: str, tenant_id: str, deleter_id: str) -> bool:
        """删除退货单"""
        result = self.return_repo.delete_return_order(order_id, tenant_id)
        logger.info(f"删除退货单: {order_id} by {deleter_id}")
        return result
    
    def get_returnable_purchase_order(self, purchase_order_id: str, tenant_id: str):
        """获取可退货的采购单信息"""
        purchase_order = self.purchase_repo.get_purchase_order_by_id(purchase_order_id, tenant_id)
        if not purchase_order:
            raise NotFoundException("采购单", purchase_order_id)
        
        if purchase_order.status != "received":
            raise BusinessException("只能对已入库的采购单进行退货", code=400)
        
        # 计算每个明细的可退货数量
        from app.api.v1.module_inventory.model import ReturnOrderItem
        
        # 导入Drug模型
        from app.api.v1.module_pharmacy.model import Drug
        
        returnable_items = []
        for item in purchase_order.items:
            # 查询药品信息
            drug = self.db.query(Drug).filter(Drug.id == item.drug_id).first()
            drug_name = drug.name if drug else ""
            
            # 计算已退货数量
            returned_quantity = self.db.query(ReturnOrderItem).join(
                ReturnOrderItem.return_order
            ).filter(
                ReturnOrderItem.purchase_order_item_id == item.id,
                ReturnOrderItem.return_order.has(status="completed"),
                ReturnOrderItem.deleted_at.is_(None)
            ).with_entities(
                func.sum(ReturnOrderItem.quantity)
            ).scalar() or 0
            
            available_quantity = item.received_quantity - returned_quantity
            if available_quantity > 0:
                returnable_items.append({
                    "id": str(item.id),
                    "drug_id": str(item.drug_id),
                    "drug_name": drug_name,
                    "quantity": item.quantity,
                    "received_quantity": item.received_quantity,
                    "returned_quantity": returned_quantity,
                    "available_quantity": available_quantity,
                    "unit_price": float(item.unit_price),
                    "batch_no": item.batch_no,
                    "expiry_date": item.expiry_date
                })
        
        return {
            "purchase_order": {
                "id": str(purchase_order.id),
                "order_no": purchase_order.order_no,
                "supplier_id": str(purchase_order.supplier_id),
                "supplier_name": purchase_order.supplier.name if purchase_order.supplier else "",
                "order_date": purchase_order.order_date.isoformat() if purchase_order.order_date else None,
                "total_amount": float(purchase_order.total_amount)
            },
            "items": returnable_items
        }

