"""
药房服务（对齐旧 services/pharmacy_service.py + repositories/pharmacy_repository.py，迁移为异步 + CRUDBase，Python 3.12+）

业务规则：
- 药品 CRUD
- 库存按药品增减（入库/出库），不足则报错
- 发药：扣库存 + 写发药记录 + 同步处方状态为已发药
- 库存预警：低库存 / 过期 / 即将过期
"""
from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import joinedload

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.api.v1.module_pharmacy.model import Drug, Inventory, Dispense, PriceAdjustment, PriceAdjustmentItem
from app.api.v1.module_tenant.model import Tenant

from .schema import (
    DrugSchema,
    DrugCreateSchema,
    DrugUpdateSchema,
    InventorySchema,
    InventoryCreateSchema,
    InventoryUpdateSchema,
    DispenseSchema,
    DispenseCreateSchema,
    DispenseUpdateSchema,
)
from .crud import DrugCRUD, InventoryCRUD, DispenseCRUD


class PharmacyService:
    """药房服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = DrugCRUD(Drug, auth=auth)
        self.inventory_crud = InventoryCRUD(Inventory, auth=auth)
        self.dispense_crud = DispenseCRUD(Dispense, auth=auth)

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

    # ── 药品 CRUD ──
    async def create(self, data: DrugCreateSchema) -> DrugSchema:
        drug = await self.crud.create(data)
        uid = self._user_id
        if uid and hasattr(drug, "created_by"):
            setattr(drug, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return await self._serialize_drug(drug)

    async def create_drug(self, drug_data: dict, creator_id: Optional[str] = None) -> DrugSchema:
        drug = await self.crud.create(drug_data)
        uid = creator_id or self._user_id
        if uid and hasattr(drug, "created_by"):
            setattr(drug, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return DrugSchema.model_validate(drug)

    async def get(self, id: str) -> DrugSchema:
        drug = await self.crud.get_or_404(id=id)
        return await self._serialize_drug(drug)

    async def get_drug(self, drug_id: str) -> DrugSchema:
        return await self.crud.get_or_404(id=drug_id, out_schema=DrugSchema)

    async def list(
        self,
        page_no: int,
        page_size: int,
        order_by=None,
        search: Optional[dict] = None,
    ) -> object:
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            out_schema=DrugSchema,
        )

    async def _serialize_drug(self, drug: Drug) -> DrugSchema:
        """序列化药品并附带供应商名称。"""
        d = DrugSchema.model_validate(drug).model_dump()
        if drug.supplier_id:
            from app.api.v1.module_inventory.model import Supplier
            sup = await self._db.get(Supplier, drug.supplier_id)
            d["supplier_name"] = sup.name if sup else None
        return DrugSchema.model_validate(d)

    async def list_drugs(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[DrugSchema], int]:
        """药品列表。

        category 兼容两种传值：分类ID（UUID，匹配 category_id）或旧的分类名字符串
        （匹配 category）；前端下拉传的是分类ID。
        """
        import uuid as _uuid
        from app.api.v1.module_inventory.model import Supplier

        stmt = (
            select(Drug, Supplier)
            .outerjoin(Supplier, Supplier.id == Drug.supplier_id)
            .where(Drug.deleted_at.is_(None))
        )
        if self._tenant_id is not None:
            stmt = stmt.where(Drug.tenant_id == self._tenant_id)
        if search:
            stmt = stmt.where(
                or_(
                    Drug.name.ilike(f"%{search}%"),
                    Drug.generic_name.ilike(f"%{search}%"),
                    Drug.drug_code.ilike(f"%{search}%"),
                )
            )
        if category:
            try:
                stmt = stmt.where(Drug.category_id == _uuid.UUID(str(category)))
            except (ValueError, AttributeError, TypeError):
                stmt = stmt.where(Drug.category == category)
        if status:
            stmt = stmt.where(Drug.status == status)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (await self._db.execute(stmt.offset(skip).limit(limit))).all()
        items = []
        for drug, sup in rows:
            d = DrugSchema.model_validate(drug).model_dump()
            d["supplier_name"] = sup.name if sup else None
            items.append(DrugSchema.model_validate(d))
        return items, int(total or 0)

    async def list_inventory(
        self,
        page_no: int = 1,
        page_size: int = 100,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
    ) -> dict:
        """库存列表：关联药品表与供应商，返回药品信息 + 库存数量等。"""
        from app.api.v1.module_inventory.model import Supplier
        stmt = (
            select(Inventory, Drug, Supplier)
            .join(Drug, Drug.id == Inventory.drug_id)
            .outerjoin(Supplier, Supplier.id == Drug.supplier_id)
            .where(Inventory.deleted_at.is_(None), Drug.deleted_at.is_(None))
        )
        if self._tenant_id is not None:
            stmt = stmt.where(Inventory.tenant_id == self._tenant_id)
        if keyword:
            stmt = stmt.where(
                or_(
                    Drug.name.ilike(f"%{keyword}%"),
                    Drug.generic_name.ilike(f"%{keyword}%"),
                    Drug.drug_code.ilike(f"%{keyword}%"),
                )
            )
        if category:
            stmt = stmt.where(Drug.category == category)

        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (
            await self._db.execute(stmt.offset((page_no - 1) * page_size).limit(page_size))
        ).all()

        items = []
        for inv, drug, sup in rows:
            items.append(
                {
                    "id": str(inv.id),
                    "drug_id": str(inv.drug_id),
                    "drug_code": drug.drug_code,
                    "drug_name": drug.name,
                    "generic_name": drug.generic_name,
                    "specification": drug.specification,
                    "unit": drug.unit,
                    "category": drug.category,
                    "manufacturer": drug.manufacturer,
                    "supplier_name": sup.name if sup else None,
                    "quantity": inv.quantity or 0,
                    "min_quantity": inv.min_quantity or 0,
                    "max_quantity": inv.max_quantity or 0,
                    "unit_price": float(inv.unit_price) if inv.unit_price is not None else 0.0,
                    "batch_no": inv.batch_no,
                    "expiry_date": inv.expiry_date,
                }
            )
        return {"items": items, "total": int(total or 0), "page": page_no, "page_size": page_size}

    async def update(self, id: str, data: DrugUpdateSchema) -> DrugSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return await self._serialize_drug(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 库存 ──
    async def _get_inventory(self, drug_id: str) -> Optional[Inventory]:
        stmt = select(Inventory).where(
            Inventory.drug_id == drug_id,
            Inventory.deleted_at.is_(None),
        )
        if self._tenant_id is not None:
            stmt = stmt.where(Inventory.tenant_id == self._tenant_id)
        return (await self._db.execute(stmt)).scalars().first()

    async def get_inventory(self, drug_id: str) -> InventorySchema:
        inv = await self._get_inventory(drug_id)
        if not inv:
            inv = Inventory(
                tenant_id=self._tenant_id,
                drug_id=drug_id,
                quantity=0,
                min_quantity=0,
                max_quantity=0,
            )
        return InventorySchema.model_validate(inv)

    async def update_inventory(
        self, drug_id: str, quantity_change: int, operator_id: Optional[str] = None
    ) -> InventorySchema:
        inv = await self._get_inventory(drug_id)
        if not inv:
            inv = Inventory(tenant_id=self._tenant_id, drug_id=drug_id, quantity=quantity_change)
        else:
            new_quantity = inv.quantity + quantity_change
            if new_quantity < 0:
                raise CustomException(msg="库存不足", code=400)
            inv.quantity = new_quantity
        self._db.add(inv)
        uid = operator_id or self._user_id
        if uid and hasattr(inv, "updated_by"):
            setattr(inv, "updated_by", uid)
        await self._db.flush()
        await self._db.commit()
        logger.info(f"更新库存: {drug_id}, 变化: {quantity_change} by {uid}")
        return InventorySchema.model_validate(inv)

    async def get_low_stock_drugs(self) -> list[InventorySchema]:
        stmt = select(Inventory).where(
            Inventory.quantity <= Inventory.min_quantity,
            Inventory.min_quantity > 0,
            Inventory.deleted_at.is_(None),
        )
        if self._tenant_id is not None:
            stmt = stmt.where(Inventory.tenant_id == self._tenant_id)
        rows = (await self._db.execute(stmt)).scalars().all()
        return [InventorySchema.model_validate(r) for r in rows]

    async def get_inventory_warnings(self) -> dict:
        warning_days = 30
        today = date.today()

        low_stmt = select(Inventory).where(
            Inventory.quantity <= Inventory.min_quantity,
            Inventory.min_quantity > 0,
            Inventory.deleted_at.is_(None),
        )
        if self._tenant_id is not None:
            low_stmt = low_stmt.where(Inventory.tenant_id == self._tenant_id)
        low_rows = (await self._db.execute(low_stmt)).scalars().all()
        low_stock_list = []
        for inv in low_rows:
            drug = await self._get_drug(inv.drug_id)
            if drug:
                low_stock_list.append(
                    {
                        "drug_id": str(inv.drug_id),
                        "drug_code": drug.drug_code,
                        "drug_name": drug.name,
                        "specification": drug.specification,
                        "current_quantity": inv.quantity,
                        "min_quantity": inv.min_quantity,
                        "unit": drug.unit or "",
                    }
                )

        all_stmt = select(Inventory).where(Inventory.deleted_at.is_(None))
        if self._tenant_id is not None:
            all_stmt = all_stmt.where(Inventory.tenant_id == self._tenant_id)
        all_rows = (await self._db.execute(all_stmt)).scalars().all()

        expired_list, expiring_soon_list = [], []
        for inv in all_rows:
            expiry = getattr(inv, "expiry_date", None)
            if not expiry:
                continue
            try:
                if isinstance(expiry, str):
                    expiry = date.fromisoformat(expiry)
                drug = await self._get_drug(inv.drug_id)
                if not drug:
                    continue
                drug_info = {
                    "drug_id": str(inv.drug_id),
                    "drug_code": drug.drug_code,
                    "drug_name": drug.name,
                    "specification": drug.specification,
                    "current_quantity": inv.quantity,
                    "expiry_date": expiry.isoformat(),
                    "unit": drug.unit or "",
                }
                if expiry < today:
                    expired_list.append(drug_info)
                elif expiry <= today + timedelta(days=warning_days):
                    drug_info["days_until_expiry"] = (expiry - today).days
                    expiring_soon_list.append(drug_info)
            except Exception as e:  # pragma: no cover
                logger.warning(f"处理库存过期日期失败: drug_id={inv.drug_id}, error={e!s}")
                continue

        return {"low_stock": low_stock_list, "expired": expired_list, "expiring_soon": expiring_soon_list}

    async def _get_drug(self, drug_id: str) -> Optional[Drug]:
        return await self.crud.get(id=drug_id)

    async def get_inventories_by_drug_ids(self, drug_ids: list[str]) -> dict:
        if not drug_ids:
            return {}
        stmt = select(Inventory).where(
            Inventory.drug_id.in_(drug_ids), Inventory.deleted_at.is_(None)
        )
        if self._tenant_id is not None:
            stmt = stmt.where(Inventory.tenant_id == self._tenant_id)
        rows = (await self._db.execute(stmt)).scalars().all()
        return {str(inv.drug_id): inv for inv in rows}

    # ── 发药 ──
    async def _is_pharmacist_review_enabled(self) -> bool:
        if self._tenant_id is None:
            return True
        tenant = (
            await self._db.execute(select(Tenant).where(Tenant.id == self._tenant_id))
        ).scalars().first()
        if not tenant:
            return True
        return bool(getattr(tenant, "pharmacist_review_enabled", True))

    async def dispense_prescription(
        self,
        prescription_id: str,
        dispense_items: list[dict],
        operator_id: Optional[str] = None,
    ) -> list[DispenseSchema]:
        pharmacist_review_enabled = await self._is_pharmacist_review_enabled()
        if not pharmacist_review_enabled:
            logger.info(f"药师审核已关闭，用药禁忌自动审核通过 - 租户: {self._tenant_id}")

        # 前置校验：处方必须先完成收费（status=paid）方可发药；旧数据无账单(bill_id 为空) 兼容直接发药
        try:
            from app.api.v1.module_treatment.model import Prescription
            pres = (
                await self._db.execute(
                    select(Prescription).where(Prescription.id == prescription_id)
                )
            ).scalars().first()
            if pres is not None:
                if pres.bill_id is not None and pres.status != "paid":
                    raise CustomException(
                        msg="处方尚未收费，不能发药，请先在收费管理完成收费",
                        code=400,
                        status_code=400,
                    )
                if pres.status == "dispensed":
                    raise CustomException(msg="处方已发药，不能重复发药", code=400, status_code=400)
        except CustomException:
            raise
        except Exception as e:  # pragma: no cover
            logger.warning(f"发药前置校验失败: {e!s}", exc_info=True)

        # 前端未传明细(items 为空)时，从处方自身 items 推导发药明细，
        # 否则循环不执行会导致处方状态无法更新为已发药。
        if not dispense_items and pres is not None and pres.items:
            raw_items = pres.items
            if isinstance(raw_items, dict):
                dispense_items = [
                    {"drug_id": str(did), "quantity": int(it.get("quantity") or it.get("qty") or 1)}
                    for did, it in raw_items.items()
                    if it
                ]
            elif isinstance(raw_items, list):
                dispense_items = [
                    {
                        "drug_id": str(it.get("drug_id") or it.get("drugId")),
                        "quantity": int(it.get("quantity") or it.get("qty") or 1),
                    }
                    for it in raw_items
                    if isinstance(it, dict) and (it.get("drug_id") or it.get("drugId"))
                ]

        records: list[Dispense] = []
        if not dispense_items:
            # 前端未传明细且处方自身也无法推导出药品时，明确报错，
            # 避免返回空列表的“假成功”导致处方状态不更新
            raise CustomException(
                msg="没有可发药的药品明细（处方明细缺少药品ID）",
                code=400,
                status_code=400,
            )
        for item in dispense_items:
            drug_id = item["drug_id"]
            quantity = item["quantity"]

            inv = await self._get_inventory(drug_id)
            if not inv or inv.quantity < quantity:
                raise CustomException(msg=f"药品库存不足: {drug_id}", code=400)

            drug = await self._get_drug(drug_id)
            unit_price = Decimal(str(drug.price)) if drug and drug.price else Decimal("0")
            total_amount = unit_price * Decimal(str(quantity))

            dispense_data = {
                "prescription_id": prescription_id,
                "drug_id": drug_id,
                "quantity": quantity,
                "unit_price": float(unit_price),
                "total_amount": float(total_amount),
                "status": "dispensed" if not pharmacist_review_enabled else "pending",
            }
            if not pharmacist_review_enabled:
                dispense_data["remark"] = "用药禁忌自动审核通过（药师审核已关闭）"

            dispense = await self.dispense_crud.create(dispense_data)
            uid = operator_id or self._user_id
            if uid and hasattr(dispense, "created_by"):
                setattr(dispense, "created_by", uid)
                await self._db.flush()
            records.append(dispense)

            # 出库
            await self.update_inventory(drug_id, -quantity, operator_id=uid)

        if records:
            try:
                from app.api.v1.module_treatment.service import TreatmentService

                treatment_service = TreatmentService(self.auth)
                await treatment_service.update_prescription(
                    prescription_id, {"status": "dispensed"}, updater_id=operator_id or self._user_id
                )
                logger.info(f"处方状态已更新为已发药: {prescription_id}")
            except Exception as e:  # pragma: no cover
                logger.warning(f"更新处方状态失败: {e!s}，但发药记录已创建")

        await self._db.commit()
        logger.info(
            f"发药: {prescription_id} by {operator_id or self._user_id}, "
            f"药师审核: {'开启' if pharmacist_review_enabled else '关闭'}"
        )
        return [DispenseSchema.model_validate(r) for r in records]

    async def list_dispenses(
        self,
        prescription_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[DispenseSchema], int]:
        stmt = select(Dispense).where(Dispense.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(Dispense.tenant_id == self._tenant_id)
        if prescription_id:
            stmt = stmt.where(Dispense.prescription_id == prescription_id)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (
            await self._db.execute(
                stmt.order_by(Dispense.created_at.desc()).offset(skip).limit(limit)
            )
        ).scalars().all()
        return [DispenseSchema.model_validate(r) for r in rows], int(total or 0)

    # ── 药品调价 ──
    async def list_price_adjustments(
        self, skip: int = 0, limit: int = 10, status: Optional[str] = None
    ) -> dict:
        stmt = select(PriceAdjustment).where(PriceAdjustment.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(PriceAdjustment.tenant_id == self._tenant_id)
        if status:
            stmt = stmt.where(PriceAdjustment.status == status)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (
            await self._db.execute(
                stmt.order_by(PriceAdjustment.created_at.desc()).offset(skip).limit(limit)
            )
        ).scalars().all()
        return {
            "items": [PriceAdjustmentSchema.model_validate(r).model_dump() for r in rows],
            "pagination": {
                "page": skip // limit + 1 if limit else 1,
                "page_size": limit,
                "total": int(total or 0),
                "pages": (int(total or 0) + limit - 1) // limit if limit else 1,
            },
        }

    async def get_price_adjustment(self, id: str) -> PriceAdjustmentSchema:
        pa = await self.crud.get_or_404(id=id, model=PriceAdjustment)
        return PriceAdjustmentSchema.model_validate(pa)

    async def create_price_adjustment(self, data: dict) -> PriceAdjustmentSchema:
        items = data.get("items") or []
        if not items:
            raise CustomException(msg="调价明细不能为空", code=400)
        today = date.today().isoformat()
        pa = PriceAdjustment(
            tenant_id=self._tenant_id,
            adjustment_no=f"PA{date.today().strftime('%Y%m%d')}{str(abs(hash(id)))[-4:]}",
            adjust_date=data.get("adjust_date") or today,
            status="draft",
            remark=data.get("remark"),
        )
        self._db.add(pa)
        await self._db.flush()
        for it in items:
            drug = await self._get_drug(it["drug_id"])
            self._db.add(
                PriceAdjustmentItem(
                    tenant_id=self._tenant_id,
                    adjustment_id=pa.id,
                    drug_id=it["drug_id"],
                    drug_name=drug.name if drug else None,
                    old_price=drug.price if drug else 0,
                    new_price=it["new_price"],
                    reason=it.get("reason"),
                )
            )
        uid = self._user_id
        if uid and hasattr(pa, "created_by"):
            setattr(pa, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return PriceAdjustmentSchema.model_validate(pa)

    async def approve_price_adjustment(self, id: str) -> PriceAdjustmentSchema:
        pa = await self.crud.get_or_404(id=id, model=PriceAdjustment)
        if pa.status == "approved":
            raise CustomException(msg="调价单已审批，不能重复审批", code=400)
        # 更新每个药品的系统售价
        items = (
            await self._db.execute(
                select(PriceAdjustmentItem).where(PriceAdjustmentItem.adjustment_id == pa.id)
            )
        ).scalars().all()
        for it in items:
            drug = await self._get_drug(str(it.drug_id))
            if drug:
                drug.price = it.new_price
                self._db.add(drug)
        pa.status = "approved"
        uid = self._user_id
        if uid and hasattr(pa, "updated_by"):
            setattr(pa, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return PriceAdjustmentSchema.model_validate(pa)

    async def delete_price_adjustment(self, id: str) -> None:
        pa = await self.crud.get_or_404(id=id, model=PriceAdjustment)
        if pa.status == "approved":
            raise CustomException(msg="已审批的调价单不能删除", code=400)
        await self.crud.delete([id], model=PriceAdjustment)
