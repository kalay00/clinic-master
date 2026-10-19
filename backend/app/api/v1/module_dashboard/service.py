"""
仪表盘统计服务（聚合查询，对齐 FastapiAdmin 风格，Python 3.12+）
"""
from __future__ import annotations
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, desc

from app.core.base_schema import AuthSchema
from app.api.v1.module_registration.model import Registration
from app.api.v1.module_patient.model import Patient
from app.api.v1.module_doctor.model import Doctor


class DashboardService:
    """仪表盘统计服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth

    @property
    def _tenant_id(self):
        return self.auth.tenant_id if self.auth else None

    @property
    def _db(self):
        return self.auth.db if self.auth else None

    def _scope(self, stmt, model):
        if self._tenant_id is not None:
            stmt = stmt.where(model.tenant_id == self._tenant_id)
        return stmt.where(model.deleted_at.is_(None))

    async def get_stats(self) -> dict:
        db = self._db
        today = date.today()

        # 今日挂号数
        reg_today = await db.scalar(
            self._scope(
                select(func.count(Registration.id)).where(
                    Registration.registration_date == today
                ),
                Registration,
            )
        )
        # 待接诊
        reg_pending = await db.scalar(
            self._scope(
                select(func.count(Registration.id)).where(
                    Registration.status == "pending"
                ),
                Registration,
            )
        )
        # 今日营收（已支付挂号费）
        rev_today = await db.scalar(
            self._scope(
                select(func.coalesce(func.sum(Registration.paid_amount), 0)).where(
                    Registration.registration_date == today,
                    Registration.payment_status == "paid",
                ),
                Registration,
            )
        )
        # 患者总数
        patient_total = await db.scalar(
            self._scope(select(func.count(Patient.id)), Patient)
        )
        # 医生总数（在职）
        doctor_total = await db.scalar(
            self._scope(
                select(func.count(Doctor.id)).where(Doctor.status == "active"),
                Doctor,
            )
        )
        # 药品总数
        try:
            from app.api.v1.module_drug.model import Drug
            drug_total = await db.scalar(
                self._scope(select(func.count(Drug.id)), Drug)
            )
        except Exception:
            drug_total = 0

        # 最近挂号（工作台待接诊）
        from sqlalchemy.orm import selectinload
        recent_stmt = self._scope(
            select(Registration).options(selectinload(Registration.patient)),
            Registration,
        ).order_by(desc(Registration.created_at)).limit(10)
        recent_res = await db.execute(recent_stmt)
        recent_objs = list(recent_res.scalars().all())
        recent = []
        for r in recent_objs:
            patient_name = ""
            patient_no = None
            patient = getattr(r, "patient", None)
            if patient:
                patient_name = getattr(patient, "name", "") or ""
                patient_no = getattr(patient, "patient_no", None)
            recent.append({
                "id": str(r.id),
                "registration_no": getattr(r, "registration_no", ""),
                "patient_name": patient_name,
                "patient_no": patient_no,
                "registration_type": getattr(r, "registration_type", ""),
                "status": getattr(r, "status", ""),
                "registration_date": str(getattr(r, "registration_date", "")) if getattr(r, "registration_date", None) else None,
                "price": float(r.price) if r.price else 0.0,
            })

        return {
            "today_registrations": int(reg_today or 0),
            "pending_registrations": int(reg_pending or 0),
            "today_revenue": float(rev_today or 0),
            "patient_total": int(patient_total or 0),
            "doctor_total": int(doctor_total or 0),
            "drug_total": int(drug_total or 0),
            "recent_registrations": recent,
            "chart": self._empty_chart(),
        }

    def _empty_chart(self) -> dict:
        dates = [
            (date.today() - timedelta(days=i)).isoformat()
            for i in range(6, -1, -1)
        ]
        return {"dates": dates, "registrations": [0] * 7, "revenue": [0.0] * 7}

    async def get_chart(self, chart_type: str = "week") -> dict:
        db = self._db
        if chart_type == "month":
            days = 30
        elif chart_type == "year":
            days = 12
        else:
            days = 7
        end = date.today()
        chart = {"dates": [], "registrations": [], "revenue": []}
        for i in range(days - 1, -1, -1):
            d = end - timedelta(days=i)
            chart["dates"].append(d.isoformat())
            reg_cnt = await db.scalar(
                self._scope(
                    select(func.count(Registration.id)).where(
                        Registration.registration_date == d
                    ),
                    Registration,
                )
            )
            rev = await db.scalar(
                self._scope(
                    select(func.coalesce(func.sum(Registration.paid_amount), 0)).where(
                        Registration.registration_date == d,
                        Registration.payment_status == "paid",
                    ),
                    Registration,
                )
            )
            chart["registrations"].append(int(reg_cnt or 0))
            chart["revenue"].append(float(rev or 0))
        return chart
