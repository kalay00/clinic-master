"""
数据加密组件：AES-256-GCM加密
"""
import base64
import hashlib
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from app.core.config import settings
from app.core.logger import logger


class EncryptionService:
    """加密服务类"""
    
    def __init__(self, key: Optional[str] = None):
        """
        初始化加密服务
        
        Args:
            key: 加密密钥（如果不提供，从配置中读取）
        """
        self.key = key or settings.ENCRYPTION_KEY
        # 将密钥转换为32字节（AES-256需要32字节密钥）
        self._key = self._derive_key(self.key)
    
    def _derive_key(self, key: str) -> bytes:
        """
        从字符串密钥派生32字节密钥
        
        Args:
            key: 原始密钥字符串
        
        Returns:
            bytes: 32字节密钥
        """
        # 使用SHA256哈希派生32字节密钥
        return hashlib.sha256(key.encode('utf-8')).digest()
    
    def encrypt(self, plaintext: str) -> str:
        """
        加密明文数据
        
        Args:
            plaintext: 明文数据
        
        Returns:
            str: Base64编码的密文
        """
        try:
            # 将字符串转换为字节
            plaintext_bytes = plaintext.encode('utf-8')
            
            # 创建AES-GCM加密器
            aesgcm = AESGCM(self._key)
            
            # 生成随机nonce（12字节，AES-GCM标准）
            nonce = os.urandom(12)
            
            # 加密
            ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
            
            # 将nonce和密文组合，然后Base64编码
            encrypted_data = nonce + ciphertext
            encrypted_str = base64.b64encode(encrypted_data).decode('utf-8')
            
            return encrypted_str
        except Exception as e:
            logger.error(f"加密失败: {str(e)}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        解密密文数据
        
        Args:
            ciphertext: Base64编码的密文
        
        Returns:
            str: 明文数据
        
        Raises:
            ValueError: 如果密文格式不正确或解密失败
        """
        try:
            # 检查输入是否有效
            if not ciphertext:
                raise ValueError("密文不能为空")
            
            # 去除可能的空白字符
            ciphertext = ciphertext.strip()
            
            if not ciphertext:
                raise ValueError("密文不能为空")
            
            # Base64解码
            try:
                encrypted_data = base64.b64decode(ciphertext.encode('utf-8'), validate=True)
            except Exception as e:
                raise ValueError(f"Base64解码失败: {str(e)}")
            
            # 检查数据长度（至少需要12字节nonce + 16字节tag + 至少1字节数据）
            if len(encrypted_data) < 29:
                raise ValueError(f"密文数据长度不足: {len(encrypted_data)} 字节")
            
            # 提取nonce和密文
            nonce = encrypted_data[:12]
            ciphertext_bytes = encrypted_data[12:]
            
            # 创建AES-GCM解密器
            aesgcm = AESGCM(self._key)
            
            # 解密
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext_bytes, None)
            
            # 转换为字符串
            plaintext = plaintext_bytes.decode('utf-8')
            
            return plaintext
        except ValueError:
            # 重新抛出ValueError
            raise
        except Exception as e:
            logger.error(f"解密失败: {str(e)}, ciphertext_length={len(ciphertext) if ciphertext else 0}")
            raise ValueError(f"解密失败: {str(e)}")
    
    def hash_for_query(self, text: str) -> str:
        """
        为查询生成哈希值（用于模糊查询场景）
        
        Args:
            text: 原始文本
        
        Returns:
            str: SHA256哈希值
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()


# 创建全局加密服务实例
encryption_service = EncryptionService()


def encrypt_data(data: str) -> str:
    """
    加密数据（便捷函数）
    
    Args:
        data: 明文数据
    
    Returns:
        str: 加密后的数据
    """
    return encryption_service.encrypt(data)


def decrypt_data(ciphertext: str) -> str:
    """
    解密数据（便捷函数）
    
    Args:
        ciphertext: 密文数据
    
    Returns:
        str: 解密后的数据
    """
    return encryption_service.decrypt(ciphertext)


def hash_for_query(text: str) -> str:
    """
    为查询生成哈希值（便捷函数）
    
    Args:
        text: 原始文本
    
    Returns:
        str: 哈希值
    """
    return encryption_service.hash_for_query(text)

