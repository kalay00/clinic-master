"""
监管事件处理器：监听业务事件并触发数据采集
v2.0新增功能
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.services.medical_insurance_data_collector import MedicalInsuranceDataCollector
from app.services.medical_insurance_data_validator import MedicalInsuranceDataValidator
from app.services.medical_insurance_regulatory_service import MedicalInsuranceRegulatoryService
from app.core.audit_enhanced import regulatory_audit_service
from app.core.logger import logger
from app.core.exceptions import BusinessException


class RegulatoryEventHandler:
    """监管事件处理器类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_collector = MedicalInsuranceDataCollector(db)
        self.data_validator = MedicalInsuranceDataValidator(db)
        self.regulatory_service = MedicalInsuranceRegulatoryService(db)
    
    async def handle_bill_paid_event(
        self,
        bill_id: str,
        tenant_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        处理账单支付事件
        
        当账单支付完成时，自动采集医保结算数据
        
        Args:
            bill_id: 账单ID
            tenant_id: 租户ID
            user_id: 操作用户ID
        
        Returns:
            Optional[Dict[str, Any]]: 创建的结算记录信息，如果失败返回None
        """
        try:
            logger.info(f"处理账单支付事件: bill_id={bill_id}")
            
            # 1. 采集医保结算数据
            settlement_data = self.data_collector.collect_settlement_data_from_bill(
                bill_id, tenant_id
            )
            
            # 2. 验证数据
            is_valid, error_message, validated_data = self.data_validator.validate_settlement_data(
                settlement_data, tenant_id
            )
            
            if not is_valid:
                logger.warning(f"医保结算数据验证失败: bill_id={bill_id}, error={error_message}")
                
                # 记录验证失败日志
                await regulatory_audit_service.log_regulatory_operation(
                    user_id=user_id,
                    regulatory_type="medical_insurance",
                    operation_type="data_validation",
                    resource_type="medical_insurance_settlement",
                    resource_id=bill_id,
                    operation_desc=f"数据验证失败: {error_message}",
                    request_ip=None,
                    risk_level="medium",
                    db=self.db
                )
                
                return None
            
            # 3. 创建医保结算记录
            settlement = self.regulatory_service.create_settlement(
                validated_data, tenant_id, user_id
            )
            
            # 4. 记录操作日志
            await regulatory_audit_service.log_regulatory_operation(
                user_id=user_id,
                regulatory_type="medical_insurance",
                operation_type="data_collection",
                resource_type="medical_insurance_settlement",
                resource_id=str(settlement.id),
                operation_desc=f"从账单采集医保结算数据: {bill_id}",
                request_ip=None,
                risk_level="low",
                db=self.db
            )
            
            logger.info(f"医保结算数据采集成功: settlement_id={settlement.id}, bill_id={bill_id}")
            
            return {
                "settlement_id": str(settlement.id),
                "settlement_no": settlement.settlement_no,
                "status": settlement.status,
            }
            
        except BusinessException as e:
            logger.warning(f"处理账单支付事件失败（业务异常）: bill_id={bill_id}, error={str(e)}")
            return None
        except Exception as e:
            logger.error(f"处理账单支付事件失败: bill_id={bill_id}, error={str(e)}", exc_info=True)
            return None
    
    async def handle_violation_detected_event(
        self,
        bill_id: str,
        violation_type: str,
        violation_data: Dict[str, Any],
        tenant_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        处理违规检测事件
        
        当检测到违规时，自动创建违规记录
        
        Args:
            bill_id: 账单ID
            violation_type: 违规类型
            violation_data: 违规数据
            tenant_id: 租户ID
            user_id: 操作用户ID
        
        Returns:
            Optional[Dict[str, Any]]: 创建的违规记录信息，如果失败返回None
        """
        try:
            logger.warning(f"处理违规检测事件: bill_id={bill_id}, violation_type={violation_type}")
            
            # 1. 验证违规数据
            is_valid, error_message = self.data_validator.validate_violation_data(violation_data)
            
            if not is_valid:
                logger.warning(f"违规数据验证失败: bill_id={bill_id}, error={error_message}")
                return None
            
            # 2. 采集违规数据
            violation_record_data = self.data_collector.collect_violation_data(
                bill_id, violation_type, violation_data, tenant_id
            )
            
            # 3. 创建违规记录
            violation = self.regulatory_service.create_violation(
                violation_record_data, tenant_id, user_id
            )
            
            # 4. 记录操作日志
            await regulatory_audit_service.log_violation_detection(
                user_id=user_id,
                regulatory_type="medical_insurance",
                violation_type=violation_type,
                violation_data=violation_data,
                request_ip=None,
                db=self.db
            )
            
            logger.warning(f"违规记录创建成功: violation_id={violation.id}, bill_id={bill_id}")
            
            return {
                "violation_id": str(violation.id),
                "violation_no": violation.violation_no,
                "violation_type": violation.violation_type,
                "violation_level": violation.violation_level,
                "status": violation.status,
            }
            
        except Exception as e:
            logger.error(f"处理违规检测事件失败: bill_id={bill_id}, error={str(e)}", exc_info=True)
            return None
    
    async def handle_batch_settlement_collection(
        self,
        bill_ids: list,
        tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        处理批量结算数据采集
        
        Args:
            bill_ids: 账单ID列表
            tenant_id: 租户ID
            user_id: 操作用户ID
        
        Returns:
            Dict[str, Any]: 采集结果统计
        """
        try:
            logger.info(f"处理批量结算数据采集: 账单数量={len(bill_ids)}")
            
            success_count = 0
            failure_count = 0
            settlement_ids = []
            
            for bill_id in bill_ids:
                result = await self.handle_bill_paid_event(bill_id, tenant_id, user_id)
                if result:
                    success_count += 1
                    settlement_ids.append(result["settlement_id"])
                else:
                    failure_count += 1
            
            # 记录批量操作日志
            await regulatory_audit_service.log_regulatory_operation(
                user_id=user_id,
                regulatory_type="medical_insurance",
                operation_type="batch_data_collection",
                resource_type="medical_insurance_settlement",
                operation_desc=f"批量采集医保结算数据: 总数={len(bill_ids)}, 成功={success_count}, 失败={failure_count}",
                request_ip=None,
                risk_level="low",
                db=self.db
            )
            
            logger.info(f"批量结算数据采集完成: 成功={success_count}, 失败={failure_count}")
            
            return {
                "total": len(bill_ids),
                "success": success_count,
                "failure": failure_count,
                "settlement_ids": settlement_ids,
            }
            
        except Exception as e:
            logger.error(f"处理批量结算数据采集失败: error={str(e)}", exc_info=True)
            raise

