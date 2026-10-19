"""
通用工具函数库
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Any, Dict
import hashlib


def generate_uuid() -> str:
    """
    生成UUID字符串
    
    Returns:
        str: UUID字符串
    """
    return str(uuid.uuid4())


def generate_id() -> str:
    """
    生成唯一ID（UUID格式）
    
    Returns:
        str: 唯一ID
    """
    return generate_uuid()


def get_current_timestamp() -> datetime:
    """
    获取当前时间戳（UTC）
    
    Returns:
        datetime: 当前UTC时间
    """
    return datetime.now(timezone.utc)


def get_current_timestamp_str() -> str:
    """
    获取当前时间戳字符串（ISO格式）
    
    Returns:
        str: ISO格式时间字符串
    """
    return get_current_timestamp().isoformat()


def md5_hash(text: str) -> str:
    """
    计算MD5哈希值
    
    Args:
        text: 待哈希的文本
    
    Returns:
        str: MD5哈希值
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def sha256_hash(text: str) -> str:
    """
    计算SHA256哈希值
    
    Args:
        text: 待哈希的文本
    
    Returns:
        str: SHA256哈希值
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def mask_sensitive_data(text: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    脱敏敏感数据
    
    Args:
        text: 原始文本
        mask_char: 掩码字符
        visible_chars: 可见字符数（从开头和结尾各显示的数量）
    
    Returns:
        str: 脱敏后的文本
    """
    if not text or len(text) <= visible_chars * 2:
        return mask_char * len(text) if text else ""
    
    start = text[:visible_chars]
    end = text[-visible_chars:]
    middle = mask_char * (len(text) - visible_chars * 2)
    
    return f"{start}{middle}{end}"


def mask_phone(phone: str) -> str:
    """
    脱敏手机号
    
    Args:
        phone: 手机号
    
    Returns:
        str: 脱敏后的手机号
    """
    if not phone or len(phone) != 11:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"


def mask_id_card(id_card: str) -> str:
    """
    脱敏身份证号
    
    Args:
        id_card: 身份证号
    
    Returns:
        str: 脱敏后的身份证号
    """
    if not id_card or len(id_card) < 8:
        return id_card
    return f"{id_card[:6]}****{id_card[-4:]}"


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数
    
    Args:
        value: 待转换的值
        default: 默认值
    
    Returns:
        int: 转换后的整数
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    
    Args:
        value: 待转换的值
        default: 默认值
    
    Returns:
        float: 转换后的浮点数
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    安全转换为字符串
    
    Args:
        value: 待转换的值
        default: 默认值
    
    Returns:
        str: 转换后的字符串
    """
    if value is None:
        return default
    return str(value)


def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    移除字典中的None值
    
    Args:
        data: 原始字典
    
    Returns:
        Dict[str, Any]: 移除None值后的字典
    """
    return {k: v for k, v in data.items() if v is not None}


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
    
    Returns:
        str: 格式化后的字符串
    """
    if dt is None:
        return ""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        dt_str: 日期时间字符串
        format_str: 格式字符串
    
    Returns:
        Optional[datetime]: 日期时间对象，解析失败返回None
    """
    try:
        return datetime.strptime(dt_str, format_str)
    except (ValueError, TypeError):
        return None

