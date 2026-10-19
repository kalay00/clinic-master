"""
医保数据采集服务：从业务数据中采集医保相关数据
v2.0新增功能
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.api.v1.module_payment.model import Bill, Payment
from app.api.v1.module_treatment.model import MedicalRecord, Prescription
from app.api.v1.module_patient.model import Patient
from app.services.payment_service import PaymentService
from app.services.treatment_service import TreatmentService
from app.services.patient_service import PatientService
from app.services.medical_insurance_regulatory_service import MedicalInsuranceRegulatoryService
from app.core.exceptions import BusinessException
from app.core.logger import logger
from app.core.encryption import EncryptionService


class MedicalInsuranceDataCollector:
    """医保数据采集服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.payment_service = PaymentService(db)
        self.treatment_service = TreatmentService(db)
        self.patient_service = PatientService(db)
        self.regulatory_service = MedicalInsuranceRegulatoryService(db)
        self.encryption_service = EncryptionService()
    
    def collect_settlement_data_from_bill(
        self,
        bill_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        从账单数据中采集医保结算数据
        
        Args:
            bill_id: 账单ID
            tenant_id: 租户ID
        
        Returns:
            Dict[str, Any]: 医保结算数据
        """
        try:
            # 获取账单信息
            bill = self.payment_service.get_bill(bill_id, tenant_id)
            
            if not bill:
                raise BusinessException(f"账单不存在: {bill_id}")
            
            # 只采集已支付的账单
            if bill.status != "paid":
                raise BusinessException(f"账单未支付，无法采集医保数据: {bill_id}")
            
            # 获取患者信息
            patient = self.patient_service.get_patient(str(bill.patient_id), tenant_id)
            if not patient:
                raise BusinessException(f"患者不存在: {bill.patient_id}")
            
            # 解密患者信息
            patient_data = self.patient_service.decrypt_patient_data(patient)
            
            # 获取病历信息（如果有）
            medical_record = None
            if bill.medical_record_id:
                try:
                    medical_record = self.treatment_service.get_medical_record(
                        str(bill.medical_record_id), tenant_id
                    )
                except Exception as e:
                    logger.warning(f"获取病历信息失败: {str(e)}")
            
            # 构建医保结算数据
            settlement_data = {
                "bill_id": bill.id,
                "patient_id": bill.patient_id,
                "medical_record_id": bill.medical_record_id,
                "insurance_card_no": patient_data.get("insurance_card_no"),  # 需要从患者信息中获取
                "insurance_type": self._determine_insurance_type(patient_data),  # 根据患者信息判断
                "total_amount": bill.total_amount or Decimal("0"),
                "insurance_amount": bill.insurance_amount or Decimal("0"),
                "personal_amount": (bill.total_amount or Decimal("0")) - (bill.insurance_amount or Decimal("0")),
                "reimbursement_ratio": self._calculate_reimbursement_ratio(
                    bill.total_amount or Decimal("0"),
                    bill.insurance_amount or Decimal("0")
                ),
                "status": "pending",  # 初始状态为pending
                "settlement_details": self._build_settlement_details(bill, medical_record),
            }
            
            logger.info(f"从账单采集医保结算数据: bill_id={bill_id}, total_amount={settlement_data['total_amount']}")
            
            return settlement_data
            
        except Exception as e:
            logger.error(f"从账单采集医保结算数据失败: bill_id={bill_id}, error={str(e)}")
            raise
    
    def _determine_insurance_type(self, patient_data: Dict[str, Any]) -> Optional[str]:
        """
        根据患者信息判断医保类型
        
        Args:
            patient_data: 患者数据（已解密）
        
        Returns:
            Optional[str]: 医保类型
        """
        # TODO: 根据实际业务规则判断医保类型
        # 可以从患者信息中的insurance_type字段获取，或者根据其他规则判断
        return patient_data.get("insurance_type") or "职工医保"
    
    def _calculate_reimbursement_ratio(
        self,
        total_amount: Decimal,
        insurance_amount: Decimal
    ) -> Optional[Decimal]:
        """
        计算报销比例
        
        Args:
            total_amount: 总金额
            insurance_amount: 医保支付金额
        
        Returns:
            Optional[Decimal]: 报销比例（0-1之间）
        """
        if total_amount and total_amount > 0:
            return insurance_amount / total_amount
        return None
    
    def _build_settlement_details(
        self,
        bill: Bill,
        medical_record: Optional[MedicalRecord]
    ) -> Dict[str, Any]:
        """
        构建结算明细
        
        Args:
            bill: 账单对象
            medical_record: 病历对象（可选）
        
        Returns:
            Dict[str, Any]: 结算明细
        """
        details = {
            "bill_no": bill.bill_no,
            "bill_type": bill.bill_type,
            "items": [],
            "diagnosis": None,
            "prescription": None,
        }
        
        # 获取账单明细
        if hasattr(bill, 'bill_items') and bill.bill_items:
            details["items"] = [
                {
                    "item_name": item.item_name,
                    "quantity": float(item.quantity) if item.quantity else 0,
                    "unit_price": float(item.unit_price) if item.unit_price else 0,
                    "total_price": float(item.total_price) if item.total_price else 0,
                }
                for item in bill.bill_items
            ]
        elif bill.items:
            # 如果items是JSON字段
            if isinstance(bill.items, list):
                details["items"] = bill.items
            elif isinstance(bill.items, dict):
                details["items"] = [bill.items]
        
        # 获取诊断信息
        if medical_record:
            details["diagnosis"] = {
                "chief_complaint": medical_record.chief_complaint,
                "diagnosis": medical_record.diagnosis,
                "treatment_plan": medical_record.treatment_plan,
            }
            
            # 获取处方信息
            if hasattr(medical_record, 'prescriptions') and medical_record.prescriptions:
                prescription = medical_record.prescriptions[0]  # 取第一个处方
                details["prescription"] = {
                    "prescription_no": prescription.prescription_no,
                    "prescription_type": prescription.prescription_type,
                    "total_amount": float(prescription.total_amount) if prescription.total_amount else 0,
                }
        
        return details
    
    def collect_violation_data(
        self,
        bill_id: str,
        violation_type: str,
        violation_data: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        采集违规数据
        
        Args:
            bill_id: 账单ID
            violation_type: 违规类型
            violation_data: 违规数据
            tenant_id: 租户ID
        
        Returns:
            Dict[str, Any]: 违规记录数据
        """
        try:
            # 获取账单信息
            bill = self.payment_service.get_bill(bill_id, tenant_id)
            
            violation_record_data = {
                "bill_id": bill.id if bill else None,
                "patient_id": bill.patient_id if bill else None,
                "medical_record_id": bill.medical_record_id if bill else None,
                "violation_type": violation_type,
                "violation_level": violation_data.get("violation_level", "medium"),
                "violation_desc": violation_data.get("violation_desc", ""),
                "violation_amount": violation_data.get("violation_amount"),
                "policy_id": violation_data.get("policy_id"),
                "rule_name": violation_data.get("rule_name"),
                "rule_description": violation_data.get("rule_description"),
                "violation_data": violation_data.get("violation_data", {}),
                "status": "detected",
            }
            
            logger.warning(f"采集违规数据: bill_id={bill_id}, violation_type={violation_type}")
            
            return violation_record_data
            
        except Exception as e:
            logger.error(f"采集违规数据失败: bill_id={bill_id}, error={str(e)}")
            raise
    
    def collect_batch_settlement_data(
        self,
        bill_ids: List[str],
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """
        批量采集医保结算数据
        
        Args:
            bill_ids: 账单ID列表
            tenant_id: 租户ID
        
        Returns:
            List[Dict[str, Any]]: 医保结算数据列表
        """
        settlement_data_list = []
        
        for bill_id in bill_ids:
            try:
                settlement_data = self.collect_settlement_data_from_bill(bill_id, tenant_id)
                settlement_data_list.append(settlement_data)
            except Exception as e:
                logger.error(f"批量采集失败，跳过账单: bill_id={bill_id}, error={str(e)}")
                continue
        
        logger.info(f"批量采集完成: 总数={len(bill_ids)}, 成功={len(settlement_data_list)}")
        
        return settlement_data_list

