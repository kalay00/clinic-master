"""
医保局监管服务：医保结算、违规监控、政策管理
v2.0新增功能
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.api.v1.module_integration.model import (
    MedicalInsuranceSettlement,
    MedicalInsuranceViolation,
    MedicalInsurancePolicy
)
from app.repositories.medical_insurance_regulatory_repository import (
    MedicalInsuranceSettlementRepository,
    MedicalInsuranceViolationRepository,
    MedicalInsurancePolicyRepository
)
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger
from app.utils.common import generate_id


class MedicalInsuranceRegulatoryService:
    """医保局监管服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.settlement_repo = MedicalInsuranceSettlementRepository(db)
        self.violation_repo = MedicalInsuranceViolationRepository(db)
        self.policy_repo = MedicalInsurancePolicyRepository(db)
    
    # ==================== 医保结算管理 ====================
    
    def create_settlement(
        self,
        settlement_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> MedicalInsuranceSettlement:
        """
        创建医保结算记录
        
        Args:
            settlement_data: 结算数据
            tenant_id: 租户ID
            creator_id: 创建人ID
        
        Returns:
            MedicalInsuranceSettlement: 医保结算记录
        """
        # 生成结算单号
        if "settlement_no" not in settlement_data:
            settlement_no = f"MI{generate_id()[:10].upper()}"
            settlement_data["settlement_no"] = settlement_no
        
        settlement = self.settlement_repo.create_settlement(settlement_data, tenant_id)
        settlement.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建医保结算记录: {settlement.id} by {creator_id}")
        return settlement
    
    def get_settlement(self, settlement_id: str, tenant_id: str) -> MedicalInsuranceSettlement:
        """
        获取医保结算记录详情
        
        Args:
            settlement_id: 结算记录ID
            tenant_id: 租户ID
        
        Returns:
            MedicalInsuranceSettlement: 医保结算记录
        """
        settlement = self.settlement_repo.get_settlement_by_id(settlement_id, tenant_id)
        if not settlement:
            raise NotFoundException("医保结算记录", settlement_id)
        return settlement
    
    def get_settlement_by_no(self, settlement_no: str, tenant_id: str) -> MedicalInsuranceSettlement:
        """
        根据结算单号获取医保结算记录
        
        Args:
            settlement_no: 结算单号
            tenant_id: 租户ID
        
        Returns:
            MedicalInsuranceSettlement: 医保结算记录
        """
        settlement = self.settlement_repo.get_settlement_by_no(settlement_no, tenant_id)
        if not settlement:
            raise NotFoundException("医保结算记录", settlement_no)
        return settlement
    
    def list_settlements(
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
        """
        获取医保结算记录列表
        
        Args:
            tenant_id: 租户ID
            bill_id: 账单ID
            patient_id: 患者ID
            status: 结算状态
            report_status: 上报状态
            start_date: 开始日期
            end_date: 结束日期
            skip: 跳过数量
            limit: 返回数量
        
        Returns:
            Tuple[List[MedicalInsuranceSettlement], int]: 结算记录列表和总数
        """
        return self.settlement_repo.get_settlements(
            tenant_id, bill_id, patient_id, status, report_status, start_date, end_date, skip, limit
        )
    
    def update_settlement(
        self,
        settlement_id: str,
        settlement_data: Dict[str, Any],
        tenant_id: str,
        updater_id: str
    ) -> MedicalInsuranceSettlement:
        """
        更新医保结算记录
        
        Args:
            settlement_id: 结算记录ID
            settlement_data: 更新数据
            tenant_id: 租户ID
            updater_id: 更新人ID
        
        Returns:
            MedicalInsuranceSettlement: 更新后的医保结算记录
        """
        settlement = self.settlement_repo.update_settlement(settlement_id, settlement_data, tenant_id)
        settlement.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新医保结算记录: {settlement_id} by {updater_id}")
        return settlement
    
    def delete_settlement(self, settlement_id: str, tenant_id: str) -> bool:
        """
        删除医保结算记录（软删除）
        
        Args:
            settlement_id: 结算记录ID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否删除成功
        """
        return self.settlement_repo.delete_settlement(settlement_id, tenant_id)
    
    # ==================== 医保违规管理 ====================
    
    def create_violation(
        self,
        violation_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> MedicalInsuranceViolation:
        """
        创建医保违规记录
        
        Args:
            violation_data: 违规数据
            tenant_id: 租户ID
            creator_id: 创建人ID
        
        Returns:
            MedicalInsuranceViolation: 医保违规记录
        """
        # 生成违规记录编号
        if "violation_no" not in violation_data:
            violation_no = f"VIO{generate_id()[:10].upper()}"
            violation_data["violation_no"] = violation_no
        
        # 设置检测时间
        if "detected_at" not in violation_data:
            violation_data["detected_at"] = datetime.now()
        
        violation = self.violation_repo.create_violation(violation_data, tenant_id)
        violation.created_by = creator_id
        self.db.commit()
        
        logger.warning(f"创建医保违规记录: {violation.id} by {creator_id}")
        return violation
    
    def get_violation(self, violation_id: str, tenant_id: str) -> MedicalInsuranceViolation:
        """
        获取医保违规记录详情
        
        Args:
            violation_id: 违规记录ID
            tenant_id: 租户ID
        
        Returns:
            MedicalInsuranceViolation: 医保违规记录
        """
        violation = self.violation_repo.get_violation_by_id(violation_id, tenant_id)
        if not violation:
            raise NotFoundException("医保违规记录", violation_id)
        return violation
    
    def list_violations(
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
        """
        获取医保违规记录列表
        
        Args:
            tenant_id: 租户ID
            violation_type: 违规类型
            violation_level: 违规级别
            status: 处理状态
            bill_id: 账单ID
            start_date: 开始日期
            end_date: 结束日期
            skip: 跳过数量
            limit: 返回数量
        
        Returns:
            Tuple[List[MedicalInsuranceViolation], int]: 违规记录列表和总数
        """
        return self.violation_repo.get_violations(
            tenant_id, violation_type, violation_level, status, bill_id, start_date, end_date, skip, limit
        )
    
    def update_violation(
        self,
        violation_id: str,
        violation_data: Dict[str, Any],
        tenant_id: str,
        updater_id: str
    ) -> MedicalInsuranceViolation:
        """
        更新医保违规记录
        
        Args:
            violation_id: 违规记录ID
            violation_data: 更新数据
            tenant_id: 租户ID
            updater_id: 更新人ID
        
        Returns:
            MedicalInsuranceViolation: 更新后的医保违规记录
        """
        violation = self.violation_repo.update_violation(violation_id, violation_data, tenant_id)
        violation.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新医保违规记录: {violation_id} by {updater_id}")
        return violation
    
    def confirm_violation(
        self,
        violation_id: str,
        tenant_id: str,
        confirmer_id: str
    ) -> MedicalInsuranceViolation:
        """
        确认医保违规记录
        
        Args:
            violation_id: 违规记录ID
            tenant_id: 租户ID
            confirmer_id: 确认人ID
        
        Returns:
            MedicalInsuranceViolation: 确认后的医保违规记录
        """
        violation = self.get_violation(violation_id, tenant_id)
        
        violation.status = "confirmed"
        violation.confirmed_at = datetime.now()
        violation.updated_by = confirmer_id
        self.db.commit()
        
        logger.info(f"确认医保违规记录: {violation_id} by {confirmer_id}")
        return violation
    
    def handle_violation(
        self,
        violation_id: str,
        handling_result: str,
        tenant_id: str,
        handler_id: str
    ) -> MedicalInsuranceViolation:
        """
        处理医保违规记录
        
        Args:
            violation_id: 违规记录ID
            handling_result: 处理结果
            tenant_id: 租户ID
            handler_id: 处理人ID
        
        Returns:
            MedicalInsuranceViolation: 处理后的医保违规记录
        """
        violation = self.get_violation(violation_id, tenant_id)
        
        violation.status = "handled"
        violation.handled_at = datetime.now()
        violation.handled_by = handler_id
        violation.handling_result = handling_result
        violation.updated_by = handler_id
        self.db.commit()
        
        logger.info(f"处理医保违规记录: {violation_id} by {handler_id}")
        return violation
    
    def delete_violation(self, violation_id: str, tenant_id: str) -> bool:
        """
        删除医保违规记录（软删除）
        
        Args:
            violation_id: 违规记录ID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否删除成功
        """
        return self.violation_repo.delete_violation(violation_id, tenant_id)
    
    # ==================== 医保政策管理 ====================
    
    def create_policy(
        self,
        policy_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> MedicalInsurancePolicy:
        """
        创建医保政策
        
        Args:
            policy_data: 政策数据
            tenant_id: 租户ID
            creator_id: 创建人ID
        
        Returns:
            MedicalInsurancePolicy: 医保政策
        """
        # 检查政策代码是否已存在
        if "policy_code" in policy_data:
            existing_policy = self.policy_repo.get_policy_by_code(policy_data["policy_code"], tenant_id)
            if existing_policy:
                raise BusinessException(f"政策代码已存在: {policy_data['policy_code']}")
        
        policy = self.policy_repo.create_policy(policy_data, tenant_id)
        policy.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建医保政策: {policy.id} by {creator_id}")
        return policy
    
    def get_policy(self, policy_id: str, tenant_id: str) -> MedicalInsurancePolicy:
        """
        获取医保政策详情
        
        Args:
            policy_id: 政策ID
            tenant_id: 租户ID
        
        Returns:
            MedicalInsurancePolicy: 医保政策
        """
        policy = self.policy_repo.get_policy_by_id(policy_id, tenant_id)
        if not policy:
            raise NotFoundException("医保政策", policy_id)
        return policy
    
    def get_policy_by_code(self, policy_code: str, tenant_id: str) -> MedicalInsurancePolicy:
        """
        根据政策代码获取医保政策
        
        Args:
            policy_code: 政策代码
            tenant_id: 租户ID
        
        Returns:
            MedicalInsurancePolicy: 医保政策
        """
        policy = self.policy_repo.get_policy_by_code(policy_code, tenant_id)
        if not policy:
            raise NotFoundException("医保政策", policy_code)
        return policy
    
    def list_policies(
        self,
        tenant_id: str,
        policy_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        effective_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[MedicalInsurancePolicy], int]:
        """
        获取医保政策列表
        
        Args:
            tenant_id: 租户ID
            policy_type: 政策类型
            is_active: 是否生效
            effective_date: 生效日期
            skip: 跳过数量
            limit: 返回数量
        
        Returns:
            Tuple[List[MedicalInsurancePolicy], int]: 政策列表和总数
        """
        return self.policy_repo.get_policies(
            tenant_id, policy_type, is_active, effective_date, skip, limit
        )
    
    def get_active_policies(
        self,
        tenant_id: str,
        policy_type: Optional[str] = None
    ) -> List[MedicalInsurancePolicy]:
        """
        获取当前生效的医保政策
        
        Args:
            tenant_id: 租户ID
            policy_type: 政策类型
        
        Returns:
            List[MedicalInsurancePolicy]: 生效的政策列表
        """
        return self.policy_repo.get_active_policies(tenant_id, policy_type)
    
    def update_policy(
        self,
        policy_id: str,
        policy_data: Dict[str, Any],
        tenant_id: str,
        updater_id: str
    ) -> MedicalInsurancePolicy:
        """
        更新医保政策
        
        Args:
            policy_id: 政策ID
            policy_data: 更新数据
            tenant_id: 租户ID
            updater_id: 更新人ID
        
        Returns:
            MedicalInsurancePolicy: 更新后的医保政策
        """
        policy = self.policy_repo.update_policy(policy_id, policy_data, tenant_id)
        policy.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新医保政策: {policy_id} by {updater_id}")
        return policy
    
    def delete_policy(self, policy_id: str, tenant_id: str) -> bool:
        """
        删除医保政策（软删除）
        
        Args:
            policy_id: 政策ID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否删除成功
        """
        return self.policy_repo.delete_policy(policy_id, tenant_id)

