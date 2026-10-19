"""
医保数据上报服务：向监管系统上报医保数据
v2.0新增功能
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import BusinessException
from app.services.medical_insurance_data_encryptor import MedicalInsuranceDataEncryptor
from app.services.medical_insurance_regulatory_service import MedicalInsuranceRegulatoryService
from app.core.audit_enhanced import regulatory_audit_service


class MedicalInsuranceDataReporter:
    """医保数据上报服务类"""
    
    def __init__(self, db=None):
        """
        初始化医保数据上报服务
        
        Args:
            db: 数据库会话（可选）
        """
        self.db = db
        self.encryptor = MedicalInsuranceDataEncryptor()
        self.regulatory_service = MedicalInsuranceRegulatoryService(db) if db else None
        
        # 配置HTTP客户端（支持重试）
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 上报接口配置（从配置或环境变量获取）
        self.report_url = getattr(settings, "MEDICAL_INSURANCE_REPORT_URL", "https://api.medical-insurance.gov.cn/v1/report")
        self.report_api_key = getattr(settings, "MEDICAL_INSURANCE_API_KEY", "")
        self.report_timeout = getattr(settings, "MEDICAL_INSURANCE_REPORT_TIMEOUT", 30)
    
    async def report_settlement(
        self,
        settlement_id: str,
        tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        上报医保结算数据
        
        Args:
            settlement_id: 结算记录ID
            tenant_id: 租户ID
            user_id: 操作用户ID
        
        Returns:
            Dict[str, Any]: 上报结果
        """
        try:
            if not self.regulatory_service:
                raise BusinessException("数据库会话未初始化")
            
            # 1. 获取结算记录
            settlement = self.regulatory_service.get_settlement(settlement_id, tenant_id)
            
            # 2. 构建上报数据
            settlement_data = {
                "settlement_no": settlement.settlement_no,
                "patient_id": str(settlement.patient_id),
                "insurance_card_no": settlement.insurance_card_no,
                "insurance_type": settlement.insurance_type,
                "total_amount": float(settlement.total_amount) if settlement.total_amount else 0,
                "insurance_amount": float(settlement.insurance_amount) if settlement.insurance_amount else 0,
                "personal_amount": float(settlement.personal_amount) if settlement.personal_amount else 0,
                "reimbursement_ratio": float(settlement.reimbursement_ratio) if settlement.reimbursement_ratio else None,
                "settlement_time": settlement.settlement_time.isoformat() if settlement.settlement_time else None,
                "settlement_details": settlement.settlement_details or {},
            }
            
            # 3. 加密数据
            encrypted_data = self.encryptor.encrypt_settlement_data(settlement_data)
            
            # 4. 上报数据
            report_result = self._send_report_request(encrypted_data)
            
            # 5. 更新结算记录的上报状态
            update_data = {
                "reported_at": datetime.now(),
                "report_status": "success" if report_result.get("success") else "failed",
                "report_error": None if report_result.get("success") else report_result.get("error_message"),
            }
            self.regulatory_service.update_settlement(
                settlement_id, update_data, tenant_id, user_id
            )
            
            # 6. 记录上报日志
            if self.db:
                await regulatory_audit_service.log_data_report(
                    user_id=user_id,
                    regulatory_type="medical_insurance",
                    report_type="settlement",
                    report_data={"settlement_id": settlement_id, "settlement_no": settlement.settlement_no},
                    report_status="success" if report_result.get("success") else "failed",
                    request_ip=None,
                    db=self.db
                )
            
            logger.info(f"医保结算数据上报完成: settlement_id={settlement_id}, success={report_result.get('success')}")
            
            return report_result
            
        except Exception as e:
            logger.error(f"上报医保结算数据失败: settlement_id={settlement_id}, error={str(e)}")
            
            # 更新上报状态为失败
            if self.regulatory_service:
                try:
                    update_data = {
                        "report_status": "failed",
                        "report_error": str(e),
                    }
                    self.regulatory_service.update_settlement(
                        settlement_id, update_data, tenant_id, user_id
                    )
                except Exception:
                    pass
            
            # 记录上报失败日志
            try:
                if self.db:
                    await regulatory_audit_service.log_data_report(
                        user_id=user_id,
                        regulatory_type="medical_insurance",
                        report_type="settlement",
                        report_data={"settlement_id": settlement_id},
                        report_status="failed",
                        request_ip=None,
                        db=self.db
                    )
            except Exception:
                pass
            
            raise BusinessException(f"上报医保结算数据失败: {str(e)}")
    
    def _send_report_request(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        发送上报请求
        
        Args:
            data: 上报数据
        
        Returns:
            Dict[str, Any]: 上报结果
        """
        try:
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.report_api_key}",
            }
            
            # 发送POST请求
            response = self.session.post(
                self.report_url,
                json=data,
                headers=headers,
                timeout=self.report_timeout,
                verify=True  # 验证SSL证书
            )
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response_data": result,
                    "message": "上报成功",
                }
            else:
                error_message = f"上报失败: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", error_message)
                except Exception:
                    error_message = f"{error_message}: {response.text}"
                
                return {
                    "success": False,
                    "error_message": error_message,
                    "status_code": response.status_code,
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error_message": "上报请求超时",
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error_message": "无法连接到上报服务器",
            }
        except Exception as e:
            return {
                "success": False,
                "error_message": f"上报请求异常: {str(e)}",
            }
    
    async def report_batch_settlements(
        self,
        settlement_ids: List[str],
        tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        批量上报医保结算数据
        
        Args:
            settlement_ids: 结算记录ID列表
            tenant_id: 租户ID
            user_id: 操作用户ID
        
        Returns:
            Dict[str, Any]: 批量上报结果统计
        """
        success_count = 0
        failure_count = 0
        results = []
        
        for settlement_id in settlement_ids:
            try:
                result = await self.report_settlement(settlement_id, tenant_id, user_id)
                if result.get("success"):
                    success_count += 1
                else:
                    failure_count += 1
                results.append({
                    "settlement_id": settlement_id,
                    "success": result.get("success"),
                    "error": result.get("error_message"),
                })
            except Exception as e:
                failure_count += 1
                results.append({
                    "settlement_id": settlement_id,
                    "success": False,
                    "error": str(e),
                })
                logger.error(f"批量上报失败，跳过该条数据: settlement_id={settlement_id}, error={str(e)}")
        
        logger.info(f"批量上报完成: 总数={len(settlement_ids)}, 成功={success_count}, 失败={failure_count}")
        
        return {
            "total": len(settlement_ids),
            "success": success_count,
            "failure": failure_count,
            "results": results,
        }

