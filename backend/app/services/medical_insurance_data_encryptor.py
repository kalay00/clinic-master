"""
医保数据加密服务：对上报数据进行加密
v2.0新增功能
"""
from typing import Dict, Any, Optional
import json
from datetime import datetime

from app.core.encryption import EncryptionService
from app.core.logger import logger
from app.core.exceptions import BusinessException


class MedicalInsuranceDataEncryptor:
    """医保数据加密服务类"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        初始化医保数据加密服务
        
        Args:
            encryption_key: 加密密钥（如果不提供，使用默认密钥）
        """
        self.encryption_service = EncryptionService(key=encryption_key)
    
    def encrypt_settlement_data(
        self,
        settlement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        加密医保结算数据
        
        Args:
            settlement_data: 医保结算数据
        
        Returns:
            Dict[str, Any]: 加密后的数据
        """
        try:
            # 构建需要加密的敏感字段
            sensitive_fields = {
                "patient_id": str(settlement_data.get("patient_id", "")),
                "insurance_card_no": settlement_data.get("insurance_card_no", ""),
                "patient_name": settlement_data.get("patient_name", ""),
                "patient_id_card": settlement_data.get("patient_id_card", ""),
            }
            
            # 将敏感字段转换为JSON字符串并加密
            sensitive_json = json.dumps(sensitive_fields, ensure_ascii=False)
            encrypted_sensitive = self.encryption_service.encrypt(sensitive_json)
            
            # 构建加密后的数据
            encrypted_data = {
                "settlement_no": settlement_data.get("settlement_no"),
                "encrypted_sensitive_data": encrypted_sensitive,
                "total_amount": float(settlement_data.get("total_amount", 0)),
                "insurance_amount": float(settlement_data.get("insurance_amount", 0)),
                "personal_amount": float(settlement_data.get("personal_amount", 0)),
                "reimbursement_ratio": float(settlement_data.get("reimbursement_ratio", 0)) if settlement_data.get("reimbursement_ratio") else None,
                "insurance_type": settlement_data.get("insurance_type"),
                "settlement_time": settlement_data.get("settlement_time").isoformat() if settlement_data.get("settlement_time") else None,
                "settlement_details": settlement_data.get("settlement_details", {}),
                "encrypted_at": datetime.now().isoformat(),
            }
            
            logger.info(f"医保结算数据加密成功: settlement_no={encrypted_data.get('settlement_no')}")
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"加密医保结算数据失败: {str(e)}")
            raise BusinessException(f"加密医保结算数据失败: {str(e)}")
    
    def decrypt_settlement_data(
        self,
        encrypted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        解密医保结算数据
        
        Args:
            encrypted_data: 加密后的数据
        
        Returns:
            Dict[str, Any]: 解密后的数据
        """
        try:
            # 解密敏感字段
            encrypted_sensitive = encrypted_data.get("encrypted_sensitive_data")
            if not encrypted_sensitive:
                raise BusinessException("缺少加密的敏感数据")
            
            sensitive_json = self.encryption_service.decrypt(encrypted_sensitive)
            sensitive_fields = json.loads(sensitive_json)
            
            # 构建解密后的数据
            decrypted_data = {
                "settlement_no": encrypted_data.get("settlement_no"),
                "patient_id": sensitive_fields.get("patient_id"),
                "insurance_card_no": sensitive_fields.get("insurance_card_no"),
                "patient_name": sensitive_fields.get("patient_name"),
                "patient_id_card": sensitive_fields.get("patient_id_card"),
                "total_amount": encrypted_data.get("total_amount"),
                "insurance_amount": encrypted_data.get("insurance_amount"),
                "personal_amount": encrypted_data.get("personal_amount"),
                "reimbursement_ratio": encrypted_data.get("reimbursement_ratio"),
                "insurance_type": encrypted_data.get("insurance_type"),
                "settlement_time": encrypted_data.get("settlement_time"),
                "settlement_details": encrypted_data.get("settlement_details", {}),
            }
            
            logger.info(f"医保结算数据解密成功: settlement_no={decrypted_data.get('settlement_no')}")
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"解密医保结算数据失败: {str(e)}")
            raise BusinessException(f"解密医保结算数据失败: {str(e)}")
    
    def encrypt_batch_settlement_data(
        self,
        settlement_data_list: list
    ) -> list:
        """
        批量加密医保结算数据
        
        Args:
            settlement_data_list: 医保结算数据列表
        
        Returns:
            list: 加密后的数据列表
        """
        encrypted_list = []
        
        for settlement_data in settlement_data_list:
            try:
                encrypted_data = self.encrypt_settlement_data(settlement_data)
                encrypted_list.append(encrypted_data)
            except Exception as e:
                logger.error(f"批量加密失败，跳过该条数据: {str(e)}")
                continue
        
        logger.info(f"批量加密完成: 总数={len(settlement_data_list)}, 成功={len(encrypted_list)}")
        
        return encrypted_list

