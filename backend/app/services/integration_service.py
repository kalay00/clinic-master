"""
对接服务：医保对接、支付对接、微信对接
支持使用第三方服务配置
"""
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.services.third_party_config_service import ThirdPartyConfigService
from app.services.third_party.alipay import AlipayAdapter
from app.services.third_party.wechat_pay import WeChatPayAdapter
from app.services.third_party.unionpay import UnionPayAdapter


class IntegrationService:
    """对接服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_service = ThirdPartyConfigService(db)
    
    def medical_insurance_verify(
        self,
        patient_id: str,
        id_card: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        医保验证
        
        Args:
            patient_id: 患者ID
            id_card: 身份证号
            tenant_id: 租户ID
        
        Returns:
            Dict[str, Any]: 医保验证结果
        """
        # TODO: 实现医保系统对接
        logger.info(f"医保验证: patient_id={patient_id}, tenant_id={tenant_id}")
        
        return {
            "verified": True,
            "insurance_type": "basic",  # basic/employee/resident
            "balance": 0.0,
            "coverage_rate": 0.8,  # 报销比例
        }
    
    def medical_insurance_pay(
        self,
        bill_id: str,
        amount: float,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        医保支付
        
        Args:
            bill_id: 账单ID
            amount: 支付金额
            tenant_id: 租户ID
        
        Returns:
            Dict[str, Any]: 支付结果
        """
        # TODO: 实现医保支付对接
        logger.info(f"医保支付: bill_id={bill_id}, amount={amount}, tenant_id={tenant_id}")
        
        return {
            "success": True,
            "transaction_id": f"INS{bill_id[:8]}",
            "paid_amount": amount,
        }
    
    def wechat_pay(
        self,
        bill_id: str,
        amount: float,
        tenant_id: str,
        openid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        微信支付
        
        Args:
            bill_id: 账单ID
            amount: 支付金额（元）
            tenant_id: 租户ID
            openid: 微信OpenID（可选，JSAPI支付需要）
        
        Returns:
            Dict[str, Any]: 支付结果（包含支付二维码）
        """
        try:
            # 尝试获取租户的微信支付配置
            config_data = self.config_service.get_config(UUID(tenant_id), "wechat_pay")
            
            if config_data and config_data.get("is_enabled"):
                # 使用微信支付
                adapter = WeChatPayAdapter(config_data["config_data"])
                result = adapter.create_payment(
                    out_trade_no=bill_id,
                    total_amount=int(amount * 100),  # 转换为分
                    description=f"账单支付-{bill_id}",
                    openid=openid
                )
                
                if result.get("success"):
                    logger.info(f"微信支付创建成功: bill_id={bill_id}")
                    return result
                else:
                    logger.error(f"微信支付创建失败: {result.get('message')}")
                    return result
            
            # 如果没有配置或未启用，返回框架结果
            logger.warning(f"微信支付未配置，使用框架模式: tenant_id={tenant_id}")
            return {
                "success": True,
                "transaction_id": f"WX{bill_id[:8]}",
                "qr_code": f"weixin://wxpay/bizpayurl?pr={bill_id[:8]}",
                "prepay_id": f"prepay_{bill_id[:8]}",
                "message": "请配置微信支付参数"
            }
        
        except Exception as e:
            logger.error(f"微信支付失败: {str(e)}")
            return {
                "success": False,
                "message": f"微信支付失败: {str(e)}"
            }
    
    def alipay_pay(
        self,
        bill_id: str,
        amount: float,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        支付宝支付
        
        Args:
            bill_id: 账单ID
            amount: 支付金额（元）
            tenant_id: 租户ID
        
        Returns:
            Dict[str, Any]: 支付结果（包含支付链接）
        """
        try:
            # 尝试获取租户的支付宝配置
            config_data = self.config_service.get_config(UUID(tenant_id), "alipay")
            
            if config_data and config_data.get("is_enabled"):
                # 使用支付宝支付
                adapter = AlipayAdapter(config_data["config_data"])
                result = adapter.create_payment(
                    out_trade_no=bill_id,
                    total_amount=amount,
                    subject=f"账单支付-{bill_id}"
                )
                
                if result.get("success"):
                    logger.info(f"支付宝支付创建成功: bill_id={bill_id}")
                    return result
                else:
                    logger.error(f"支付宝支付创建失败: {result.get('message')}")
                    return result
            
            # 如果没有配置或未启用，返回框架结果
            logger.warning(f"支付宝支付未配置，使用框架模式: tenant_id={tenant_id}")
            return {
                "success": True,
                "transaction_id": f"ALI{bill_id[:8]}",
                "pay_url": f"https://openapi.alipay.com/gateway.do?bill_id={bill_id}",
                "message": "请配置支付宝支付参数"
            }
        
        except Exception as e:
            logger.error(f"支付宝支付失败: {str(e)}")
            return {
                "success": False,
                "message": f"支付宝支付失败: {str(e)}"
            }
    
    def unionpay_pay(
        self,
        bill_id: str,
        amount: float,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        银联支付
        
        Args:
            bill_id: 账单ID
            amount: 支付金额（元）
            tenant_id: 租户ID
        
        Returns:
            Dict[str, Any]: 支付结果（包含支付URL或表单）
        """
        try:
            # 尝试获取租户的银联支付配置
            config_data = self.config_service.get_config(UUID(tenant_id), "unionpay")
            
            if config_data and config_data.get("is_enabled"):
                # 使用银联支付
                adapter = UnionPayAdapter(config_data["config_data"])
                result = adapter.create_payment(
                    out_trade_no=bill_id,
                    total_amount=amount,
                    subject=f"账单支付-{bill_id}"
                )
                
                if result.get("success"):
                    logger.info(f"银联支付创建成功: bill_id={bill_id}")
                    return result
                else:
                    logger.error(f"银联支付创建失败: {result.get('message')}")
                    return result
            
            # 如果没有配置或未启用，返回框架结果
            logger.warning(f"银联支付未配置，使用框架模式: tenant_id={tenant_id}")
            return {
                "success": True,
                "transaction_id": f"UNION{bill_id[:8]}",
                "pay_url": f"https://gateway.95516.com/gateway/api/order.do?bill_id={bill_id}",
                "message": "请配置银联支付参数"
            }
        
        except Exception as e:
            logger.error(f"银联支付失败: {str(e)}")
            return {
                "success": False,
                "message": f"银联支付失败: {str(e)}"
            }
    
    def wechat_auth(
        self,
        code: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        微信授权
        
        Args:
            code: 微信授权码
            tenant_id: 租户ID
        
        Returns:
            Dict[str, Any]: 授权结果（包含OpenID）
        """
        # TODO: 实现微信授权对接
        logger.info(f"微信授权: code={code}, tenant_id={tenant_id}")
        
        return {
            "success": True,
            "openid": f"openid_{code[:8]}",
            "unionid": None,
            "access_token": f"token_{code[:8]}",
        }
