"""
应用配置（对齐 FastapiAdmin: app.config.setting）
从 app.core.config 复用既有 Settings，保持原有配置不变。
"""
from app.core.config import Settings, settings  # noqa: F401

__all__ = ["Settings", "settings"]
