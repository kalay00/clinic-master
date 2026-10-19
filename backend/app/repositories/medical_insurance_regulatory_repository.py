"""
医保局监管数据仓库：医保结算、违规记录、政策配置的数据操作
v2.0新增功能
"""
from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from uuid import UUID

from app.api.v1.module_integration.model import (
    MedicalInsuranceSettlement,
    MedicalInsuranceViolation,
    MedicalInsurancePolicy
)
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class MedicalInsuranceSettlementRepository:
    """医保结算数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_settlement(self, settlement_data: dict, tenant_id: str) -> MedicalInsuranceSettlement:
        """创建医保结算记录"""
        settlement = MedicalInsuranceSettlement(
            tenant_id=tenant_id,
            **settlement_data
        )
        self.db.add(settlement)
        self.db.commit()
        self.db.refresh(settlement)
        return settlement
    
    def get_settlement_by_id(self, settlement_id: str, tenant_id: str) -> Optional[MedicalInsuranceSettlement]:
        """根据ID获取医保结算记录"""
        if isinstance(settlement_id, str):
            try:
                settlement_id_uuid = UUID(settlement_id)
            except (ValueError, TypeError):
                settlement_id_uuid = settlement_id
        else:
            settlement_id_uuid = settlement_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(MedicalInsuranceSettlement).filter(
            and_(
                MedicalInsuranceSettlement.id == settlement_id_uuid,
                MedicalInsuranceSettlement.tenant_id == tenant_id_uuid,
                MedicalInsuranceSettlement.deleted_at.is_(None)
            )
        ).first()
    
    def get_settlement_by_no(self, settlement_no: str, tenant_id: str) -> Optional[MedicalInsuranceSettlement]:
        """根据结算单号获取医保结算记录"""
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(MedicalInsuranceSettlement).filter(
            and_(
                MedicalInsuranceSettlement.settlement_no == settlement_no,
                MedicalInsuranceSettlement.tenant_id == tenant_id_uuid,
                MedicalInsuranceSettlement.deleted_at.is_(None)
            )
        ).first()
    
    def get_settlements(
        self,
        tenant_id: str,
        bill_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        status: Optional[str] = None,
        report_status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[MedicalInsuranceSettlement], int]:
        """获取医保结算记录列表"""
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(MedicalInsuranceSettlement).filter(
            and_(
                MedicalInsuranceSettlement.tenant_id == tenant_id_uuid,
                MedicalInsuranceSettlement.deleted_at.is_(None)
            )
        )
        
        if bill_id:
            if isinstance(bill_id, str):
                try:
                    bill_id_uuid = UUID(bill_id)
                except (ValueError, TypeError):
                    bill_id_uuid = bill_id
            else:
                bill_id_uuid = bill_id
            query = query.filter(MedicalInsuranceSettlement.bill_id == bill_id_uuid)
        
        if patient_id:
            if isinstance(patient_id, str):
                try:
                    patient_id_uuid = UUID(patient_id)
                except (ValueError, TypeError):
                    patient_id_uuid = patient_id
            else:
                patient_id_uuid = patient_id
            query = query.filter(MedicalInsuranceSettlement.patient_id == patient_id_uuid)
        
        if status:
            query = query.filter(MedicalInsuranceSettlement.status == status)
        
        if report_status:
            query = query.filter(MedicalInsuranceSettlement.report_status == report_status)
        
        if start_date:
            query = query.filter(MedicalInsuranceSettlement.created_at >= start_date)
        
        if end_date:
            query = query.filter(MedicalInsuranceSettlement.created_at <= end_date)
        
        total = query.count()
        settlements = query.order_by(desc(MedicalInsuranceSettlement.created_at)).offset(skip).limit(limit).all()
        
        return settlements, total
    
    def update_settlement(self, settlement_id: str, settlement_data: dict, tenant_id: str) -> MedicalInsuranceSettlement:
        """更新医保结算记录"""
        settlement = self.get_settlement_by_id(settlement_id, tenant_id)
        if not settlement:
            raise NotFoundException("医保结算记录", settlement_id)
        
        for key, value in settlement_data.items():
            if hasattr(settlement, key):
                setattr(settlement, key, value)
        
        self.db.commit()
        self.db.refresh(settlement)
        return settlement
    
    def delete_settlement(self, settlement_id: str, tenant_id: str) -> bool:
        """软删除医保结算记录"""
        settlement = self.get_settlement_by_id(settlement_id, tenant_id)
        if not settlement:
            raise NotFoundException("医保结算记录", settlement_id)
        
        settlement.deleted_at = datetime.now()
        self.db.commit()
        return True


class MedicalInsuranceViolationRepository:
    """医保违规记录数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_violation(self, violation_data: dict, tenant_id: str) -> MedicalInsuranceViolation:
        """创建医保违规记录"""
        violation = MedicalInsuranceViolation(
            tenant_id=tenant_id,
            **violation_data
        )
        self.db.add(violation)
        self.db.commit()
        self.db.refresh(violation)
        return violation
    
    def get_violation_by_id(self, violation_id: str, tenant_id: str) -> Optional[MedicalInsuranceViolation]:
        """根据ID获取医保违规记录"""
        if isinstance(violation_id, str):
            try:
                violation_id_uuid = UUID(violation_id)
            except (ValueError, TypeError):
                violation_id_uuid = violation_id
        else:
            violation_id_uuid = violation_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(MedicalInsuranceViolation).filter(
            and_(
                MedicalInsuranceViolation.id == violation_id_uuid,
                MedicalInsuranceViolation.tenant_id == tenant_id_uuid,
                MedicalInsuranceViolation.deleted_at.is_(None)
            )
        ).first()
    
    def get_violations(
        self,
        tenant_id: str,
        violation_type: Optional[str] = None,
        violation_level: Optional[str] = None,
        status: Optional[str] = None,
        bill_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[MedicalInsuranceViolation], int]:
        """获取医保违规记录列表"""
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(MedicalInsuranceViolation).filter(
            and_(
                MedicalInsuranceViolation.tenant_id == tenant_id_uuid,
                MedicalInsuranceViolation.deleted_at.is_(None)
            )
        )
        
        if violation_type:
            query = query.filter(MedicalInsuranceViolation.violation_type == violation_type)
        
        if violation_level:
            query = query.filter(MedicalInsuranceViolation.violation_level == violation_level)
        
        if status:
            query = query.filter(MedicalInsuranceViolation.status == status)
        
        if bill_id:
            if isinstance(bill_id, str):
                try:
                    bill_id_uuid = UUID(bill_id)
                except (ValueError, TypeError):
                    bill_id_uuid = bill_id
            else:
                bill_id_uuid = bill_id
            query = query.filter(MedicalInsuranceViolation.bill_id == bill_id_uuid)
        
        if start_date:
            query = query.filter(MedicalInsuranceViolation.detected_at >= start_date)
        
        if end_date:
            query = query.filter(MedicalInsuranceViolation.detected_at <= end_date)
        
        total = query.count()
        violations = query.order_by(desc(MedicalInsuranceViolation.detected_at)).offset(skip).limit(limit).all()
        
        return violations, total
    
    def update_violation(self, violation_id: str, violation_data: dict, tenant_id: str) -> MedicalInsuranceViolation:
        """更新医保违规记录"""
        violation = self.get_violation_by_id(violation_id, tenant_id)
        if not violation:
            raise NotFoundException("医保违规记录", violation_id)
        
        for key, value in violation_data.items():
            if hasattr(violation, key):
                setattr(violation, key, value)
        
        self.db.commit()
        self.db.refresh(violation)
        return violation
    
    def delete_violation(self, violation_id: str, tenant_id: str) -> bool:
        """软删除医保违规记录"""
        violation = self.get_violation_by_id(violation_id, tenant_id)
        if not violation:
            raise NotFoundException("医保违规记录", violation_id)
        
        violation.deleted_at = datetime.now()
        self.db.commit()
        return True


class MedicalInsurancePolicyRepository:
    """医保政策配置数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_policy(self, policy_data: dict, tenant_id: str) -> MedicalInsurancePolicy:
        """创建医保政策"""
        policy = MedicalInsurancePolicy(
            tenant_id=tenant_id,
            **policy_data
        )
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def get_policy_by_id(self, policy_id: str, tenant_id: str) -> Optional[MedicalInsurancePolicy]:
        """根据ID获取医保政策"""
        if isinstance(policy_id, str):
            try:
                policy_id_uuid = UUID(policy_id)
            except (ValueError, TypeError):
                policy_id_uuid = policy_id
        else:
            policy_id_uuid = policy_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(MedicalInsurancePolicy).filter(
            and_(
                MedicalInsurancePolicy.id == policy_id_uuid,
                MedicalInsurancePolicy.tenant_id == tenant_id_uuid,
                MedicalInsurancePolicy.deleted_at.is_(None)
            )
        ).first()
    
    def get_policy_by_code(self, policy_code: str, tenant_id: str) -> Optional[MedicalInsurancePolicy]:
        """根据政策代码获取医保政策"""
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(MedicalInsurancePolicy).filter(
            and_(
                MedicalInsurancePolicy.policy_code == policy_code,
                MedicalInsurancePolicy.tenant_id == tenant_id_uuid,
                MedicalInsurancePolicy.deleted_at.is_(None)
            )
        ).first()
    
    def get_policies(
        self,
        tenant_id: str,
        policy_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        effective_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[MedicalInsurancePolicy], int]:
        """获取医保政策列表"""
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(MedicalInsurancePolicy).filter(
            and_(
                MedicalInsurancePolicy.tenant_id == tenant_id_uuid,
                MedicalInsurancePolicy.deleted_at.is_(None)
            )
        )
        
        if policy_type:
            query = query.filter(MedicalInsurancePolicy.policy_type == policy_type)
        
        if is_active is not None:
            query = query.filter(MedicalInsurancePolicy.is_active == is_active)
        
        if effective_date:
            query = query.filter(MedicalInsurancePolicy.effective_date <= effective_date)
            query = query.filter(
                or_(
                    MedicalInsurancePolicy.expiry_date.is_(None),
                    MedicalInsurancePolicy.expiry_date >= effective_date
                )
            )
        
        total = query.count()
        policies = query.order_by(desc(MedicalInsurancePolicy.effective_date)).offset(skip).limit(limit).all()
        
        return policies, total
    
    def get_active_policies(self, tenant_id: str, policy_type: Optional[str] = None) -> List[MedicalInsurancePolicy]:
        """获取当前生效的医保政策"""
        now = datetime.now()
        policies, _ = self.get_policies(
            tenant_id=tenant_id,
            policy_type=policy_type,
            is_active=True,
            effective_date=now
        )
        return policies
    
    def update_policy(self, policy_id: str, policy_data: dict, tenant_id: str) -> MedicalInsurancePolicy:
        """更新医保政策"""
        policy = self.get_policy_by_id(policy_id, tenant_id)
        if not policy:
            raise NotFoundException("医保政策", policy_id)
        
        for key, value in policy_data.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def delete_policy(self, policy_id: str, tenant_id: str) -> bool:
        """软删除医保政策"""
        policy = self.get_policy_by_id(policy_id, tenant_id)
        if not policy:
            raise NotFoundException("医保政策", policy_id)
        
        policy.deleted_at = datetime.now()
        self.db.commit()
        return True

