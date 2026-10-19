"""
医保数据验证服务：验证采集的医保数据
v2.0新增功能
"""
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.medical_insurance_regulatory_service import MedicalInsuranceRegulatoryService
from app.core.exceptions import ValidationException, BusinessException
from app.core.logger import logger


class MedicalInsuranceDataValidator:
    """医保数据验证服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.regulatory_service = MedicalInsuranceRegulatoryService(db)
    
    def validate_settlement_data(
        self,
        settlement_data: Dict[str, Any],
        tenant_id: str
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        验证医保结算数据
        
        Args:
            settlement_data: 医保结算数据
            tenant_id: 租户ID
        
        Returns:
            Tuple[bool, Optional[str], Optional[Dict[str, Any]]]: (是否通过, 错误信息, 验证后的数据)
        """
        try:
            errors = []
            
            # 1. 格式验证
            format_valid, format_errors = self._validate_settlement_format(settlement_data)
            if not format_valid:
                errors.extend(format_errors)
            
            # 2. 业务规则验证
            business_valid, business_errors = self._validate_settlement_business_rules(
                settlement_data, tenant_id
            )
            if not business_valid:
                errors.extend(business_errors)
            
            # 3. 数据完整性验证
            completeness_valid, completeness_errors = self._validate_settlement_completeness(
                settlement_data
            )
            if not completeness_valid:
                errors.extend(completeness_errors)
            
            if errors:
                error_message = "; ".join(errors)
                logger.warning(f"医保结算数据验证失败: {error_message}")
                return False, error_message, None
            
            # 验证通过，返回验证后的数据
            validated_data = self._normalize_settlement_data(settlement_data)
            
            logger.info(f"医保结算数据验证通过: bill_id={settlement_data.get('bill_id')}")
            return True, None, validated_data
            
        except Exception as e:
            logger.error(f"验证医保结算数据时发生异常: {str(e)}")
            return False, f"验证异常: {str(e)}", None
    
    def _validate_settlement_format(
        self,
        settlement_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        验证结算数据格式
        
        Args:
            settlement_data: 结算数据
        
        Returns:
            Tuple[bool, List[str]]: (是否通过, 错误列表)
        """
        errors = []
        
        # 必需字段检查
        required_fields = ["bill_id", "patient_id", "total_amount"]
        for field in required_fields:
            if field not in settlement_data or settlement_data[field] is None:
                errors.append(f"缺少必需字段: {field}")
        
        # 金额字段验证
        if "total_amount" in settlement_data:
            try:
                total_amount = Decimal(str(settlement_data["total_amount"]))
                if total_amount < 0:
                    errors.append("总金额不能为负数")
            except (ValueError, TypeError):
                errors.append("总金额格式错误")
        
        if "insurance_amount" in settlement_data and settlement_data["insurance_amount"] is not None:
            try:
                insurance_amount = Decimal(str(settlement_data["insurance_amount"]))
                if insurance_amount < 0:
                    errors.append("医保支付金额不能为负数")
            except (ValueError, TypeError):
                errors.append("医保支付金额格式错误")
        
        if "personal_amount" in settlement_data and settlement_data["personal_amount"] is not None:
            try:
                personal_amount = Decimal(str(settlement_data["personal_amount"]))
                if personal_amount < 0:
                    errors.append("个人支付金额不能为负数")
            except (ValueError, TypeError):
                errors.append("个人支付金额格式错误")
        
        # 金额一致性验证
        if all(key in settlement_data and settlement_data[key] is not None 
               for key in ["total_amount", "insurance_amount", "personal_amount"]):
            try:
                total = Decimal(str(settlement_data["total_amount"]))
                insurance = Decimal(str(settlement_data["insurance_amount"]))
                personal = Decimal(str(settlement_data["personal_amount"]))
                
                if abs(total - insurance - personal) > Decimal("0.01"):  # 允许0.01的误差
                    errors.append("总金额、医保支付金额、个人支付金额不一致")
            except (ValueError, TypeError):
                pass  # 格式错误已在上面检查
        
        # 医保卡号格式验证
        if "insurance_card_no" in settlement_data and settlement_data["insurance_card_no"]:
            card_no = str(settlement_data["insurance_card_no"]).strip()
            if len(card_no) < 10 or len(card_no) > 20:
                errors.append("医保卡号长度应在10-20位之间")
        
        return len(errors) == 0, errors
    
    def _validate_settlement_business_rules(
        self,
        settlement_data: Dict[str, Any],
        tenant_id: str
    ) -> Tuple[bool, List[str]]:
        """
        验证结算数据业务规则
        
        Args:
            settlement_data: 结算数据
            tenant_id: 租户ID
        
        Returns:
            Tuple[bool, List[str]]: (是否通过, 错误列表)
        """
        errors = []
        
        # 获取当前生效的医保政策
        try:
            active_policies = self.regulatory_service.get_active_policies(tenant_id, "reimbursement")
            
            # 验证报销比例是否符合政策
            if "reimbursement_ratio" in settlement_data and settlement_data["reimbursement_ratio"] is not None:
                reimbursement_ratio = float(settlement_data["reimbursement_ratio"])
                
                # 检查是否有政策限制报销比例
                for policy in active_policies:
                    policy_rules = policy.policy_rules or {}
                    max_ratio = policy_rules.get("max_reimbursement_ratio")
                    min_ratio = policy_rules.get("min_reimbursement_ratio")
                    
                    if max_ratio and reimbursement_ratio > float(max_ratio):
                        errors.append(f"报销比例超过政策限制: {max_ratio}")
                    if min_ratio and reimbursement_ratio < float(min_ratio):
                        errors.append(f"报销比例低于政策限制: {min_ratio}")
            
            # 验证医保支付金额是否符合政策
            if "insurance_amount" in settlement_data and settlement_data["insurance_amount"] is not None:
                insurance_amount = Decimal(str(settlement_data["insurance_amount"]))
                
                for policy in active_policies:
                    policy_rules = policy.policy_rules or {}
                    max_amount = policy_rules.get("max_insurance_amount")
                    
                    if max_amount and insurance_amount > Decimal(str(max_amount)):
                        errors.append(f"医保支付金额超过政策限制: {max_amount}")
        
        except Exception as e:
            logger.warning(f"验证业务规则时发生异常: {str(e)}")
            # 业务规则验证失败不影响数据采集，只记录警告
        
        return len(errors) == 0, errors
    
    def _validate_settlement_completeness(
        self,
        settlement_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        验证结算数据完整性
        
        Args:
            settlement_data: 结算数据
        
        Returns:
            Tuple[bool, List[str]]: (是否通过, 错误列表)
        """
        errors = []
        
        # 检查结算明细
        if "settlement_details" not in settlement_data or not settlement_data["settlement_details"]:
            errors.append("缺少结算明细")
        else:
            details = settlement_data["settlement_details"]
            if "items" not in details or not details["items"]:
                errors.append("结算明细中缺少项目列表")
        
        return len(errors) == 0, errors
    
    def _normalize_settlement_data(
        self,
        settlement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        规范化结算数据
        
        Args:
            settlement_data: 结算数据
        
        Returns:
            Dict[str, Any]: 规范化后的数据
        """
        normalized = settlement_data.copy()
        
        # 确保金额字段为Decimal类型
        if "total_amount" in normalized and normalized["total_amount"] is not None:
            normalized["total_amount"] = Decimal(str(normalized["total_amount"]))
        
        if "insurance_amount" in normalized and normalized["insurance_amount"] is not None:
            normalized["insurance_amount"] = Decimal(str(normalized["insurance_amount"]))
        else:
            normalized["insurance_amount"] = Decimal("0")
        
        if "personal_amount" in normalized and normalized["personal_amount"] is not None:
            normalized["personal_amount"] = Decimal(str(normalized["personal_amount"]))
        else:
            # 自动计算个人支付金额
            total = normalized.get("total_amount", Decimal("0"))
            insurance = normalized.get("insurance_amount", Decimal("0"))
            normalized["personal_amount"] = total - insurance
        
        # 重新计算报销比例
        if normalized.get("total_amount") and normalized["total_amount"] > 0:
            normalized["reimbursement_ratio"] = (
                normalized["insurance_amount"] / normalized["total_amount"]
            )
        else:
            normalized["reimbursement_ratio"] = None
        
        return normalized
    
    def validate_violation_data(
        self,
        violation_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        验证违规数据
        
        Args:
            violation_data: 违规数据
        
        Returns:
            Tuple[bool, Optional[str]]: (是否通过, 错误信息)
        """
        try:
            errors = []
            
            # 必需字段检查
            required_fields = ["violation_type", "violation_desc"]
            for field in required_fields:
                if field not in violation_data or not violation_data[field]:
                    errors.append(f"缺少必需字段: {field}")
            
            # 违规类型验证
            valid_violation_types = [
                "over_limit", "duplicate", "unauthorized", "invalid_diagnosis",
                "invalid_prescription", "other"
            ]
            if "violation_type" in violation_data:
                if violation_data["violation_type"] not in valid_violation_types:
                    errors.append(f"无效的违规类型: {violation_data['violation_type']}")
            
            # 违规级别验证
            valid_violation_levels = ["low", "medium", "high"]
            if "violation_level" in violation_data:
                if violation_data["violation_level"] not in valid_violation_levels:
                    errors.append(f"无效的违规级别: {violation_data['violation_level']}")
            
            if errors:
                error_message = "; ".join(errors)
                logger.warning(f"违规数据验证失败: {error_message}")
                return False, error_message
            
            logger.info("违规数据验证通过")
            return True, None
            
        except Exception as e:
            logger.error(f"验证违规数据时发生异常: {str(e)}")
            return False, f"验证异常: {str(e)}"

