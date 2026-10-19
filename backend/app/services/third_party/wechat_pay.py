"""
微信支付服务适配器
"""
import json
import time
import hashlib
import hmac
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import requests

from app.core.logger import logger

# 尝试导入微信支付SDK（如果未安装，使用简化实现）
try:
    from wechatpayv3 import WeChatPay, WeChatPayType
    WECHATPAY_SDK_AVAILABLE = True
except ImportError:
    WECHATPAY_SDK_AVAILABLE = False
    logger.warning("微信支付SDK未安装，使用简化实现")


class WeChatPayAdapter:
    """微信支付适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化适配器
        
        Args:
            config: 配置数据（已解密）
        """
        self.config = config
        self.app_id = config.get("app_id")
        self.mch_id = config.get("mch_id")
        self.api_key = config.get("api_key")
        self.app_secret = config.get("app_secret")
        self.cert_path = config.get("cert_path")
        self.key_path = config.get("key_path")
        
        # 创建微信支付客户端（使用wechatpayv3库）
        if WECHATPAY_SDK_AVAILABLE:
            try:
                self.wechatpay = WeChatPay(
                    wechatpay_type=WeChatPayType.NATIVE,
                    mchid=self.mch_id,
                    private_key_path=self.key_path,
                    cert_serial_no=config.get("cert_serial_no"),
                    appid=self.app_id,
                    notify_url=config.get("notify_url"),
                    cert_dir=config.get("cert_dir", "/tmp")
                )
            except Exception as e:
                logger.warning(f"微信支付客户端初始化失败（可能缺少证书）: {str(e)}")
                self.wechatpay = None
        else:
            self.wechatpay = None
    
    def create_payment(
        self,
        out_trade_no: str,
        total_amount: int,
        description: str,
        notify_url: Optional[str] = None,
        openid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建支付订单
        
        Args:
            out_trade_no: 商户订单号
            total_amount: 订单金额（分）
            description: 订单描述
            notify_url: 支付结果通知URL
            openid: 用户OpenID（JSAPI支付需要）
        
        Returns:
            Dict[str, Any]: 支付结果（包含支付URL、二维码或支付参数）
        """
        try:
            if not self.wechatpay:
                # 如果没有证书，使用旧版API（需要手动实现）
                return self._create_payment_v2(out_trade_no, total_amount, description, openid)
            
            # 使用新版API
            amount = {"total": total_amount, "currency": "CNY"}
            
            # 根据支付方式选择
            if openid:
                # JSAPI支付
                code, result = self.wechatpay.pay(
                    description=description,
                    out_trade_no=out_trade_no,
                    amount=amount,
                    payer={"openid": openid}
                )
            else:
                # Native支付（扫码支付）
                code, result = self.wechatpay.pay(
                    description=description,
                    out_trade_no=out_trade_no,
                    amount=amount
                )
            
            # wechatpayv3的pay方法返回(code, message)元组
            # code为200表示成功，result为包含支付信息的字典
            if code == 200 and isinstance(result, dict):
                return {
                    "success": True,
                    "pay_url": result.get("code_url"),  # Native支付返回的二维码URL
                    "prepay_id": result.get("prepay_id"),  # JSAPI支付返回的预支付ID
                    "h5_url": result.get("h5_url"),  # H5支付返回的跳转URL
                    "out_trade_no": out_trade_no
                }
            else:
                # 支付失败
                error_msg = result if isinstance(result, str) else "支付创建失败"
                logger.error(f"微信支付创建失败: code={code}, message={error_msg}")
                return {
                    "success": False,
                    "message": error_msg
                }
        
        except Exception as e:
            logger.error(f"微信支付创建支付失败: {str(e)}")
            return {
                "success": False,
                "message": f"创建支付失败: {str(e)}"
            }
    
    def _create_payment_v2(
        self,
        out_trade_no: str,
        total_amount: int,
        description: str,
        openid: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        使用旧版API创建支付（无证书情况）
        
        Args:
            out_trade_no: 商户订单号
            total_amount: 订单金额（分）
            description: 订单描述
            openid: 用户OpenID
        
        Returns:
            Dict[str, Any]: 支付结果
        """
        # 构建请求参数
        params = {
            "appid": self.app_id,
            "mch_id": self.mch_id,
            "nonce_str": self._generate_nonce_str(),
            "body": description,
            "out_trade_no": out_trade_no,
            "total_fee": total_amount,
            "spbill_create_ip": "127.0.0.1",
            "notify_url": self.config.get("notify_url"),
            "trade_type": "JSAPI" if openid else "NATIVE",
        }
        
        if openid:
            params["openid"] = openid
        
        # 生成签名
        params["sign"] = self._generate_sign(params)
        
        # 转换为XML
        xml_data = self._dict_to_xml(params)
        
        # 发送请求
        try:
            response = requests.post(
                "https://api.mch.weixin.qq.com/pay/unifiedorder",
                data=xml_data.encode("utf-8"),
                headers={"Content-Type": "application/xml"}
            )
            
            result = self._xml_to_dict(response.text)
            
            if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
                return {
                    "success": True,
                    "pay_url": result.get("code_url"),
                    "prepay_id": result.get("prepay_id"),
                    "out_trade_no": out_trade_no
                }
            else:
                return {
                    "success": False,
                    "message": result.get("return_msg", "创建支付失败")
                }
        
        except Exception as e:
            logger.error(f"微信支付请求失败: {str(e)}")
            return {
                "success": False,
                "message": f"请求失败: {str(e)}"
            }
    
    def verify_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证支付回调
        
        Args:
            callback_data: 回调数据（XML格式字符串）
        
        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 解析XML
            if isinstance(callback_data, str):
                data = self._xml_to_dict(callback_data)
            else:
                data = callback_data
            
            # 验证签名
            sign = data.pop("sign", None)
            if not sign:
                return {
                    "success": False,
                    "message": "缺少签名"
                }
            
            calculated_sign = self._generate_sign(data)
            
            if sign == calculated_sign:
                return {
                    "success": True,
                    "transaction_id": data.get("transaction_id"),
                    "out_trade_no": data.get("out_trade_no"),
                    "total_fee": data.get("total_fee"),
                    "result_code": data.get("result_code")
                }
            else:
                return {
                    "success": False,
                    "message": "签名验证失败"
                }
        
        except Exception as e:
            logger.error(f"微信支付回调验证失败: {str(e)}")
            return {
                "success": False,
                "message": f"验证失败: {str(e)}"
            }
    
    def _generate_nonce_str(self) -> str:
        """生成随机字符串"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 排序
        sorted_params = sorted([(k, v) for k, v in params.items() if v and k != "sign"])
        # 拼接
        string_a = "&".join([f"{k}={v}" for k, v in sorted_params])
        # 加上key
        string_sign_temp = f"{string_a}&key={self.api_key}"
        # MD5加密并转大写
        sign = hashlib.md5(string_sign_temp.encode("utf-8")).hexdigest().upper()
        return sign
    
    def _dict_to_xml(self, params: Dict[str, Any]) -> str:
        """字典转XML"""
        xml = "<xml>"
        for k, v in params.items():
            xml += f"<{k}><![CDATA[{v}]]></{k}>"
        xml += "</xml>"
        return xml
    
    def _xml_to_dict(self, xml_str: str) -> Dict[str, Any]:
        """XML转字典"""
        root = ET.fromstring(xml_str)
        return {child.tag: child.text for child in root}

