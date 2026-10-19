"""
收费数据仓库：账单和支付的数据操作
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.api.v1.module_payment.model import Bill, Payment
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class BillRepository:
    """账单数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_bill(self, bill_data: dict, tenant_id: str) -> Bill:
        """创建账单"""
        bill = Bill(
            tenant_id=tenant_id,
            **bill_data
        )
        self.db.add(bill)
        self.db.commit()
        self.db.refresh(bill)
        return bill
    
    def get_bill_by_id(self, bill_id: str, tenant_id: str) -> Optional[Bill]:
        """根据ID获取账单"""
        return self.db.query(Bill).filter(
            and_(
                Bill.id == bill_id,
                Bill.tenant_id == tenant_id,
                Bill.deleted_at.is_(None)
            )
        ).first()
    
    def get_bills(
        self,
        tenant_id: str,
        patient_id: Optional[str] = None,
        registration_id: Optional[str] = None,
        status: Optional[str] = None,
        bill_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Bill], int]:
        """获取账单列表"""
        from sqlalchemy.orm import joinedload
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(Bill).options(
            joinedload(Bill.patient),
            joinedload(Bill.registration)
        ).filter(
            and_(
                Bill.tenant_id == tenant_id_uuid,
                Bill.deleted_at.is_(None)
            )
        )
        
        if patient_id:
            if isinstance(patient_id, str):
                try:
                    patient_id_uuid = UUID(patient_id)
                except (ValueError, TypeError):
                    patient_id_uuid = patient_id
            else:
                patient_id_uuid = patient_id
            query = query.filter(Bill.patient_id == patient_id_uuid)
        if registration_id:
            if isinstance(registration_id, str):
                try:
                    registration_id_uuid = UUID(registration_id)
                except (ValueError, TypeError):
                    registration_id_uuid = registration_id
            else:
                registration_id_uuid = registration_id
            query = query.filter(Bill.registration_id == registration_id_uuid)
        if status:
            query = query.filter(Bill.status == status)
        if bill_type:
            query = query.filter(Bill.bill_type == bill_type)
        
        total = query.count()
        bills = query.order_by(Bill.created_at.desc()).offset(skip).limit(limit).all()
        return bills, total
    
    def update_bill(self, bill_id: str, tenant_id: str, bill_data: dict) -> Bill:
        """更新账单"""
        bill = self.get_bill_by_id(bill_id, tenant_id)
        if not bill:
            raise NotFoundException("账单", bill_id)
        
        for key, value in bill_data.items():
            if hasattr(bill, key):
                setattr(bill, key, value)
        
        self.db.commit()
        self.db.refresh(bill)
        return bill


class PaymentRepository:
    """支付数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(self, payment_data: dict, tenant_id: str) -> Payment:
        """创建支付记录"""
        payment = Payment(
            tenant_id=tenant_id,
            **payment_data
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_payment_by_id(self, payment_id: str, tenant_id: str) -> Optional[Payment]:
        """根据ID获取支付记录"""
        return self.db.query(Payment).filter(
            and_(
                Payment.id == payment_id,
                Payment.tenant_id == tenant_id,
                Payment.deleted_at.is_(None)
            )
        ).first()
    
    def get_payments(
        self,
        tenant_id: str,
        bill_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Payment], int]:
        """获取支付记录列表"""
        query = self.db.query(Payment).filter(
            and_(
                Payment.tenant_id == tenant_id,
                Payment.deleted_at.is_(None)
            )
        )
        
        if bill_id:
            query = query.filter(Payment.bill_id == bill_id)
        if patient_id:
            query = query.filter(Payment.patient_id == patient_id)
        if status:
            query = query.filter(Payment.status == status)
        
        total = query.count()
        payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
        return payments, total

