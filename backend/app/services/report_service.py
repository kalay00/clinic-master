"""
报表服务：数据统计和报表生成
"""
from typing import Dict, Any, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.api.v1.module_registration.model import Registration
from app.api.v1.module_payment.model import Bill, Payment
from app.api.v1.module_treatment.model import Prescription
from app.core.logger import logger


class ReportService:
    """报表服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_revenue_report(
        self,
        tenant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        收入报表
        
        Args:
            tenant_id: 租户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict[str, Any]: 收入报表数据，包含汇总数据和每日数据
        """
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        # 基础查询条件
        base_filter = and_(
            Bill.tenant_id == tenant_id_uuid,
            Bill.deleted_at.is_(None),
            Bill.status == "paid"
        )
        
        # 日期过滤（使用支付时间）
        if start_date:
            base_filter = and_(base_filter, func.date(Bill.payment_time) >= start_date)
        if end_date:
            base_filter = and_(base_filter, func.date(Bill.payment_time) <= end_date)
        
        # 汇总统计
        summary_query = self.db.query(
            func.sum(Bill.total_amount).label("total_revenue"),
            func.sum(Bill.paid_amount).label("paid_revenue"),
            func.sum(Bill.insurance_amount).label("insurance_revenue"),
            func.count(Bill.id).label("bill_count")
        ).filter(base_filter)
        
        result = summary_query.first()
        
        # 按支付方式统计
        payment_method_query = self.db.query(
            Bill.payment_method,
            func.sum(Bill.paid_amount).label("amount")
        ).filter(base_filter).group_by(Bill.payment_method)
        
        payment_methods = payment_method_query.all()
        cash_amount = 0.0
        online_amount = 0.0
        insurance_amount = 0.0
        
        for method, amount in payment_methods:
            if method == "cash":
                cash_amount = float(amount) if amount else 0.0
            elif method in ["wechat", "alipay", "online"]:
                online_amount += float(amount) if amount else 0.0
            elif method == "insurance":
                insurance_amount = float(amount) if amount else 0.0
        
        # 每日数据统计
        daily_data = []
        if start_date and end_date:
            current_date = start_date
            while current_date <= end_date:
                day_query = self.db.query(
                    func.sum(Bill.paid_amount).label("amount")
                ).filter(
                    and_(
                        base_filter,
                        func.date(Bill.payment_time) == current_date
                    )
                )
                day_result = day_query.first()
                daily_data.append({
                    "date": current_date.isoformat(),
                    "date_str": current_date.strftime("%Y-%m-%d"),
                    "amount": float(day_result.amount) if day_result and day_result.amount else 0.0,
                    "revenue": float(day_result.amount) if day_result and day_result.amount else 0.0
                })
                current_date += timedelta(days=1)
        
        return {
            "total": float(result.total_revenue) if result.total_revenue else 0.0,
            "total_revenue": float(result.total_revenue) if result.total_revenue else 0.0,
            "paid_revenue": float(result.paid_revenue) if result.paid_revenue else 0.0,
            "cash": cash_amount,
            "cash_amount": cash_amount,
            "online": online_amount,
            "online_amount": online_amount,
            "insurance": insurance_amount,
            "insurance_revenue": insurance_amount,
            "bill_count": result.bill_count or 0,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "daily": daily_data,
            "daily_data": daily_data
        }
    
    def get_visits_report(
        self,
        tenant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        就诊量报表
        
        Args:
            tenant_id: 租户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict[str, Any]: 就诊量报表数据，包含汇总数据和每日数据
        """
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        # 基础查询条件
        base_filter = and_(
            Registration.tenant_id == tenant_id_uuid,
            Registration.deleted_at.is_(None),
            Registration.status == "completed"
        )
        
        # 日期过滤
        if start_date:
            base_filter = and_(base_filter, Registration.registration_date >= start_date)
        if end_date:
            base_filter = and_(base_filter, Registration.registration_date <= end_date)
        
        # 汇总统计
        summary_query = self.db.query(
            func.count(Registration.id).label("total_visits"),
            func.count(func.distinct(Registration.patient_id)).label("unique_patients")
        ).filter(base_filter)
        
        result = summary_query.first()
        
        # 每日数据统计
        daily_data = []
        if start_date and end_date:
            current_date = start_date
            while current_date <= end_date:
                day_query = self.db.query(
                    func.count(Registration.id).label("visits"),
                    func.count(func.distinct(Registration.patient_id)).label("unique_patients")
                ).filter(
                    and_(
                        base_filter,
                        Registration.registration_date == current_date
                    )
                )
                day_result = day_query.first()
                daily_data.append({
                    "date": current_date.isoformat(),
                    "date_str": current_date.strftime("%Y-%m-%d"),
                    "visits": day_result.visits or 0 if day_result else 0,
                    "unique_patients": day_result.unique_patients or 0 if day_result else 0
                })
                current_date += timedelta(days=1)
        
        return {
            "total_visits": result.total_visits or 0,
            "unique_patients": result.unique_patients or 0,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "daily": daily_data,
            "daily_data": daily_data
        }
    
    def get_drugs_report(
        self,
        tenant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        药品销售报表
        
        Args:
            tenant_id: 租户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict[str, Any]: 药品销售报表数据，包含汇总数据、每日数据和药品明细
        """
        from uuid import UUID
        from app.api.v1.module_pharmacy.model import Drug
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        # 基础查询条件
        base_filter = and_(
            Prescription.tenant_id == tenant_id_uuid,
            Prescription.deleted_at.is_(None),
            Prescription.status == "dispensed"
        )
        
        # 日期过滤
        if start_date:
            base_filter = and_(base_filter, func.date(Prescription.created_at) >= start_date)
        if end_date:
            base_filter = and_(base_filter, func.date(Prescription.created_at) <= end_date)
        
        # 汇总统计
        summary_query = self.db.query(
            func.sum(Prescription.total_amount).label("total_amount"),
            func.count(Prescription.id).label("prescription_count")
        ).filter(base_filter)
        
        result = summary_query.first()
        
        # 每日数据统计
        daily_data = []
        if start_date and end_date:
            current_date = start_date
            while current_date <= end_date:
                day_query = self.db.query(
                    func.sum(Prescription.total_amount).label("amount"),
                    func.count(Prescription.id).label("count")
                ).filter(
                    and_(
                        base_filter,
                        func.date(Prescription.created_at) == current_date
                    )
                )
                day_result = day_query.first()
                daily_data.append({
                    "date": current_date.isoformat(),
                    "date_str": current_date.strftime("%Y-%m-%d"),
                    "amount": float(day_result.amount) if day_result and day_result.amount else 0.0,
                    "count": day_result.count or 0 if day_result else 0
                })
                current_date += timedelta(days=1)
        
        # 药品销售明细（按药品统计）
        drug_stats = {}
        prescriptions = self.db.query(Prescription).filter(base_filter).all()
        for prescription in prescriptions:
            if prescription.items:
                items = prescription.items
                if isinstance(items, dict):
                    for drug_id, item_data in items.items():
                        if isinstance(item_data, dict):
                            quantity = float(item_data.get("quantity", 0))
                            price = float(item_data.get("price", item_data.get("unit_price", 0)))
                            amount = quantity * price
                            
                            if drug_id not in drug_stats:
                                drug_stats[drug_id] = {
                                    "drug_id": drug_id,
                                    "quantity": 0.0,
                                    "amount": 0.0,
                                    "count": 0
                                }
                            
                            drug_stats[drug_id]["quantity"] += quantity
                            drug_stats[drug_id]["amount"] += amount
                            drug_stats[drug_id]["count"] += 1
        
        # 获取药品名称
        drug_list = []
        for drug_id, stats in drug_stats.items():
            try:
                drug = self.db.query(Drug).filter(
                    Drug.id == UUID(drug_id) if isinstance(drug_id, str) else drug_id,
                    Drug.tenant_id == tenant_id_uuid
                ).first()
                drug_name = drug.name if drug else "未知药品"
            except Exception:
                drug_name = "未知药品"
            
            drug_list.append({
                "drug_id": drug_id,
                "drug_name": drug_name,
                "quantity": stats["quantity"],
                "amount": stats["amount"],
                "count": stats["count"]
            })
        
        # 按金额排序
        drug_list.sort(key=lambda x: x["amount"], reverse=True)
        
        return {
            "total_amount": float(result.total_amount) if result.total_amount else 0.0,
            "prescription_count": result.prescription_count or 0,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "daily": daily_data,
            "daily_data": daily_data,
            "drugs": drug_list[:20],  # 只返回前20个
            "drug_list": drug_list[:20]
        }
    
    def get_daily_statistics(
        self,
        tenant_id: str,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        每日统计
        
        Args:
            tenant_id: 租户ID
            target_date: 目标日期（默认今天）
        
        Returns:
            Dict[str, Any]: 每日统计数据
        """
        if not target_date:
            target_date = date.today()
        
        # 挂号数
        registration_count = self.db.query(func.count(Registration.id)).filter(
            and_(
                Registration.tenant_id == tenant_id,
                Registration.registration_date == target_date,
                Registration.deleted_at.is_(None)
            )
        ).scalar() or 0
        
        # 收入
        revenue = self.db.query(func.sum(Bill.paid_amount)).filter(
            and_(
                Bill.tenant_id == tenant_id,
                func.date(Bill.payment_time) == target_date,
                Bill.deleted_at.is_(None),
                Bill.status == "paid"
            )
        ).scalar() or 0
        
        # 处方数
        prescription_count = self.db.query(func.count(Prescription.id)).filter(
            and_(
                Prescription.tenant_id == tenant_id,
                func.date(Prescription.created_at) == target_date,
                Prescription.deleted_at.is_(None)
            )
        ).scalar() or 0
        
        return {
            "date": target_date.isoformat(),
            "registration_count": registration_count,
            "revenue": float(revenue) if revenue else 0.0,
            "prescription_count": prescription_count,
        }
    
    def get_dashboard_stats(
        self,
        tenant_id: str,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        获取工作台统计数据
        
        Args:
            tenant_id: 租户ID
            target_date: 目标日期（默认今天）
        
        Returns:
            Dict[str, Any]: 工作台统计数据
        """
        if not target_date:
            target_date = date.today()
        
        # 今日挂号数
        today_registrations = self.db.query(func.count(Registration.id)).filter(
            and_(
                Registration.tenant_id == tenant_id,
                Registration.registration_date == target_date,
                Registration.deleted_at.is_(None)
            )
        ).scalar() or 0
        
        # 今日就诊数（已完成挂号）
        today_visits = self.db.query(func.count(Registration.id)).filter(
            and_(
                Registration.tenant_id == tenant_id,
                Registration.registration_date == target_date,
                Registration.status == "completed",
                Registration.deleted_at.is_(None)
            )
        ).scalar() or 0
        
        # 今日收入（已支付账单）
        today_revenue = self.db.query(func.sum(Bill.paid_amount)).filter(
            and_(
                Bill.tenant_id == tenant_id,
                func.date(Bill.payment_time) == target_date,
                Bill.deleted_at.is_(None),
                Bill.status == "paid"
            )
        ).scalar() or 0
        
        # 待处理处方数（未发药）
        pending_prescriptions = self.db.query(func.count(Prescription.id)).filter(
            and_(
                Prescription.tenant_id == tenant_id,
                Prescription.deleted_at.is_(None),
                Prescription.status != "dispensed"
            )
        ).scalar() or 0
        
        return {
            "today_registrations": today_registrations,
            "today_visits": today_visits,
            "today_revenue": float(today_revenue) if today_revenue else 0.0,
            "pending_prescriptions": pending_prescriptions,
        }
    
    def get_patients_report(
        self,
        tenant_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        患者统计报表
        
        Args:
            tenant_id: 租户ID
            start_date: 开始日期（用于统计新增患者）
            end_date: 结束日期（用于统计新增患者）
        
        Returns:
            Dict[str, Any]: 患者统计报表数据
        """
        from uuid import UUID
        from app.api.v1.module_patient.model import Patient
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        # 总患者数
        total_patients = self.db.query(func.count(Patient.id)).filter(
            and_(
                Patient.tenant_id == tenant_id_uuid,
                Patient.deleted_at.is_(None)
            )
        ).scalar() or 0
        
        # 新增患者数（如果提供了日期范围）
        new_patients = 0
        if start_date and end_date:
            new_patients = self.db.query(func.count(Patient.id)).filter(
                and_(
                    Patient.tenant_id == tenant_id_uuid,
                    Patient.deleted_at.is_(None),
                    func.date(Patient.created_at) >= start_date,
                    func.date(Patient.created_at) <= end_date
                )
            ).scalar() or 0
        
        # 按性别统计
        gender_stats = self.db.query(
            Patient.gender,
            func.count(Patient.id).label("count")
        ).filter(
            and_(
                Patient.tenant_id == tenant_id_uuid,
                Patient.deleted_at.is_(None)
            )
        ).group_by(Patient.gender).all()
        
        male_count = 0
        female_count = 0
        for gender, count in gender_stats:
            if gender == "male":
                male_count = count or 0
            elif gender == "female":
                female_count = count or 0
        
        # 按年龄段统计（需要计算年龄）
        age_groups = {
            "0-18": 0,
            "19-30": 0,
            "31-50": 0,
            "51-70": 0,
            "70+": 0
        }
        
        patients = self.db.query(Patient).filter(
            and_(
                Patient.tenant_id == tenant_id_uuid,
                Patient.deleted_at.is_(None),
                Patient.birthday.isnot(None)
            )
        ).all()
        
        today = date.today()
        for patient in patients:
            if patient.birthday:
                age = today.year - patient.birthday.year - ((today.month, today.day) < (patient.birthday.month, patient.birthday.day))
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
        
        # 每日新增患者数据（如果提供了日期范围）
        daily_data = []
        if start_date and end_date:
            current_date = start_date
            while current_date <= end_date:
                day_count = self.db.query(func.count(Patient.id)).filter(
                    and_(
                        Patient.tenant_id == tenant_id_uuid,
                        Patient.deleted_at.is_(None),
                        func.date(Patient.created_at) == current_date
                    )
                ).scalar() or 0
                daily_data.append({
                    "date": current_date.isoformat(),
                    "date_str": current_date.strftime("%Y-%m-%d"),
                    "count": day_count,
                    "new_patients": day_count
                })
                current_date += timedelta(days=1)
        
        return {
            "total_patients": total_patients,
            "new_patients": new_patients,
            "male_count": male_count,
            "female_count": female_count,
            "age_groups": age_groups,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "daily": daily_data,
            "daily_data": daily_data
        }

