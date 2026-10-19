"""
报表服务（对齐旧 services/report_service.py，异步，Python 3.12+）

本模块无独立 ORM 模型，直接使用 AuthSchema 的异步会话查询各业务表。
"""
from __future__ import annotations
from typing import Optional, Dict, Any
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import select, func, and_

from app.core.base_schema import AuthSchema
from app.core.logger import logger

from app.api.v1.module_registration.model import Registration
from app.api.v1.module_payment.model import Bill, Payment
from app.api.v1.module_treatment.model import Prescription
from app.api.v1.module_pharmacy.model import Drug
from app.api.v1.module_patient.model import Patient


def _to_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return value


class ReportService:
    """报表服务（无独立模型，使用 auth 会话）"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.db = auth.db

    @property
    def _tenant_id(self) -> Optional[str]:
        return self.auth.tenant_id if self.auth else None

    # ── 收入报表 ──
    async def get_revenue_report(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None, tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        tid = _to_uuid(tenant_id or self._tenant_id)
        base = and_(Bill.tenant_id == tid, Bill.deleted_at.is_(None), Bill.status == "paid")
        if start_date:
            base = and_(base, func.date(Bill.payment_time) >= start_date)
        if end_date:
            base = and_(base, func.date(Bill.payment_time) <= end_date)

        summary = (await self.db.execute(
            select(
                func.sum(Bill.total_amount).label("total_revenue"),
                func.sum(Bill.paid_amount).label("paid_revenue"),
                func.sum(Bill.insurance_amount).label("insurance_revenue"),
                func.count(Bill.id).label("bill_count"),
            ).where(base)
        )).first()

        methods = (await self.db.execute(
            select(Bill.payment_method, func.sum(Bill.paid_amount).label("amount")).where(base).group_by(Bill.payment_method)
        )).all()
        cash = online = insurance = 0.0
        for method, amount in methods:
            amt = float(amount) if amount else 0.0
            if method == "cash":
                cash = amt
            elif method in ("wechat", "alipay", "online"):
                online += amt
            elif method == "insurance":
                insurance = amt

        daily: list = []
        if start_date and end_date:
            cur = start_date
            while cur <= end_date:
                d = (await self.db.execute(
                    select(func.sum(Bill.paid_amount).label("amount")).where(and_(base, func.date(Bill.payment_time) == cur))
                )).first()
                daily.append({
                    "date": cur.isoformat(), "date_str": cur.strftime("%Y-%m-%d"),
                    "amount": float(d.amount) if d and d.amount else 0.0,
                    "revenue": float(d.amount) if d and d.amount else 0.0,
                })
                cur += timedelta(days=1)

        return {
            "total": float(summary.total_revenue) if summary and summary.total_revenue else 0.0,
            "total_revenue": float(summary.total_revenue) if summary and summary.total_revenue else 0.0,
            "paid_revenue": float(summary.paid_revenue) if summary and summary.paid_revenue else 0.0,
            "cash": cash, "cash_amount": cash,
            "online": online, "online_amount": online,
            "insurance": insurance, "insurance_revenue": insurance,
            "bill_count": summary.bill_count or 0 if summary else 0,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "daily": daily, "daily_data": daily,
        }

    # ── 就诊量报表 ──
    async def get_visits_report(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None, tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        tid = _to_uuid(tenant_id or self._tenant_id)
        base = and_(Registration.tenant_id == tid, Registration.deleted_at.is_(None), Registration.status == "completed")
        if start_date:
            base = and_(base, Registration.registration_date >= start_date)
        if end_date:
            base = and_(base, Registration.registration_date <= end_date)

        summary = (await self.db.execute(
            select(
                func.count(Registration.id).label("total_visits"),
                func.count(func.distinct(Registration.patient_id)).label("unique_patients"),
            ).where(base)
        )).first()

        daily: list = []
        if start_date and end_date:
            cur = start_date
            while cur <= end_date:
                d = (await self.db.execute(
                    select(
                        func.count(Registration.id).label("visits"),
                        func.count(func.distinct(Registration.patient_id)).label("unique_patients"),
                    ).where(and_(base, Registration.registration_date == cur))
                )).first()
                daily.append({
                    "date": cur.isoformat(), "date_str": cur.strftime("%Y-%m-%d"),
                    "visits": d.visits or 0 if d else 0,
                    "unique_patients": d.unique_patients or 0 if d else 0,
                })
                cur += timedelta(days=1)

        return {
            "total_visits": summary.total_visits or 0 if summary else 0,
            "unique_patients": summary.unique_patients or 0 if summary else 0,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "daily": daily, "daily_data": daily,
        }

    # ── 药品销售报表 ──
    async def get_drugs_report(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None, tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        tid = _to_uuid(tenant_id or self._tenant_id)
        base = and_(Prescription.tenant_id == tid, Prescription.deleted_at.is_(None), Prescription.status == "dispensed")
        if start_date:
            base = and_(base, func.date(Prescription.created_at) >= start_date)
        if end_date:
            base = and_(base, func.date(Prescription.created_at) <= end_date)

        summary = (await self.db.execute(
            select(
                func.sum(Prescription.total_amount).label("total_amount"),
                func.count(Prescription.id).label("prescription_count"),
            ).where(base)
        )).first()

        daily: list = []
        if start_date and end_date:
            cur = start_date
            while cur <= end_date:
                d = (await self.db.execute(
                    select(
                        func.sum(Prescription.total_amount).label("amount"),
                        func.count(Prescription.id).label("count"),
                    ).where(and_(base, func.date(Prescription.created_at) == cur))
                )).first()
                daily.append({
                    "date": cur.isoformat(), "date_str": cur.strftime("%Y-%m-%d"),
                    "amount": float(d.amount) if d and d.amount else 0.0,
                    "count": d.count or 0 if d else 0,
                })
                cur += timedelta(days=1)

        prescriptions = (await self.db.execute(select(Prescription).where(base))).scalars().all()
        drug_stats: Dict[str, Any] = {}
        for pres in prescriptions:
            items = pres.items
            if isinstance(items, dict):
                for drug_id, item_data in items.items():
                    if not isinstance(item_data, dict):
                        continue
                    qty = float(item_data.get("quantity", 0))
                    price = float(item_data.get("price", item_data.get("unit_price", 0)))
                    drug_stats.setdefault(drug_id, {"drug_id": drug_id, "quantity": 0.0, "amount": 0.0, "count": 0})
                    drug_stats[drug_id]["quantity"] += qty
                    drug_stats[drug_id]["amount"] += qty * price
                    drug_stats[drug_id]["count"] += 1

        drug_list = []
        for drug_id, stats in drug_stats.items():
            try:
                drug = (await self.db.execute(
                    select(Drug).where(Drug.id == _to_uuid(drug_id), Drug.tenant_id == tid)
                )).scalars().first()
                drug_name = drug.name if drug else "未知药品"
            except Exception:  # pragma: no cover
                drug_name = "未知药品"
            drug_list.append({
                "drug_id": drug_id, "drug_name": drug_name,
                "quantity": stats["quantity"], "amount": stats["amount"], "count": stats["count"],
            })
        drug_list.sort(key=lambda x: x["amount"], reverse=True)

        return {
            "total_amount": float(summary.total_amount) if summary and summary.total_amount else 0.0,
            "prescription_count": summary.prescription_count or 0 if summary else 0,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "daily": daily, "daily_data": daily,
            "drugs": drug_list[:20], "drug_list": drug_list[:20],
        }

    # ── 每日统计 ──
    async def get_daily_statistics(self, target_date: Optional[date] = None, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        if not target_date:
            target_date = date.today()
        tid = _to_uuid(tenant_id or self._tenant_id)
        reg_count = (await self.db.execute(
            select(func.count(Registration.id)).where(
                and_(Registration.tenant_id == tid, Registration.registration_date == target_date, Registration.deleted_at.is_(None))
            )
        )).scalar() or 0
        revenue = (await self.db.execute(
            select(func.sum(Bill.paid_amount)).where(
                and_(Bill.tenant_id == tid, func.date(Bill.payment_time) == target_date, Bill.deleted_at.is_(None), Bill.status == "paid")
            )
        )).scalar() or 0
        presc_count = (await self.db.execute(
            select(func.count(Prescription.id)).where(
                and_(Prescription.tenant_id == tid, func.date(Prescription.created_at) == target_date, Prescription.deleted_at.is_(None))
            )
        )).scalar() or 0
        return {
            "date": target_date.isoformat(),
            "registration_count": reg_count,
            "revenue": float(revenue) if revenue else 0.0,
            "prescription_count": presc_count,
        }

    # ── 工作台统计 ──
    async def get_dashboard_stats(self, target_date: Optional[date] = None, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        if not target_date:
            target_date = date.today()
        tid = _to_uuid(tenant_id or self._tenant_id)
        today_reg = (await self.db.execute(
            select(func.count(Registration.id)).where(
                and_(Registration.tenant_id == tid, Registration.registration_date == target_date, Registration.deleted_at.is_(None))
            )
        )).scalar() or 0
        today_visits = (await self.db.execute(
            select(func.count(Registration.id)).where(
                and_(Registration.tenant_id == tid, Registration.registration_date == target_date,
                     Registration.status == "completed", Registration.deleted_at.is_(None))
            )
        )).scalar() or 0
        today_revenue = (await self.db.execute(
            select(func.sum(Bill.paid_amount)).where(
                and_(Bill.tenant_id == tid, func.date(Bill.payment_time) == target_date, Bill.deleted_at.is_(None), Bill.status == "paid")
            )
        )).scalar() or 0
        pending_presc = (await self.db.execute(
            select(func.count(Prescription.id)).where(
                and_(Prescription.tenant_id == tid, Prescription.deleted_at.is_(None), Prescription.status != "dispensed")
            )
        )).scalar() or 0
        return {
            "today_registrations": today_reg,
            "today_visits": today_visits,
            "today_revenue": float(today_revenue) if today_revenue else 0.0,
            "pending_prescriptions": pending_presc,
        }

    # ── 患者统计报表 ──
    async def get_patients_report(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None, tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        tid = _to_uuid(tenant_id or self._tenant_id)
        total = (await self.db.execute(
            select(func.count(Patient.id)).where(and_(Patient.tenant_id == tid, Patient.deleted_at.is_(None)))
        )).scalar() or 0
        new_patients = 0
        if start_date and end_date:
            new_patients = (await self.db.execute(
                select(func.count(Patient.id)).where(
                    and_(Patient.tenant_id == tid, Patient.deleted_at.is_(None),
                         func.date(Patient.created_at) >= start_date, func.date(Patient.created_at) <= end_date)
                )
            )).scalar() or 0

        gender = (await self.db.execute(
            select(Patient.gender, func.count(Patient.id).label("c")).where(
                and_(Patient.tenant_id == tid, Patient.deleted_at.is_(None))
            ).group_by(Patient.gender)
        )).all()
        male = female = 0
        for g, c in gender:
            if g == "male":
                male = c or 0
            elif g == "female":
                female = c or 0

        age_groups = {"0-18": 0, "19-30": 0, "31-50": 0, "51-70": 0, "70+": 0}
        patients = (await self.db.execute(
            select(Patient).where(and_(Patient.tenant_id == tid, Patient.deleted_at.is_(None), Patient.birthday.isnot(None)))
        )).scalars().all()
        today = date.today()
        for p in patients:
            if p.birthday:
                age = today.year - p.birthday.year - ((today.month, today.day) < (p.birthday.month, p.birthday.day))
                if age <= 18:
                    age_groups["0-18"] += 1
                elif age <= 30:
                    age_groups["19-30"] += 1
                elif age <= 50:
                    age_groups["31-50"] += 1
                elif age <= 70:
                    age_groups["51-70"] += 1
                else:
                    age_groups["70+"] += 1

        daily: list = []
        if start_date and end_date:
            cur = start_date
            while cur <= end_date:
                c = (await self.db.execute(
                    select(func.count(Patient.id)).where(
                        and_(Patient.tenant_id == tid, Patient.deleted_at.is_(None), func.date(Patient.created_at) == cur)
                    )
                )).scalar() or 0
                daily.append({"date": cur.isoformat(), "date_str": cur.strftime("%Y-%m-%d"), "count": c, "new_patients": c})
                cur += timedelta(days=1)

        return {
            "total_patients": total, "new_patients": new_patients,
            "male_count": male, "female_count": female,
            "age_groups": age_groups,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "daily": daily, "daily_data": daily,
        }
