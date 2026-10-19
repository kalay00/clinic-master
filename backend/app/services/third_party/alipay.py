"""
支付宝支付服务适配器
"""
import json
from typing import Dict, Any, Optional

from app.core.logger import logger

# 尝试导入支付宝SDK（如果未安装，使用简化实现）
try:
    from alipay import AliPay
    from alipay.utils import AliPayConfig
    ALIPAY_SDK_AVAILABLE = True
except ImportError:
    ALIPAY_SDK_AVAILABLE = False
    logger.warning("支付宝SDK未安装，使用简化实现")


class AlipayAdapter:
    """支付宝支付适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化适配器
        
        Args:
            config: 配置数据（已解密）
        """
        self.config = config
        self.app_id = config.get("app_id")
        self.app_private_key = config.get("app_private_key")
        self.alipay_public_key = config.get("alipay_public_key")
        self.sign_type = config.get("sign_type", "RSA2")
        self.gateway_url = config.get("gateway_url", "https://openapi.alipay.com/gateway.do")
        
        # 创建支付宝客户端（如果SDK可用）
        if ALIPAY_SDK_AVAILABLE:
            try:
                self.alipay = AliPay(
                    appid=self.app_id,
                    app_notify_url=config.get("notify_url"),
                    app_private_key_string=self.app_private_key,
                    alipay_public_key_string=self.alipay_public_key,
                    sign_type=self.sign_type,
                    debug=config.get("debug", False),
                    config=AliPayConfig(timeout=15)
                )
            except Exception as e:
                logger.warning(f"支付宝客户端初始化失败: {str(e)}")
                self.alipay = None
        else:
            self.alipay = None
    
    def create_payment(
        self,
        out_trade_no: str,
        total_amount: float,
        subject: str,
        return_url: Optional[str] = None,
        notify_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建支付订单
        
        Args:
            out_trade_no: 商户订单号
            total_amount: 订单金额
            subject: 订单标题
            return_url: 支付成功返回URL
            notify_url: 支付结果通知URL
        
        Returns:
            Dict[str, Any]: 支付结果（包含支付URL或二维码）
        """
        try:
            if not self.alipay:
                # 简化实现（用于测试）
                logger.warning("支付宝SDK未安装，返回模拟结果")
                return {
                    "success": True,
                    "pay_url": f"{self.gateway_url}?out_trade_no={out_trade_no}",
                    "order_string": f"out_trade_no={out_trade_no}",
                    "out_trade_no": out_trade_no,
                    "message": "模拟支付URL（请配置支付宝SDK）"
                }
            
            # 创建订单
            order_string = self.alipay.api_alipay_trade_page_pay(
                out_trade_no=out_trade_no,
                total_amount=str(total_amount),
                subject=subject,
                return_url=return_url or self.config.get("return_url"),
                notify_url=notify_url or self.config.get("notify_url")
            )
            
            # 生成支付URL
            pay_url = f"{self.gateway_url}?{order_string}"
            
            return {
                "success": True,
                "pay_url": pay_url,
                "order_string": order_string,
                "out_trade_no": out_trade_no
            }
        
        except Exception as e:
            logger.error(f"支付宝创建支付失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建支付失败: {str(e)}"
            }
    
    def verify_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证支付回调
        
        Args:
            callback_data: 回调数据
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 验证签名
            sign = callback_data.get("sign")
            if not sign:
                return {
                    "success": False,
                    "message": "缺少签名"
                }
            
            # 移除sign和sign_type，验证签名
            verify_data = {k: v for k, v in callback_data.items() if k not in ["sign", "sign_type"]}
            
            is_valid = self.alipay.verify(verify_data, sign)
            
            if is_valid:
                return {
                    "success": True,
                    "trade_no": callback_data.get("trade_no"),
                    "out_trade_no": callback_data.get("out_trade_no"),
                    "total_amount": callback_data.get("total_amount"),
                    "trade_status": callback_data.get("trade_status")
                }
            else:
                return {
                    "success": False,
                    "message": "签名验证失败"
                }
        
        except Exception as e:
            logger.error(f"支付宝回调验证失败: {str(e)}")
            return {
                "success": False,
                "message": f"验证失败: {str(e)}"
            }
    
    def query_order(self, out_trade_no: str) -> Dict[str, Any]:
        """
        查询订单状态
        
        Args:
            out_trade_no: 商户订单号
        
        Returns:
            Dict[str, Any]: 订单信息
        """
        try:
            result = self.alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
            
            if result.get("code") == "10000":
                return {
                    "success": True,
                    "trade_no": result.get("trade_no"),
                    "out_trade_no": result.get("out_trade_no"),
                    "trade_status": result.get("trade_status"),
                    "total_amount": result.get("total_amount")
                }
            else:
                return {
                    "success": False,
                    "message": result.get("msg", "查询失败")
                }
        
        except Exception as e:
            logger.error(f"支付宝查询订单失败: {str(e)}")
            return {
                "success": False,
                "message": f"查询失败: {str(e)}"
            }

