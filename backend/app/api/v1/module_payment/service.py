"""
收费服务（对齐旧 services/payment_service.py + repositories/payment_repository.py，迁移为异步 + CRUDBase，Python 3.12+）

业务规则：
- 账单号自动生成（BILL + 8位）
- 账单含 items 时按明细汇总 total_amount
- 支付：创建支付记录、累加 paid_amount、满额置 paid 并同步挂号支付状态
- 退费：回退 paid_amount、同步挂号支付状态
"""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.api.v1.module_payment.model import Bill, Payment
from app.api.v1.module_registration.model import Registration
from app.utils.common import generate_id

from .model import Bill as BillModel, Payment as PaymentModel
from .schema import (
    BillSchema,
    BillCreateSchema,
    BillUpdateSchema,
    PaymentSchema,
    PaymentCreateSchema,
    PaymentUpdateSchema,
)
from .crud import BillCRUD, PaymentCRUD


class PaymentService:
    """收费服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = BillCRUD(BillModel, auth=auth)
        self.payment_crud = PaymentCRUD(PaymentModel, auth=auth)

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

    # ── 纯计算 ──
    def calculate_bill_amount(
        self,
        registration_price: Decimal = Decimal("0"),
        treatment_price: Decimal = Decimal("0"),
        pharmacy_price: Decimal = Decimal("0"),
        discount: Decimal = Decimal("0"),
        insurance_amount: Decimal = Decimal("0"),
    ) -> dict:
        """计算账单金额（无 DB 操作）"""
        total_amount = registration_price + treatment_price + pharmacy_price
        actual_amount = total_amount - discount - insurance_amount
        return {
            "total_amount": float(total_amount),
            "discount_amount": float(discount),
            "insurance_amount": float(insurance_amount),
            "actual_amount": float(actual_amount) if actual_amount > 0 else 0.0,
        }

    # ── 标准 CRUD（primary: Bill）──
    async def create(self, data: BillCreateSchema) -> BillSchema:
        bill = await self._create_bill(data.model_dump(exclude_unset=True))
        return BillSchema.model_validate(bill)

    async def _create_bill(self, bill_data: dict) -> Bill:
        bill_data.setdefault("bill_no", f"BILL{generate_id()[:8].upper()}")
        if bill_data.get("items"):
            total = Decimal("0")
            for item in bill_data["items"]:
                total += Decimal(str(item.get("amount", 0)))
            bill_data["total_amount"] = total
        bill = await self.crud.create(bill_data)
        uid = self._user_id
        if uid and hasattr(bill, "created_by"):
            setattr(bill, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        logger.info(f"创建账单: {bill.id} by {uid}")
        return bill

    async def create_bill(self, bill_data: dict, creator_id: Optional[str] = None) -> BillSchema:
        bill = await self._create_bill(bill_data)
        return BillSchema.model_validate(bill)

    async def get(self, id: str) -> dict:
        obj = await self.crud.get_or_404(id=id, preload=["patient", "registration"])
        return self._bill_dict(obj)

    async def get_bill(self, bill_id: str) -> dict:
        obj = await self.crud.get_or_404(id=bill_id, preload=["patient", "registration"])
        return self._bill_dict(obj)

    def _bill_dict(self, bill) -> dict:
        """将账单 ORM 转为富化字典（补全展示字段）

        BillSchema 未声明 patient 关联字段，直接 model_validate 会丢失
        patient_name。这里在已预加载 patient 基础上手工补齐。
        """
        data = BillSchema.model_validate(bill).model_dump()
        patient = getattr(bill, "patient", None)
        patient_name = ""
        if patient:
            patient_name = patient.name or ""
        data["patient_name"] = patient_name
        return data

    async def list(
        self,
        page_no: int,
        page_size: int,
        order_by=None,
        search: Optional[dict] = None,
    ) -> object:
        result = await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            preload=["patient", "registration"],
        )
        result.items = [self._bill_dict(obj) for obj in result.items]
        return result

    async def list_bills(
        self,
        patient_id: Optional[str] = None,
        registration_id: Optional[str] = None,
        status: Optional[str] = None,
        bill_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[BillSchema], int]:
        stmt = (
            select(Bill)
            .options(joinedload(Bill.patient), joinedload(Bill.registration))
            .where(Bill.deleted_at.is_(None))
        )
        if self._tenant_id is not None:
            stmt = stmt.where(Bill.tenant_id == self._tenant_id)
        if patient_id:
            stmt = stmt.where(Bill.patient_id == patient_id)
        if registration_id:
            stmt = stmt.where(Bill.registration_id == registration_id)
        if status:
            stmt = stmt.where(Bill.status == status)
        if bill_type:
            stmt = stmt.where(Bill.bill_type == bill_type)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (
            await self._db.execute(
                stmt.order_by(Bill.created_at.desc()).offset(skip).limit(limit)
            )
        ).scalars().all()
        return [BillSchema.model_validate(r) for r in rows], int(total or 0)

    async def update(self, id: str, data: BillUpdateSchema) -> BillSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        await self._db.refresh(obj)
        return BillSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 支付 / 退费 ──
    async def pay_bill(
        self,
        bill_id: str,
        payment_method: str,
        amount,
        transaction_id: Optional[str] = None,
        use_balance: bool = False,
        use_points: int = 0,
    ) -> PaymentSchema:
        bill = await self.crud.get(id=bill_id)
        if not bill:
            raise CustomException(msg="账单不存在", code=404, status_code=404)
        if bill.status == "paid":
            raise CustomException(msg="账单已支付", code=400, status_code=400)

        total = float(bill.total_amount or 0)
        insurance = float(bill.insurance_amount or 0)
        already_paid = float(bill.paid_amount or 0)
        remaining = round(total - insurance - already_paid, 2)
        if remaining <= 0:
            raise CustomException(msg="账单无需支付", code=400, status_code=400)

        # 读取会员积分配置（抵扣比例 / 赠送规则）
        loyalty = {}
        try:
            from app.api.v1.module_tenant.service import TenantService
            cfg = await TenantService(self.auth).get_tenant_config(self.auth.tenant_id)
            loyalty = (cfg or {}).get("loyalty", {}) or {}
        except Exception as e:
            logger.warning(f"读取会员积分配置失败: {e!s}")

        use_balance = bool(use_balance)
        use_points = int(use_points or 0)
        balance_deduction = 0.0
        points_used = 0
        points_money = 0.0
        patient = None
        if (use_balance or use_points) and bill.patient_id:
            from app.api.v1.module_patient.model import Patient
            from uuid import UUID
            patient = await self._db.get(Patient, UUID(str(bill.patient_id)))

        # 余额抵扣
        if use_balance and patient is not None:
            balance_deduction = min(float(patient.balance or 0), remaining)
            remaining = round(remaining - balance_deduction, 2)
        # 积分抵扣
        points_to_yuan = float(loyalty.get("points_to_yuan", 0) or 0)
        if use_points and points_to_yuan > 0 and patient is not None:
            max_points_money = min(remaining, use_points / points_to_yuan)
            max_by_points = int(patient.points or 0)
            points_used = min(int(max_points_money * points_to_yuan), max_by_points, use_points)
            points_money = round(points_used / points_to_yuan, 2)
            remaining = round(remaining - points_money, 2)

        amount = Decimal(str(amount or 0))
        if amount < Decimal(str(round(remaining, 2))):
            raise CustomException(msg=f"收款金额不足（还需 ¥{remaining:.2f}）", code=400, status_code=400)

        payment = await self.payment_crud.create(
            {
                "payment_no": f"PAY{generate_id()[:8].upper()}",
                "bill_id": bill.id,
                "patient_id": bill.patient_id,
                "payment_method": payment_method,
                "amount": float(amount),
                "status": "success",
                "transaction_id": transaction_id,
            }
        )

        bill.paid_amount += amount
        bill.balance_deduction = round(balance_deduction, 2)
        bill.points_deduction = points_used
        total_covered = bill.paid_amount + Decimal(str(balance_deduction)) + Decimal(str(points_money))
        if total_covered >= (bill.total_amount - bill.insurance_amount - Decimal("0.001")):
            bill.status = "paid"
            bill.payment_method = payment_method
            bill.payment_time = datetime.now()

        # 扣除患者余额/积分
        if patient is not None:
            if balance_deduction > 0:
                patient.balance = round(float(patient.balance or 0) - balance_deduction, 2)
            if points_used > 0:
                patient.points = max(0, (patient.points or 0) - points_used)

        # 消费赠送积分（按消费金额累计，消费金额=总额-医保）
        points_per_yuan = float(loyalty.get("points_per_yuan", 0) or 0)
        consumption_amount = round(total - insurance, 2)
        if points_per_yuan > 0 and patient is not None and consumption_amount > 0 and bill.status == "paid":
            earned = int(consumption_amount * points_per_yuan)
            if earned > 0:
                patient.points = (patient.points or 0) + earned

        await self._db.flush()

        # 收费完成后，累计会员消费并自动晋升等级（consumption_total 由该方法累加）
        if bill.status == "paid" and bill.patient_id:
            try:
                from app.api.v1.module_member.service import MemberLevelService
                await MemberLevelService(self.auth).check_and_upgrade(bill.patient_id, consumption_amount)
            except Exception as e:  # pragma: no cover
                logger.warning(f"会员等级自动晋升失败（可忽略）: {e!s}", exc_info=True)

        # 处方类账单收费完成后，同步处方状态为已收费（paid），方可发药
        if bill.bill_type == "prescription" and bill.prescription_id:
            try:
                from app.api.v1.module_treatment.model import Prescription
                pres = (
                    await self._db.execute(
                        select(Prescription).where(Prescription.id == bill.prescription_id)
                    )
                ).scalars().first()
                if pres and pres.status == "pending":
                    pres.status = "paid"
                    await self._db.flush()
                    logger.info(f"处方 {pres.id} 收费完成，状态置为已收费")
            except Exception as e:  # pragma: no cover
                logger.warning(f"同步处方收费状态失败: {e!s}", exc_info=True)

        # 同步挂号支付状态
        if bill.bill_type == "registration" and bill.registration_id:
            reg = (
                await self._db.execute(
                    select(Registration).where(Registration.id == bill.registration_id)
                )
            ).scalars().first()
            if reg:
                reg.paid_amount = bill.paid_amount
                reg.payment_status = (
                    "paid"
                    if bill.paid_amount >= (bill.total_amount - bill.insurance_amount)
                    else "partial"
                )
                await self._db.flush()
                logger.info(f"同步更新挂号支付状态: {reg.id}, 金额: {bill.paid_amount}")

        await self._db.commit()
        await self._db.refresh(payment)
        logger.info(f"支付账单: {bill_id}, 金额: {amount}")
        return PaymentSchema.model_validate(payment)

    async def refund_bill(
        self,
        bill_id: str,
        refund_amount,
        reason: Optional[str] = None,
    ) -> BillSchema:
        bill = await self.crud.get(id=bill_id)
        if not bill:
            raise CustomException(msg="账单不存在", code=404, status_code=404)
        if bill.status != "paid":
            raise CustomException(msg="只有已支付账单可以退费", code=400, status_code=400)
        if Decimal(str(refund_amount)) > bill.paid_amount:
            raise CustomException(msg="退费金额不能超过已支付金额", code=400, status_code=400)

        bill.paid_amount -= Decimal(str(refund_amount))
        if bill.paid_amount == 0:
            bill.status = "refunded"
        else:
            bill.status = "partial_refunded"

        if bill.bill_type == "registration" and bill.registration_id:
            reg = (
                await self._db.execute(
                    select(Registration).where(Registration.id == bill.registration_id)
                )
            ).scalars().first()
            if reg:
                reg.paid_amount = bill.paid_amount
                reg.payment_status = "refunded" if bill.paid_amount <= 0 else "partial"
                await self._db.flush()
                logger.info(f"同步更新挂号退费状态: {reg.id}, 金额: {bill.paid_amount}")

        if reason:
            bill.remark = f"{bill.remark or ''}\n退费原因: {reason}"

        await self._db.commit()
        # commit 后对象属性会过期，异步会话下 model_validate 触发 lazy load 会抛 MissingGreenlet；
        # 先在 async 上下文内 refresh 重新加载属性，再序列化。
        await self._db.refresh(bill)
        logger.info(f"退费账单: {bill_id}, 金额: {refund_amount}")
        return BillSchema.model_validate(bill)

    async def list_payments(
        self,
        bill_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[PaymentSchema], int]:
        stmt = select(Payment).where(Payment.deleted_at.is_(None))
        if self._tenant_id is not None:
            stmt = stmt.where(Payment.tenant_id == self._tenant_id)
        if bill_id:
            stmt = stmt.where(Payment.bill_id == bill_id)
        if patient_id:
            stmt = stmt.where(Payment.patient_id == patient_id)
        if status:
            stmt = stmt.where(Payment.status == status)
        total = await self._db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = (
            await self._db.execute(
                stmt.order_by(Payment.created_at.desc()).offset(skip).limit(limit)
            )
        ).scalars().all()
        return [PaymentSchema.model_validate(r) for r in rows], int(total or 0)
