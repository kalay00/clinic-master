"""
通用工具（对齐 FastapiAdmin: app.utils.common_util）
"""
import uuid


def uuid4_str() -> str:
    """返回 str 类型的 UUID4，用于模型 uuid 字段默认值。"""
    return str(uuid.uuid4())
