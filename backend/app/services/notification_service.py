"""
通知服务：短信通知、微信通知
支持使用第三方服务配置
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.mq_client import mq_client
from app.core.logger import logger
from app.services.third_party_config_service import ThirdPartyConfigService
try:
    from app.services.third_party.aliyun_sms import AliyunSMSAdapter, ALIYUN_SDK_AVAILABLE
except ImportError:
    ALIYUN_SDK_AVAILABLE = False
    AliyunSMSAdapter = None


class NotificationService:
    """通知服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_service = ThirdPartyConfigService(db)
    
    def send_sms(
        self,
        phone: str,
        message: str,
        tenant_id: str,
        template_params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        发送短信通知
        
        Args:
            phone: 手机号
            message: 消息内容
            tenant_id: 租户ID
            template_params: 模板参数（可选）
        
        Returns:
            bool: 是否成功
        """
        try:
            # 尝试获取租户的阿里云短信配置
            config_data = self.config_service.get_config(UUID(tenant_id), "aliyun_sms")
            
            if config_data and config_data.get("is_enabled") and AliyunSMSAdapter:
                # 使用阿里云短信发送
                adapter = AliyunSMSAdapter(config_data["config_data"])
                result = adapter.send_notification(phone, message)
                
                if result.get("success"):
                    logger.info(f"阿里云短信发送成功: {phone}")
                    return True
                else:
                    logger.error(f"阿里云短信发送失败: {result.get('message')}")
                    # 失败时回退到消息队列
                    return self._send_sms_via_queue(phone, message, tenant_id)
            else:
                # 如果没有配置或未启用，使用消息队列
                return self._send_sms_via_queue(phone, message, tenant_id)
        
        except Exception as e:
            logger.error(f"发送短信失败: {str(e)}")
            # 失败时回退到消息队列
            return self._send_sms_via_queue(phone, message, tenant_id)
    
    def _send_sms_via_queue(self, phone: str, message: str, tenant_id: str) -> bool:
        """通过消息队列发送短信（备用方案）"""
        try:
            notification_data = {
                "type": "sms",
                "phone": phone,
                "message": message,
                "tenant_id": tenant_id,
            }
            
            mq_client.publish(
                exchange="notifications",
                routing_key="sms.send",
                message=notification_data
            )
            
            logger.info(f"短信通知已加入队列: {phone}")
            return True
        except Exception as e:
            logger.error(f"加入消息队列失败: {str(e)}")
            return False
    
    def send_wechat(
        self,
        openid: str,
        template_id: str,
        data: Dict[str, Any],
        tenant_id: str
    ) -> bool:
        """
        发送微信通知
        
        Args:
            openid: 微信OpenID
            template_id: 模板ID
            data: 模板数据
            tenant_id: 租户ID
        
        Returns:
            bool: 是否成功
        """
        try:
            # 通过消息队列发送（异步处理）
            notification_data = {
                "type": "wechat",
                "openid": openid,
                "template_id": template_id,
                "data": data,
                "tenant_id": tenant_id,
            }
            
            mq_client.publish(
                exchange="notifications",
                routing_key="wechat.send",
                message=notification_data
            )
            
            logger.info(f"发送微信通知: {openid}")
            return True
        except Exception as e:
            logger.error(f"发送微信通知失败: {str(e)}")
            return False
    
    def send_appointment_reminder(
        self,
        patient_id: str,
        appointment_time: str,
        phone: Optional[str] = None,
        openid: Optional[str] = None,
        tenant_id: str = ""
    ) -> bool:
        """
        发送预约提醒
        
        Args:
            patient_id: 患者ID
            appointment_time: 预约时间
            phone: 手机号
            openid: 微信OpenID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否成功
        """
        message = f"您的预约时间为{appointment_time}，请准时就诊。"
        
        success = True
        if phone:
            success = self.send_sms(phone, message, tenant_id) and success
        
        if openid:
            success = self.send_wechat(
                openid,
                "appointment_reminder",
                {"time": appointment_time},
                tenant_id
            ) and success
        
        return success
    
    def send_payment_notification(
        self,
        patient_id: str,
        amount: float,
        phone: Optional[str] = None,
        openid: Optional[str] = None,
        tenant_id: str = ""
    ) -> bool:
        """
        发送支付通知
        
        Args:
            patient_id: 患者ID
            amount: 支付金额
            phone: 手机号
            openid: 微信OpenID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否成功
        """
        message = f"您的账单已支付成功，金额：{amount}元。"
        
        success = True
        if phone:
            success = self.send_sms(phone, message, tenant_id) and success
        
        if openid:
            success = self.send_wechat(
                openid,
                "payment_notification",
                {"amount": amount},
                tenant_id
            ) and success
        
        return success

