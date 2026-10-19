"""
会员模块 Service
"""
import math
from typing import Optional
from sqlalchemy import func, select
from app.core.base_crud import CRUDBase
from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from .model import MemberLevel
from .schema import MemberLevelSchema, MemberLevelCreateSchema, MemberLevelUpdateSchema
from app.api.v1.module_patient.model import Patient


class MemberLevelService:
    """会员等级业务逻辑"""

    def __init__(self, auth: AuthSchema):
        self.auth = auth
        self.db = auth.db
        self.crud = CRUDBase(MemberLevel, auth, auth.db)

    async def list_levels(self, page: int, page_size: int, keyword: Optional[str] = None, status: Optional[str] = None):
        search = {}
        if keyword:
            search["name"] = ("like", keyword)
        if status:
            search["status"] = status
        result = await self.crud.page(
            offset=(page - 1) * page_size,
            limit=page_size,
            order_by=[{"sort": "asc"}, {"created_at": "desc"}],
            search=search,
            out_schema=MemberLevelSchema,
        )
        # 填充各等级会员数量
        for item in result.items:
            item["member_count"] = await self._count_members(item["id"])
        return result

    async def get_default(self) -> Optional[MemberLevel]:
        return await self.crud.get(order_by=[{"is_default": "desc"}, {"sort": "asc"}], search={"is_default": True}) or \
            await self.crud.get(order_by=[{"sort": "asc"}], search={"status": "active"})

    async def create(self, data: MemberLevelCreateSchema):
        payload = data.model_dump()
        if payload.get("is_default"):
            await self._clear_default()
        obj = await self.crud.create(payload)
        return MemberLevelSchema.model_validate(obj).model_dump()

    async def update(self, level_id, data: MemberLevelUpdateSchema):
        payload = data.model_dump(exclude_unset=True)
        if payload.get("is_default"):
            await self._clear_default(except_id=level_id)
        obj = await self.crud.update(level_id, payload)
        return MemberLevelSchema.model_validate(obj).model_dump()

    async def delete(self, level_ids: list):
        # 默认等级不允许删除
        for lid in level_ids:
            lvl = await self.crud.get_by_id(lid)
            if lvl and lvl.is_default:
                raise CustomException(msg="默认会员等级不可删除")
        await self.crud.delete(level_ids)
        return True

    async def _clear_default(self, except_id=None):
        from sqlalchemy import update as sa_update
        stmt = sa_update(MemberLevel).where(MemberLevel.is_default.is_(True))
        if except_id:
            stmt = stmt.where(MemberLevel.id != except_id)
        await self.db.execute(stmt.values(is_default=False))
        await self.db.flush()

    async def _count_members(self, level_id) -> int:
        try:
            conditions = [
                Patient.member_level_id == level_id,
                Patient.deleted_at.is_(None),
            ]
            if self.auth and self.auth.tenant_id is not None:
                conditions.append(Patient.tenant_id == self.auth.tenant_id)
            stmt = select(func.count()).select_from(Patient).where(*conditions)
            res = await self.db.execute(stmt)
            return res.scalar() or 0
        except Exception:
            return 0

    async def check_and_upgrade(self, patient_id, added_amount: float = 0):
        """消费后累计金额并自动晋升到满足条件的等级（按 upgrade_threshold 从高到低取第一个满足的）"""
        patient = (await self.db.execute(
            select(Patient).where(Patient.id == patient_id, Patient.deleted_at.is_(None))
        )).scalars().first()
        if not patient:
            return
        patient.consumption_total = (patient.consumption_total or 0) + added_amount
        # 取所有启用等级，按阈值降序，命中第一个 <= 累计消费的
        levels = (await self.db.execute(
            select(MemberLevel).where(
                MemberLevel.status == "active",
                MemberLevel.deleted_at.is_(None),
            ).order_by(MemberLevel.upgrade_threshold.desc())
        )).scalars().all()
        target = None
        for lvl in levels:
            if patient.consumption_total >= (lvl.upgrade_threshold or 0):
                target = lvl
                break
        if target and (str(patient.member_level_id) != str(target.id)):
            patient.member_level_id = target.id
        await self.db.flush()
        await self.db.commit()


from app.api.v1.module_patient.model import Patient
from .model import MemberTransaction
from .schema import (
    MemberSchema, MemberTransactionSchema,
    MemberRechargeSchema, MemberRefundSchema, MemberPointsSchema, MemberLevelSetSchema,
)


class MemberService:
    """会员（患者）资产与等级管理"""

    def __init__(self, auth: AuthSchema):
        self.auth = auth
        self.db = auth.db

    def _tenant_cond(self):
        conds = [Patient.deleted_at.is_(None)]
        if self.auth and self.auth.tenant_id is not None:
            conds.append(Patient.tenant_id == self.auth.tenant_id)
        return conds

    async def list_members(self, page=1, page_size=10, keyword=None, level_id=None, status=None, member_type=None):
        from sqlalchemy import func, select
        from .model import MemberLevel
        offset = (page - 1) * page_size
        conds = self._tenant_cond()
        if keyword:
            conds.append(
                (Patient.name.like(f"%{keyword}%")) |
                (Patient.phone.like(f"%{keyword}%")) |
                (Patient.patient_no.like(f"%{keyword}%"))
            )
        if level_id:
            conds.append(Patient.member_level_id == str(level_id))
        if status:
            conds.append(Patient.member_status == status)
        # member_type: paid=付费会员(有等级且非默认), free=免费/未设等级
        if member_type == "paid":
            conds.append(Patient.member_level_id.isnot(None))
        elif member_type == "free":
            conds.append(Patient.member_level_id.is_(None))

        from sqlalchemy.orm import joinedload
        stmt = (
            select(Patient)
            .options(joinedload(Patient.member_level))
            .where(*conds)
            .order_by(Patient.created_at.desc())
        )
        total_stmt = select(func.count()).select_from(Patient).where(*conds)
        total = (await self.db.execute(total_stmt)).scalar() or 0
        rows = (await self.db.execute(stmt.offset(offset).limit(page_size))).scalars().all()

        items = []
        for p in rows:
            data = MemberSchema(
                id=str(p.id),
                patient_no=p.patient_no,
                name=p.name,
                gender=p.gender,
                phone=p.phone,
                member_level_id=str(p.member_level_id) if p.member_level_id else None,
                member_level_name=p.member_level.name if p.member_level else None,
                balance=float(p.balance or 0),
                points=int(p.points or 0),
                consumption_total=float(p.consumption_total or 0),
                stored_total=float(p.stored_total or 0),
                gift_total=float(p.gift_total or 0),
                member_status=p.member_status or "active",
                expire_date=p.expire_date.isoformat() if p.expire_date else None,
                created_at=p.created_at.isoformat() if p.created_at else None,
            ).model_dump()
            items.append(data)
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": math.ceil(total / page_size) if page_size else 0,
            },
        }

    async def _write_txn(self, patient, type_, amount=0, points=0, remark=None, operator_id=None, level_id=None):
        from sqlalchemy import select
        before_balance = float(patient.balance or 0)
        before_points = int(patient.points or 0)
        txn = MemberTransaction(
            tenant_id=self.auth.tenant_id,
            patient_id=str(patient.id),
            member_level_id=level_id,
            type=type_,
            amount=amount,
            points=points,
            before_balance=before_balance,
            after_balance=before_balance + amount,
            before_points=before_points,
            after_points=before_points + points,
            operator_id=operator_id,
            remark=remark,
        )
        self.db.add(txn)
        await self.db.flush()

    async def recharge(self, patient_id, data: MemberRechargeSchema):
        patient = await self._get_patient(patient_id)
        amount = float(data.amount)
        # 读取赠送比例
        bonus_ratio = 0
        gift = 0
        try:
            from app.api.v1.module_tenant.service import TenantService
            cfg = await TenantService(self.auth).get_tenant_config(self.auth.tenant_id)
            loyalty = (cfg or {}).get("loyalty", {}) or {}
            bonus_ratio = float(loyalty.get("recharge_bonus_ratio", 0) or 0)
        except Exception:
            pass
        gift = round(amount * bonus_ratio, 2)
        patient.balance = round(float(patient.balance or 0) + amount + gift, 2)
        patient.stored_total = round(float(patient.stored_total or 0) + amount, 2)
        patient.gift_total = round(float(patient.gift_total or 0) + gift, 2)
        if patient.member_status != "active":
            patient.member_status = "active"
        await self._write_txn(patient, "recharge", amount=amount, remark=data.remark, operator_id=str(self.auth.user.id))
        await self.db.commit()
        return await self._serialize(patient)

    async def refund(self, patient_id, data: MemberRefundSchema):
        patient = await self._get_patient(patient_id)
        amount = float(data.amount)
        if amount > float(patient.balance or 0):
            raise CustomException(msg="退款金额不能大于账户余额", code=400, status_code=400)
        patient.balance = round(float(patient.balance or 0) - amount, 2)
        if patient.balance <= 0:
            patient.member_status = "inactive"
        await self._write_txn(patient, "refund", amount=-amount, remark=data.remark, operator_id=str(self.auth.user.id))
        await self.db.commit()
        return await self._serialize(patient)

    async def adjust_points(self, patient_id, data: MemberPointsSchema):
        patient = await self._get_patient(patient_id)
        pts = int(data.points)
        patient.points = int(patient.points or 0) + pts
        if patient.points < 0:
            patient.points = 0
        await self._write_txn(patient, "points_add" if pts >= 0 else "points_deduct",
                              points=pts, remark=data.remark, operator_id=str(self.auth.user.id))
        await self.db.commit()
        return await self._serialize(patient)

    async def set_level(self, patient_id, data: MemberLevelSetSchema):
        patient = await self._get_patient(patient_id)
        from .model import MemberLevel
        lvl = (await self.db.execute(
            select(MemberLevel).where(MemberLevel.id == data.member_level_id, MemberLevel.deleted_at.is_(None))
        )).scalars().first()
        if not lvl:
            raise CustomException(msg="会员等级不存在", code=404, status_code=404)
        old_level = patient.member_level_id
        patient.member_level_id = lvl.id
        patient.member_status = "active"
        await self._write_txn(patient, "level_change", remark=data.remark or f"等级变更: {old_level} -> {lvl.id}",
                              operator_id=str(self.auth.user.id), level_id=str(lvl.id))
        await self.db.commit()
        return await self._serialize(patient)

    async def get_transactions(self, patient_id, page=1, page_size=20, type_=None):
        from sqlalchemy import func, select
        offset = (page - 1) * page_size
        conds = [MemberTransaction.patient_id == str(patient_id)]
        if type_:
            conds.append(MemberTransaction.type == type_)
        total_stmt = select(func.count()).select_from(MemberTransaction).where(*conds)
        total = (await self.db.execute(total_stmt)).scalar() or 0
        stmt = (
            select(MemberTransaction)
            .where(*conds)
            .order_by(MemberTransaction.created_at.desc())
            .offset(offset).limit(page_size)
        )
        rows = (await self.db.execute(stmt)).scalars().all()
        items = []
        for t in rows:
            items.append(MemberTransactionSchema(
                id=str(t.id),
                patient_id=str(t.patient_id),
                type=t.type,
                amount=float(t.amount or 0),
                points=int(t.points or 0),
                before_balance=float(t.before_balance or 0),
                after_balance=float(t.after_balance or 0),
                before_points=int(t.before_points or 0),
                after_points=int(t.after_points or 0),
                operator_id=str(t.operator_id) if t.operator_id else None,
                remark=t.remark,
                created_at=t.created_at.isoformat() if t.created_at else None,
            ).model_dump())
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": math.ceil(total / page_size) if page_size else 0,
            },
        }

    async def _get_patient(self, patient_id):
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        stmt = select(Patient).options(joinedload(Patient.member_level)).where(
            Patient.id == patient_id, Patient.deleted_at.is_(None)
        )
        patient = (await self.db.execute(stmt)).scalars().first()
        if not patient:
            raise CustomException(msg="患者不存在", code=404, status_code=404)
        return patient

    async def _serialize(self, patient):
        return MemberSchema(
            id=str(patient.id),
            patient_no=patient.patient_no,
            name=patient.name,
            gender=patient.gender,
            phone=patient.phone,
            member_level_id=str(patient.member_level_id) if patient.member_level_id else None,
            member_level_name=patient.member_level.name if patient.member_level else None,
            balance=float(patient.balance or 0),
            points=int(patient.points or 0),
            consumption_total=float(patient.consumption_total or 0),
            stored_total=float(patient.stored_total or 0),
            gift_total=float(patient.gift_total or 0),
            member_status=patient.member_status or "active",
            expire_date=patient.expire_date.isoformat() if patient.expire_date else None,
            created_at=patient.created_at.isoformat() if patient.created_at else None,
        ).model_dump()

    async def update_member(self, patient_id, data: "MemberUpdateSchema"):
        patient = await self._get_patient(patient_id)
        payload = data.model_dump(exclude_unset=True)
        from datetime import date, datetime
        # 会员等级变更
        new_level = payload.get("member_level_id")
        if "member_level_id" in payload:
            if new_level:  # 非空=设置等级
                from .model import MemberLevel
                lvl = (await self.db.execute(
                    select(MemberLevel).where(MemberLevel.id == new_level, MemberLevel.deleted_at.is_(None))
                )).scalars().first()
                if not lvl:
                    raise CustomException(msg="会员等级不存在", code=404, status_code=404)
                patient.member_level_id = lvl.id
            else:  # 空字符串=清除等级
                patient.member_level_id = None
        if "name" in payload and payload["name"] is not None:
            patient.name = payload["name"]
        if "gender" in payload and payload["gender"] is not None:
            patient.gender = payload["gender"]
        if "phone" in payload and payload["phone"] is not None:
            patient.phone = payload["phone"]
        if "member_status" in payload and payload["member_status"] is not None:
            patient.member_status = payload["member_status"]
        if "expire_date" in payload:
            raw = payload["expire_date"]
            if raw:
                try:
                    patient.expire_date = datetime.fromisoformat(raw).date() if "T" in raw else date.fromisoformat(raw)
                except Exception:
                    raise CustomException(msg="到期时间格式错误(应为 YYYY-MM-DD)", code=400, status_code=400)
            else:
                patient.expire_date = None
        await self.db.commit()
        return await self._serialize(patient)
