"""
阿里云短信服务适配器
"""
import json
from typing import Dict, Any, Optional

from app.core.logger import logger

# 尝试导入阿里云SDK（如果未安装，使用简化实现）
try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    from aliyunsdkcore.acs_exception.exceptions import ClientException, ServerException
    ALIYUN_SDK_AVAILABLE = True
except ImportError:
    ALIYUN_SDK_AVAILABLE = False
    logger.warning("阿里云SDK未安装，使用简化实现")
    # 定义占位符类以避免导入错误
    class AcsClient:
        pass
    class CommonRequest:
        pass
    class ClientException(Exception):
        def get_error_code(self):
            return ""
        def get_error_msg(self):
            return str(self)
    class ServerException(Exception):
        def get_error_code(self):
            return ""
        def get_error_msg(self):
            return str(self)


class AliyunSMSAdapter:
    """阿里云短信适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化适配器
        
        Args:
            config: 配置数据（已解密）
        """
        self.config = config
        self.access_key_id = config.get("access_key_id")
        self.access_key_secret = config.get("access_key_secret")
        self.sign_name = config.get("sign_name")
        self.template_code = config.get("template_code")
        self.region = config.get("region", "cn-hangzhou")
        
        # 创建客户端（如果SDK可用）
        if ALIYUN_SDK_AVAILABLE and self.access_key_id and self.access_key_secret:
            try:
                self.client = AcsClient(
                    self.access_key_id,
                    self.access_key_secret,
                    self.region
                )
            except Exception as e:
                logger.warning(f"阿里云客户端初始化失败: {str(e)}")
                self.client = None
        else:
            self.client = None
    
    def send_sms(
        self,
        phone: str,
        template_params: Optional[Dict[str, Any]] = None,
        template_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送短信
        
        Args:
            phone: 手机号码
            template_params: 模板参数（可选）
            template_code: 模板代码（可选，使用配置中的默认模板）
        
        Returns:
            Dict[str, Any]: 发送结果
        """
        try:
            if not ALIYUN_SDK_AVAILABLE:
                # 简化实现（用于测试）
                logger.warning("阿里云SDK未安装，返回模拟结果")
                return {
                    "success": True,
                    "message_id": f"MSG_{phone[-4:]}",
                    "message": "发送成功（模拟）"
                }
            
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('dysmsapi.aliyuncs.com')
            request.set_method('POST')
            request.set_protocol_type('https')
            request.set_version('2017-05-25')
            request.set_action_name('SendSms')
            
            # 设置请求参数
            request.add_query_param('RegionId', self.region)
            request.add_query_param('PhoneNumbers', phone)
            request.add_query_param('SignName', self.sign_name)
            request.add_query_param('TemplateCode', template_code or self.template_code)
            
            if template_params:
                request.add_query_param('TemplateParam', json.dumps(template_params))
            
            # 发送请求
            response = self.client.do_action_with_exception(request)
            result = json.loads(response.decode('utf-8'))
            
            if result.get('Code') == 'OK':
                return {
                    "success": True,
                    "message_id": result.get('BizId'),
                    "message": "发送成功"
                }
            else:
                logger.error(f"阿里云短信发送失败: {result.get('Message')}")
                return {
                    "success": False,
                    "error_code": result.get('Code'),
                    "message": result.get('Message', '发送失败')
                }
        
        except ClientException as e:
            logger.error(f"阿里云短信客户端异常: {str(e)}")
            return {
                "success": False,
                "error_code": e.get_error_code(),
                "message": e.get_error_msg()
            }
        except ServerException as e:
            logger.error(f"阿里云短信服务端异常: {str(e)}")
            return {
                "success": False,
                "error_code": e.get_error_code(),
                "message": e.get_error_msg()
            }
        except Exception as e:
            logger.error(f"阿里云短信发送异常: {str(e)}")
            return {
                "success": False,
                "message": f"发送失败: {str(e)}"
            }
    
    def send_verification_code(self, phone: str, code: str) -> Dict[str, Any]:
        """
        发送验证码
        
        Args:
            phone: 手机号码
            code: 验证码
        
        Returns:
            Dict[str, Any]: 发送结果
        """
        return self.send_sms(
            phone=phone,
            template_params={"code": code}
        )
    
    def send_notification(self, phone: str, message: str) -> Dict[str, Any]:
        """
        发送通知短信
        
        Args:
            phone: 手机号码
            message: 消息内容
        
        Returns:
            Dict[str, Any]: 发送结果
        """
        return self.send_sms(
            phone=phone,
            template_params={"message": message}
        )

