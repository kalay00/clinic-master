"""
进销存服务（对齐旧 services/inventory_service.py + repositories/inventory_repository.py，迁移为异步 + CRUDBase，Python 3.12+）

业务规则：
- 供应商 / 采购单（含明细）/ 库存流水 / 盘点单（含明细）/ 退货单（含明细）
- 采购入库：累加库存 + 写流水
- 盘点完成：按差异调整库存 + 写流水
- 退货完成：扣库存 + 写流水 + 生成系统虚拟患者账单
"""
from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.core.encryption import encrypt_data
from app.utils.common import generate_id

from app.api.v1.module_inventory.model import (
    Supplier,
    PurchaseOrder,
    PurchaseOrderItem,
    InventoryTransaction,
    InventoryCheck,
    InventoryCheckItem,
    ReturnOrder,
    ReturnOrderItem,
)
from app.api.v1.module_patient.model import Patient
from app.api.v1.module_pharmacy.model import Drug

from .schema import (
    SupplierSchema, SupplierCreateSchema, SupplierUpdateSchema,
    PurchaseOrderSchema, PurchaseOrderCreateSchema, PurchaseOrderUpdateSchema,
    PurchaseOrderItemSchema, PurchaseOrderItemCreateSchema, PurchaseOrderItemUpdateSchema,
    InventoryTransactionSchema, InventoryTransactionCreateSchema, InventoryTransactionUpdateSchema,
    InventoryCheckSchema, InventoryCheckCreateSchema, InventoryCheckUpdateSchema,
    InventoryCheckItemSchema, InventoryCheckItemCreateSchema, InventoryCheckItemUpdateSchema,
    ReturnOrderSchema, ReturnOrderCreateSchema, ReturnOrderUpdateSchema,
    ReturnOrderItemSchema, ReturnOrderItemCreateSchema, ReturnOrderItemUpdateSchema,
)
from .crud import (
    SupplierCRUD, PurchaseOrderCRUD, PurchaseOrderItemCRUD,
    InventoryTransactionCRUD, InventoryCheckCRUD, InventoryCheckItemCRUD,
    ReturnOrderCRUD, ReturnOrderItemCRUD,
)


class InventoryService:
    """进销存服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = SupplierCRUD(Supplier, auth=auth)
        self.po_crud = PurchaseOrderCRUD(PurchaseOrder, auth=auth)
        self.po_item_crud = PurchaseOrderItemCRUD(PurchaseOrderItem, auth=auth)
        self.tx_crud = InventoryTransactionCRUD(InventoryTransaction, auth=auth)
        self.check_crud = InventoryCheckCRUD(InventoryCheck, auth=auth)
        self.check_item_crud = InventoryCheckItemCRUD(InventoryCheckItem, auth=auth)
        self.return_crud = ReturnOrderCRUD(ReturnOrder, auth=auth)
        self.return_item_crud = ReturnOrderItemCRUD(ReturnOrderItem, auth=auth)

    @property
    def _db(self):
        return self.crud.db

    @property
    def _tenant_id(self) -> Optional[str]:
        return self.auth.tenant_id if self.auth else None

    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    async def _pharmacy(self):
        from app.api.v1.module_pharmacy.service import PharmacyService

        return PharmacyService(self.auth)

    async def _payment(self):
        from app.api.v1.module_payment.service import PaymentService

        return PaymentService(self.auth)

    # ── 供应商（primary）──
    async def create(self, data: SupplierCreateSchema) -> SupplierSchema:
        obj = await self.crud.create(data)
        uid = self._user_id
        if uid and hasattr(obj, "created_by"):
            setattr(obj, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return SupplierSchema.model_validate(obj)

    async def get(self, id: str) -> SupplierSchema:
        return await self.crud.get_or_404(id=id, out_schema=SupplierSchema)

    async def list(
        self, page_no: int, page_size: int, order_by=None, search: Optional[dict] = None
    ) -> object:
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            out_schema=SupplierSchema,
        )

    async def update(self, id: str, data: SupplierUpdateSchema) -> SupplierSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return SupplierSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    async def create_supplier(self, supplier_data: dict, creator_id: Optional[str] = None) -> SupplierSchema:
        obj = await self.crud.create(supplier_data)
        uid = creator_id or self._user_id
        if uid and hasattr(obj, "created_by"):
            setattr(obj, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return SupplierSchema.model_validate(obj)

    async def get_supplier(self, supplier_id: str) -> SupplierSchema:
        return await self.crud.get_or_404(id=supplier_id, out_schema=SupplierSchema)

    async def list_suppliers(
        self, skip: int = 0, limit: int = 100,
        search: Optional[str] = None, status: Optional[str] = None,
    ) -> tuple[list[SupplierSchema], int]:
        stmt = select(Supplier).where(Supplier.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(Supplier.tenant_id == self._tenant_id)
        if search:
            stmt = stmt.where(Supplier.name.ilike(f"%{search}%") | Supplier.code.ilike(f"%{search}%"))
        if status:
            stmt = stmt.where(Supplier.status == status)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.offset(skip).limit(limit))).scalars().all()
        return [SupplierSchema.model_validate(r) for r in rows], int(total or 0)

    async def update_supplier(self, supplier_id: str, supplier_data: dict, updater_id: Optional[str] = None) -> SupplierSchema:
        obj = await self.crud.update(supplier_id, supplier_data)
        uid = updater_id or self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return SupplierSchema.model_validate(obj)

    async def delete_supplier(self, supplier_id: str, deleter_id: Optional[str] = None) -> bool:
        await self.crud.delete([supplier_id])
        return True

    # ── 采购单 ──
    @staticmethod
    def _generate_order_no(prefix: str = "PO") -> str:
        """生成单据编号：前缀 + 毫秒级时间戳，保证唯一且可读。"""
        return f"{prefix}{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"

    @staticmethod
    def _parse_date(value):
        """将前端传入的日期字符串解析为 date，已为 date/None 则原样返回。"""
        if value is None or value == "":
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value[:10], "%Y-%m-%d").date()
            except ValueError:
                return None
        return None

    async def create_purchase_order(self, order_data: dict, creator_id: Optional[str] = None) -> PurchaseOrderSchema:
        items = order_data.pop("items", None)
        # 前端未传采购单号时自动生成（order_no 列非空且唯一）
        if not order_data.get("order_no"):
            order_data["order_no"] = self._generate_order_no()
        # 解析日期字符串（前端传入 YYYY-MM-DD）
        order_data["order_date"] = self._parse_date(order_data.get("order_date"))
        order_data["expected_date"] = self._parse_date(order_data.get("expected_date"))
        # 计算总金额并补全每条明细的 total_amount
        if items:
            computed_total = 0
            for it in items:
                it = dict(it)
                qty = it.get("quantity") or 0
                price = it.get("unit_price") or 0
                it_total = it.get("total_amount") or (qty * price)
                it["total_amount"] = it_total
                computed_total += it_total
            order_data["total_amount"] = computed_total
        order = await self.po_crud.create(order_data)
        uid = creator_id or self._user_id
        if uid and hasattr(order, "created_by"):
            setattr(order, "created_by", uid)
            await self._db.flush()
        if items:
            for it in items:
                it = dict(it)
                it["purchase_order_id"] = order.id
                await self.po_item_crud.create(it)
        await self._db.commit()
        return PurchaseOrderSchema.model_validate(order)

    async def get_purchase_order(self, order_id: str) -> PurchaseOrderSchema:
        order = await self.po_crud.get(id=order_id)
        if not order:
            raise CustomException(msg="采购单不存在")
        return PurchaseOrderSchema.model_validate(order)

    async def list_purchase_orders(
        self, skip: int = 0, limit: int = 100, search: Optional[str] = None,
        supplier_id: Optional[str] = None, status: Optional[str] = None,
        start_date: Optional[date] = None, end_date: Optional[date] = None,
    ) -> tuple[list[PurchaseOrderSchema], int]:
        stmt = select(PurchaseOrder).where(PurchaseOrder.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(PurchaseOrder.tenant_id == self._tenant_id)
        if supplier_id:
            stmt = stmt.where(PurchaseOrder.supplier_id == supplier_id)
        if status:
            stmt = stmt.where(PurchaseOrder.status == status)
        if start_date and end_date:
            stmt = stmt.where(PurchaseOrder.order_date >= start_date, PurchaseOrder.order_date <= end_date)
        if search:
            stmt = stmt.where(PurchaseOrder.order_no.ilike(f"%{search}%"))
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit))).scalars().all()

        # 批量补全供应商名称（前端列表“供应商”列使用 supplier_name）
        supplier_ids = [str(r.supplier_id) for r in rows if r.supplier_id]
        supplier_map: dict = {}
        if supplier_ids:
            sup_rows = (await self._db.execute(select(Supplier).where(Supplier.id.in_(supplier_ids)))).scalars().all()
            for s in sup_rows:
                supplier_map[str(s.id)] = getattr(s, "name", "") or ""

        result = []
        for r in rows:
            d = PurchaseOrderSchema.model_validate(r).model_dump()
            d["supplier_name"] = supplier_map.get(str(r.supplier_id), "") if r.supplier_id else ""
            result.append(d)
        return result, int(total or 0)

    async def update_purchase_order(self, order_id: str, order_data: dict, updater_id: Optional[str] = None) -> PurchaseOrderSchema:
        order_data["order_date"] = self._parse_date(order_data.get("order_date"))
        order_data["expected_date"] = self._parse_date(order_data.get("expected_date"))
        obj = await self.po_crud.update(order_id, order_data)
        uid = updater_id or self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return PurchaseOrderSchema.model_validate(obj)

    async def get_purchase_order_detail(self, order_id: str) -> dict:
        """采购单详情：订单字段 + 富化明细（含药品名称/规格）。

        PurchaseOrderSchema 不含 items 关系字段，这里联表 drugs 补全
        每条明细的 drug_name / specification，供前端详情弹窗展示。
        """
        order = await self.po_crud.get(id=order_id)
        if not order:
            raise CustomException(msg="采购单不存在")
        data = PurchaseOrderSchema.model_validate(order).model_dump()

        # 补全供应商名称
        if order.supplier_id:
            supplier = (await self._db.execute(
                select(Supplier).where(Supplier.id == order.supplier_id)
            )).scalars().first()
            data["supplier_name"] = getattr(supplier, "name", "") or "" if supplier else ""
        else:
            data["supplier_name"] = ""

        stmt = select(PurchaseOrderItem).where(
            PurchaseOrderItem.purchase_order_id == order_id,
            PurchaseOrderItem.deleted_at.is_(None),
        )
        item_rows = (await self._db.execute(stmt)).scalars().all()

        drug_ids = [str(it.drug_id) for it in item_rows if it.drug_id]
        drug_map: dict = {}
        if drug_ids:
            drug_rows = (await self._db.execute(select(Drug).where(Drug.id.in_(drug_ids)))).scalars().all()
            for d in drug_rows:
                drug_map[str(d.id)] = d

        items = []
        for it in item_rows:
            item_dict = PurchaseOrderItemSchema.model_validate(it).model_dump()
            drug = drug_map.get(str(it.drug_id)) if it.drug_id else None
            if drug is not None:
                item_dict["drug_name"] = getattr(drug, "name", "") or ""
                item_dict["specification"] = getattr(drug, "specification", "") or ""
            else:
                item_dict["drug_name"] = ""
                item_dict["specification"] = ""
            items.append(item_dict)
        data["items"] = items
        return data

    async def approve_purchase_order(self, order_id: str, approver_id: Optional[str] = None) -> PurchaseOrderSchema:
        obj = await self.po_crud.update(order_id, {
            "status": "approved", "approved_by": approver_id or self._user_id, "approved_at": datetime.now(),
        })
        await self._db.commit()
        return PurchaseOrderSchema.model_validate(obj)

    async def receive_purchase_order(self, order_id: str, receiver_id: Optional[str] = None) -> PurchaseOrderSchema:
        order = await self.po_crud.get(id=order_id, preload=["items"])
        if not order:
            raise CustomException(msg="采购单不存在")
        if order.status != "approved":
            raise CustomException(msg="只有已审核的采购单可以入库", code=400)

        pharmacy = await self._pharmacy()
        for item in order.items:
            inv = await pharmacy.get_inventory(str(item.drug_id))
            before_quantity = inv.quantity if inv else 0
            await pharmacy.update_inventory(str(item.drug_id), item.quantity, operator_id=receiver_id or self._user_id)
            after_inv = await pharmacy.get_inventory(str(item.drug_id))
            after_quantity = after_inv.quantity if after_inv else item.quantity
            await self.tx_crud.create({
                "drug_id": str(item.drug_id),
                "transaction_type": "purchase",
                "reference_id": order.id,
                "reference_type": "purchase_order",
                "quantity": item.quantity,
                "unit_price": float(item.unit_price) if item.unit_price is not None else 0,
                "total_amount": float(item.total_amount) if item.total_amount is not None else 0,
                "before_quantity": before_quantity,
                "after_quantity": after_quantity,
                "operator_id": receiver_id or self._user_id,
                "transaction_date": datetime.now(),
                "remark": f"采购入库：{order.order_no}",
            })
            item.received_quantity = item.quantity

        obj = await self.po_crud.update(order_id, {
            "status": "received", "received_by": receiver_id or self._user_id, "received_at": datetime.now(),
        })
        await self._db.commit()
        logger.info(f"入库采购单: {order_id} by {receiver_id or self._user_id}")
        return PurchaseOrderSchema.model_validate(obj)

    async def delete_purchase_order(self, order_id: str, deleter_id: Optional[str] = None) -> bool:
        await self.po_crud.delete([order_id])
        return True

    # ── 库存流水 ──
    async def list_transactions(
        self, skip: int = 0, limit: int = 100, drug_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
    ) -> tuple[list[InventoryTransactionSchema], int]:
        stmt = select(InventoryTransaction).where(InventoryTransaction.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(InventoryTransaction.tenant_id == self._tenant_id)
        if drug_id:
            stmt = stmt.where(InventoryTransaction.drug_id == drug_id)
        if transaction_type:
            stmt = stmt.where(InventoryTransaction.transaction_type == transaction_type)
        if start_date and end_date:
            stmt = stmt.where(InventoryTransaction.transaction_date >= start_date, InventoryTransaction.transaction_date <= end_date)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.order_by(InventoryTransaction.transaction_date.desc()).offset(skip).limit(limit))).scalars().all()
        return [InventoryTransactionSchema.model_validate(r) for r in rows], int(total or 0)

    # ── 盘点单 ──
    async def create_inventory_check(self, check_data: dict, creator_id: Optional[str] = None) -> InventoryCheckSchema:
        items = check_data.pop("items", None)
        if items:
            pharmacy = await self._pharmacy()
            for it in items:
                inv = await pharmacy.get_inventory(str(it["drug_id"]))
                it["book_quantity"] = inv.quantity if inv else 0
        check = await self.check_crud.create(check_data)
        uid = creator_id or self._user_id
        if uid and hasattr(check, "created_by"):
            setattr(check, "created_by", uid)
            await self._db.flush()
        if items:
            for it in items:
                it = dict(it)
                it["inventory_check_id"] = check.id
                await self.check_item_crud.create(it)
        await self._db.commit()
        return InventoryCheckSchema.model_validate(check)

    async def get_inventory_check(self, check_id: str) -> InventoryCheckSchema:
        check = await self.check_crud.get(id=check_id)
        if not check:
            raise CustomException(msg="盘点单不存在")
        return InventoryCheckSchema.model_validate(check)

    async def list_inventory_checks(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        start_date: Optional[date] = None, end_date: Optional[date] = None,
    ) -> tuple[list[InventoryCheckSchema], int]:
        stmt = select(InventoryCheck).where(InventoryCheck.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(InventoryCheck.tenant_id == self._tenant_id)
        if status:
            stmt = stmt.where(InventoryCheck.status == status)
        if start_date and end_date:
            stmt = stmt.where(InventoryCheck.check_date >= start_date, InventoryCheck.check_date <= end_date)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.order_by(InventoryCheck.created_at.desc()).offset(skip).limit(limit))).scalars().all()
        return [InventoryCheckSchema.model_validate(r) for r in rows], int(total or 0)

    async def complete_inventory_check(self, check_id: str, operator_id: Optional[str] = None) -> InventoryCheckSchema:
        check = await self.check_crud.get(id=check_id, preload=["items"])
        if not check:
            raise CustomException(msg="盘点单不存在")
        if check.status != "draft":
            raise CustomException(msg="只有草稿状态的盘点单可以完成", code=400)

        pharmacy = await self._pharmacy()
        uid = operator_id or self._user_id
        for item in check.items:
            if item.difference == 0:
                continue
            inv = await pharmacy.get_inventory(str(item.drug_id))
            before_quantity = inv.quantity if inv else 0
            await pharmacy.update_inventory(str(item.drug_id), item.difference, operator_id=uid)
            after_inv = await pharmacy.get_inventory(str(item.drug_id))
            after_quantity = after_inv.quantity if after_inv else item.actual_quantity
            await self.tx_crud.create({
                "drug_id": str(item.drug_id),
                "transaction_type": "check",
                "reference_id": check.id,
                "reference_type": "inventory_check",
                "quantity": item.difference,
                "unit_price": float(item.unit_price) if item.unit_price is not None else 0,
                "total_amount": float(abs(item.difference_amount)) if item.difference_amount is not None else 0,
                "before_quantity": before_quantity,
                "after_quantity": after_quantity,
                "operator_id": uid,
                "transaction_date": datetime.now(),
                "remark": f"盘点调整：{check.check_no}",
            })

        obj = await self.check_crud.update(check_id, {"status": "completed"})
        await self._db.commit()
        logger.info(f"完成盘点单: {check_id} by {uid}")
        return InventoryCheckSchema.model_validate(obj)

    async def delete_inventory_check(self, check_id: str, deleter_id: Optional[str] = None) -> bool:
        await self.check_crud.delete([check_id])
        return True

    # ── 退货单 ──
    async def _get_or_create_system_patient(self) -> str:
        system_patient = (
            await self._db.execute(
                select(Patient).where(
                    Patient.tenant_id == self._tenant_id,
                    Patient.patient_no == "SYSTEM",
                    Patient.deleted_at.is_(None),
                )
            )
        ).scalars().first()
        if system_patient:
            return str(system_patient.id)
        patient = Patient(
            tenant_id=self._tenant_id,
            patient_no="SYSTEM",
            name_encrypted=encrypt_data("系统账户"),
            remark="系统虚拟患者，用于系统内部账单（如退货单、采购单等）",
        )
        self._db.add(patient)
        await self._db.flush()
        logger.info(f"创建系统虚拟患者: {patient.id} for tenant {self._tenant_id}")
        return str(patient.id)

    async def create_return_order(self, order_data: dict, creator_id: Optional[str] = None) -> ReturnOrderSchema:
        purchase_order_id = order_data["purchase_order_id"]
        po = await self.po_crud.get(id=purchase_order_id, preload=["items"])
        if not po:
            raise CustomException(msg="采购单不存在", code=404, status_code=404)
        if po.status != "received":
            raise CustomException(msg="只能对已入库的采购单进行退货", code=400, status_code=400)
        # 必须 pop 掉 items：否则会随 order_data 一起传入模型构造，
        # SQLAlchemy 将 dict 列表当作关系赋值，报 '_sa_instance_state' 错误
        items = order_data.pop("items", None) or []
        if not items:
            raise CustomException(msg="退货明细不能为空", code=400, status_code=400)
        # 退货日期非空，前端传 YYYY-MM-DD 字符串，需解析为 date（否则 asyncpg DataError）
        order_data["return_date"] = self._parse_date(order_data.get("return_date"))
        # 后端不生成退货单号，模型非空唯一，前端未传时兜底生成
        if not order_data.get("return_no"):
            order_data["return_no"] = self._generate_order_no("RET")

        total_amount = Decimal("0")
        purchase_item_map = {str(it.id): it for it in po.items}
        for it in items:
            p_item = purchase_item_map.get(str(it["purchase_order_item_id"]))
            if not p_item:
                raise CustomException(msg=f"采购明细不存在: {it['purchase_order_item_id']}")
            qty = it["quantity"]
            if qty <= 0:
                raise CustomException(msg="退货数量必须大于0", code=400)
            returned = await self._sum_returned_qty(it["purchase_order_item_id"], exclude_order_id=None)
            available = p_item.received_quantity - returned
            if qty > available:
                raise CustomException(msg=f"退货数量({qty})超过可退货数量({available})", code=400)
            unit_price = it.get("unit_price") or p_item.unit_price
            it["unit_price"] = float(unit_price) if unit_price is not None else 0
            it["total_amount"] = float(qty * Decimal(str(unit_price))) if unit_price is not None else 0
            it["drug_id"] = str(p_item.drug_id)
            it["batch_no"] = it.get("batch_no") or p_item.batch_no
            it["expiry_date"] = it.get("expiry_date") or p_item.expiry_date
            total_amount += Decimal(str(it["total_amount"]))
        order_data["total_amount"] = float(total_amount)

        order = await self.return_crud.create(order_data)
        uid = creator_id or self._user_id
        if uid and hasattr(order, "created_by"):
            setattr(order, "created_by", uid)
            await self._db.flush()
        for it in items:
            it2 = dict(it)
            it2["return_order_id"] = order.id
            await self.return_item_crud.create(it2)
        await self._db.commit()
        return ReturnOrderSchema.model_validate(order)

    async def _sum_returned_qty(self, purchase_order_item_id: str, exclude_order_id=None) -> int:
        stmt = select(func.coalesce(func.sum(ReturnOrderItem.quantity), 0)).join(
            ReturnOrderItem.return_order
        ).where(
            ReturnOrderItem.purchase_order_item_id == purchase_order_item_id,
            ReturnOrder.status == "completed",
            ReturnOrderItem.deleted_at.is_(None),
        )
        if exclude_order_id:
            stmt = stmt.where(ReturnOrder.id != exclude_order_id)
        return int((await self._db.execute(stmt)).scalar() or 0)

    async def get_return_order(self, order_id: str) -> ReturnOrderSchema:
        order = await self.return_crud.get(id=order_id)
        if not order:
            raise CustomException(msg="退货单不存在")
        return ReturnOrderSchema.model_validate(order)

    async def list_return_orders(
        self, skip: int = 0, limit: int = 100, search: Optional[str] = None,
        purchase_order_id: Optional[str] = None, status: Optional[str] = None,
        start_date: Optional[date] = None, end_date: Optional[date] = None,
    ) -> tuple[list[ReturnOrderSchema], int]:
        stmt = select(ReturnOrder).where(ReturnOrder.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(ReturnOrder.tenant_id == self._tenant_id)
        if purchase_order_id:
            stmt = stmt.where(ReturnOrder.purchase_order_id == purchase_order_id)
        if status:
            stmt = stmt.where(ReturnOrder.status == status)
        if start_date and end_date:
            stmt = stmt.where(ReturnOrder.return_date >= start_date, ReturnOrder.return_date <= end_date)
        if search:
            stmt = stmt.where(ReturnOrder.return_no.ilike(f"%{search}%"))
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.order_by(ReturnOrder.created_at.desc()).offset(skip).limit(limit))).scalars().all()
        return [ReturnOrderSchema.model_validate(r) for r in rows], int(total or 0)

    async def update_return_order(self, order_id: str, order_data: dict, updater_id: Optional[str] = None) -> ReturnOrderSchema:
        order = await self.return_crud.get(id=order_id, preload=["items"])
        if not order:
            raise CustomException(msg="退货单不存在")
        if order.status != "draft":
            raise CustomException(msg="只有草稿状态的退货单可以更新", code=400)
        items = order_data.get("items")
        if items:
            po = await self.po_crud.get(id=str(order.purchase_order_id), preload=["items"])
            purchase_item_map = {str(it.id): it for it in po.items}
            total_amount = Decimal("0")
            for it in items:
                p_item = purchase_item_map.get(str(it["purchase_order_item_id"]))
                if not p_item:
                    raise CustomException(msg=f"采购明细不存在: {it['purchase_order_item_id']}")
                qty = it["quantity"]
                if qty <= 0:
                    raise CustomException(msg="退货数量必须大于0", code=400)
                returned = await self._sum_returned_qty(it["purchase_order_item_id"], exclude_order_id=order_id)
                available = p_item.received_quantity - returned
                if qty > available:
                    raise CustomException(msg=f"退货数量({qty})超过可退货数量({available})", code=400)
                unit_price = it.get("unit_price") or p_item.unit_price
                it["unit_price"] = float(unit_price) if unit_price is not None else 0
                it["total_amount"] = float(qty * Decimal(str(unit_price))) if unit_price is not None else 0
                it["drug_id"] = str(p_item.drug_id)
                it["batch_no"] = it.get("batch_no") or p_item.batch_no
                it["expiry_date"] = it.get("expiry_date") or p_item.expiry_date
                total_amount += Decimal(str(it["total_amount"]))
            order_data["total_amount"] = float(total_amount)
        obj = await self.return_crud.update(order_id, order_data)
        uid = updater_id or self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return ReturnOrderSchema.model_validate(obj)

    async def approve_return_order(self, order_id: str, approver_id: Optional[str] = None) -> ReturnOrderSchema:
        obj = await self.return_crud.update(order_id, {
            "status": "approved", "approved_by": approver_id or self._user_id, "approved_at": datetime.now(),
        })
        await self._db.commit()
        return ReturnOrderSchema.model_validate(obj)

    async def complete_return_order(self, order_id: str, completer_id: Optional[str] = None) -> ReturnOrderSchema:
        order = await self.return_crud.get(id=order_id, preload=["items"])
        if not order:
            raise CustomException(msg="退货单不存在")
        if order.status != "approved":
            raise CustomException(msg="只有已审核的退货单可以完成", code=400)
        uid = completer_id or self._user_id
        pharmacy = await self._pharmacy()
        try:
            for item in order.items:
                inv = await pharmacy.get_inventory(str(item.drug_id))
                before_quantity = inv.quantity if inv else 0
                await pharmacy.update_inventory(str(item.drug_id), -item.quantity, operator_id=uid)
                after_inv = await pharmacy.get_inventory(str(item.drug_id))
                after_quantity = after_inv.quantity if after_inv else 0
                await self.tx_crud.create({
                    "drug_id": str(item.drug_id),
                    "transaction_type": "return",
                    "reference_id": order.id,
                    "reference_type": "return_order",
                    "quantity": -item.quantity,
                    "unit_price": float(item.unit_price) if item.unit_price is not None else 0,
                    "total_amount": float(item.total_amount) if item.total_amount is not None else 0,
                    "before_quantity": before_quantity,
                    "after_quantity": after_quantity,
                    "operator_id": uid,
                    "transaction_date": datetime.now(),
                    "remark": f"退货出库：{order.return_no}",
                })
                p_item = await self.po_item_crud.get(id=str(item.purchase_order_item_id))
                if p_item:
                    p_item.received_quantity = max(0, (p_item.received_quantity or 0) - item.quantity)
                    await self._db.flush()

            # 财务记录
            system_patient_id = await self._get_or_create_system_patient()
            bill_items = []
            for item in order.items:
                drug = (await self._db.execute(select(Drug).where(Drug.id == item.drug_id))).scalars().first()
                bill_items.append({
                    "drug_name": drug.name if drug else "",
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price) if item.unit_price is not None else 0,
                    "amount": float(item.total_amount) if item.total_amount is not None else 0,
                })
            payment = await self._payment()
            await payment.create_bill({
                "bill_no": f"BILL{generate_id()[:8].upper()}",
                "patient_id": system_patient_id,
                "bill_type": "purchase_return",
                "total_amount": Decimal(str(order.total_amount)),
                "paid_amount": Decimal("0"),
                "discount_amount": Decimal("0"),
                "insurance_amount": Decimal("0"),
                "status": "paid",
                "payment_method": "system",
                "payment_time": datetime.now(),
                "items": bill_items,
                "remark": f"退货单：{order.return_no}",
            }, creator_id=uid)

            obj = await self.return_crud.update(order_id, {
                "status": "completed", "completed_by": uid, "completed_at": datetime.now(),
            })
            await self._db.commit()
            logger.info(f"完成退货单: {order_id} by {uid}")
            return ReturnOrderSchema.model_validate(obj)
        except Exception as e:
            await self._db.rollback()
            logger.error(f"完成退货单失败: {order_id}, 错误: {e!s}", exc_info=True)
            raise CustomException(msg=f"完成退货单失败: {e!s}", code=500)

    async def cancel_return_order(self, order_id: str) -> ReturnOrderSchema:
        obj = await self.return_crud.update(order_id, {"status": "cancelled"})
        await self._db.commit()
        return ReturnOrderSchema.model_validate(obj)

    async def delete_return_order(self, order_id: str, deleter_id: Optional[str] = None) -> bool:
        await self.return_crud.delete([order_id])
        return True

    async def get_returnable_purchase_order(self, purchase_order_id: str) -> dict:
        po = await self.po_crud.get(id=purchase_order_id, preload=["items", "supplier"])
        if not po:
            raise CustomException(msg="采购单不存在")
        if po.status != "received":
            raise CustomException(msg="只能对已入库的采购单进行退货", code=400)
        returnable_items = []
        for item in po.items:
            drug = (await self._db.execute(select(Drug).where(Drug.id == item.drug_id))).scalars().first()
            returned = await self._sum_returned_qty(str(item.id))
            available = (item.received_quantity or 0) - returned
            if available > 0:
                returnable_items.append({
                    "id": str(item.id),
                    "drug_id": str(item.drug_id),
                    "drug_name": drug.name if drug else "",
                    "quantity": item.quantity,
                    "received_quantity": item.received_quantity,
                    "returned_quantity": returned,
                    "available_quantity": available,
                    "unit_price": float(item.unit_price) if item.unit_price is not None else 0,
                    "batch_no": item.batch_no,
                    "expiry_date": item.expiry_date,
                })
        return {
            "purchase_order": {
                "id": str(po.id),
                "order_no": po.order_no,
                "supplier_id": str(po.supplier_id),
                "supplier_name": po.supplier.name if po.supplier else "",
                "order_date": po.order_date.isoformat() if po.order_date else None,
                "total_amount": float(po.total_amount) if po.total_amount is not None else 0,
            },
            "items": returnable_items,
        }
