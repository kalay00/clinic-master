"""
银联支付服务适配器
"""
import json
import hashlib
import base64
from typing import Dict, Any, Optional
import requests

from app.core.logger import logger

# 尝试导入加密库（如果未安装，使用简化实现）
try:
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pkcs1_15
    from Crypto.Hash import SHA256
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("加密库未安装，使用简化签名实现")


class UnionPayAdapter:
    """银联支付适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化适配器
        
        Args:
            config: 配置数据（已解密）
        """
        self.config = config
        self.mer_id = config.get("mer_id")
        self.mer_key = config.get("mer_key")
        self.gateway_url = config.get("gateway_url", "https://gateway.95516.com/gateway/api/order.do")
        self.version = config.get("version", "5.1.0")
    
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
            total_amount: 订单金额（元）
            subject: 订单标题
            return_url: 支付成功返回URL
            notify_url: 支付结果通知URL
        
        Returns:
            Dict[str, Any]: 支付结果（包含支付URL或表单）
        """
        try:
            # 构建请求参数
            params = {
                "version": self.version,
                "encoding": "UTF-8",
                "signMethod": "01",  # RSA
                "txnType": "01",  # 消费
                "txnSubType": "01",  # 消费
                "bizType": "000201",  # B2C
                "channelType": "07",  # PC
                "merId": self.mer_id,
                "orderId": out_trade_no,
                "txnTime": self._get_txn_time(),
                "txnAmt": str(int(total_amount * 100)),  # 转换为分
                "currencyCode": "156",  # 人民币
                "orderDesc": subject,
                "frontUrl": return_url or self.config.get("return_url"),
                "backUrl": notify_url or self.config.get("notify_url"),
            }
            
            # 生成签名
            params["signature"] = self._generate_sign(params)
            
            # 发送请求
            response = requests.post(
                self.gateway_url,
                data=params,
                timeout=30
            )
            
            # 解析响应
            result = self._parse_response(response.text)
            
            if result.get("respCode") == "00":
                # 支付成功，返回支付URL或表单
                return {
                    "success": True,
                    "pay_url": result.get("payUrl"),
                    "html_form": result.get("html"),
                    "out_trade_no": out_trade_no
                }
            else:
                return {
                    "success": False,
                    "message": result.get("respMsg", "创建支付失败")
                }
        
        except Exception as e:
            logger.error(f"银联支付创建支付失败: {str(e)}")
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
            signature = callback_data.pop("signature", None)
            if not signature:
                return {
                    "success": False,
                    "message": "缺少签名"
                }
            
            is_valid = self._verify_sign(callback_data, signature)
            
            if is_valid:
                return {
                    "success": True,
                    "orderId": callback_data.get("orderId"),
                    "queryId": callback_data.get("queryId"),
                    "txnAmt": callback_data.get("txnAmt"),
                    "respCode": callback_data.get("respCode")
                }
            else:
                return {
                    "success": False,
                    "message": "签名验证失败"
                }
        
        except Exception as e:
            logger.error(f"银联支付回调验证失败: {str(e)}")
            return {
                "success": False,
                "message": f"验证失败: {str(e)}"
            }
    
    def _get_txn_time(self) -> str:
        """获取交易时间（YYYYMMDDHHmmss格式）"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d%H%M%S")
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 排序并拼接
        sorted_params = sorted([(k, v) for k, v in params.items() if v and k != "signature"])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 使用RSA私钥签名（这里简化处理，实际需要使用证书）
        # 注意：银联签名需要使用RSA私钥，这里仅为示例
        try:
            # 如果有私钥文件，使用私钥签名
            if hasattr(self, '_private_key'):
                hash_obj = SHA256.new(sign_str.encode('utf-8'))
                signature = pkcs1_15.new(self._private_key).sign(hash_obj)
                return base64.b64encode(signature).decode('utf-8')
            else:
                # 简化处理：使用MD5（实际应该使用RSA）
                return hashlib.md5(f"{sign_str}&key={self.mer_key}".encode('utf-8')).hexdigest().upper()
        except Exception as e:
            logger.error(f"签名生成失败: {str(e)}")
            # 简化处理：使用MD5
            return hashlib.md5(f"{sign_str}&key={self.mer_key}".encode('utf-8')).hexdigest().upper()
    
    def _verify_sign(self, params: Dict[str, Any], signature: str) -> bool:
        """验证签名"""
        # 排序并拼接
        sorted_params = sorted([(k, v) for k, v in params.items() if v and k != "signature"])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # 验证签名（简化处理）
        calculated_sign = hashlib.md5(f"{sign_str}&key={self.mer_key}".encode('utf-8')).hexdigest().upper()
        return signature.upper() == calculated_sign
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析响应"""
        # 银联返回的是键值对格式
        result = {}
        for line in response_text.split('&'):
            if '=' in line:
                key, value = line.split('=', 1)
                result[key] = value
        return result

