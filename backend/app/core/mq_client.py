"""
消息队列客户端：RabbitMQ连接管理
"""
import json
import pika
from typing import Optional, Dict, Any, Callable
from pika.connection import URLParameters
from pika.exceptions import AMQPConnectionError

from app.core.config import settings
from app.core.logger import logger


class MQClient:
    """消息队列客户端"""
    
    def __init__(self):
        """初始化消息队列客户端"""
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
    
    def connect(self) -> bool:
        """
        连接到RabbitMQ
        
        Returns:
            bool: 连接是否成功
        """
        try:
            parameters = URLParameters(settings.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("RabbitMQ连接成功")
            return True
        except Exception as e:
            logger.error(f"RabbitMQ连接失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开连接"""
        if self.channel and not self.channel.is_closed:
            self.channel.close()
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        logger.info("RabbitMQ连接已断开")
    
    def publish(
        self,
        exchange: str,
        routing_key: str,
        message: Dict[str, Any],
        durable: bool = True
    ) -> bool:
        """
        发布消息
        
        Args:
            exchange: 交换机名称
            routing_key: 路由键
            message: 消息内容
            durable: 是否持久化
        
        Returns:
            bool: 发布是否成功
        """
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            
            # 声明交换机
            self.channel.exchange_declare(
                exchange=exchange,
                exchange_type='topic',
                durable=durable
            )
            
            # 发布消息
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2 if durable else 1,  # 2=持久化
                    content_type='application/json'
                )
            )
            
            logger.debug(f"消息已发布: {exchange}/{routing_key}")
            return True
        except Exception as e:
            logger.error(f"发布消息失败: {str(e)}")
            return False
    
    def subscribe(
        self,
        exchange: str,
        queue: str,
        routing_key: str,
        callback: Callable,
        durable: bool = True
    ):
        """
        订阅消息
        
        Args:
            exchange: 交换机名称
            queue: 队列名称
            routing_key: 路由键
            callback: 消息处理回调函数
            durable: 是否持久化
        """
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            
            # 声明交换机
            self.channel.exchange_declare(
                exchange=exchange,
                exchange_type='topic',
                durable=durable
            )
            
            # 声明队列
            self.channel.queue_declare(queue=queue, durable=durable)
            
            # 绑定队列到交换机
            self.channel.queue_bind(
                exchange=exchange,
                queue=queue,
                routing_key=routing_key
            )
            
            # 设置消费者
            self.channel.basic_consume(
                queue=queue,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info(f"开始订阅消息: {exchange}/{queue}/{routing_key}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"订阅消息失败: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            bool: 连接是否正常
        """
        try:
            if not self.connection or self.connection.is_closed:
                return self.connect()
            return True
        except Exception:
            return False


# 创建全局消息队列客户端实例
mq_client = MQClient()

