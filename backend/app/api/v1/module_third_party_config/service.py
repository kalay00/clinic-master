"""
第三方服务配置服务（对齐旧 services/third_party_config_service.py，异步 + CRUDBase，Python 3.12+）

业务规则：
- 敏感字段加密存储（AES-GCM）
- 按服务类型校验必填字段
- 配置解密后返回
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import select

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.core.encryption import encrypt_data, decrypt_data

from .model import ThirdPartyConfig
from .schema import (
    ThirdPartyConfigSchema,
    ThirdPartyConfigCreateSchema,
    ThirdPartyConfigUpdateSchema,
)
from .crud import ThirdPartyConfigCRUD


def _to_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return value


class ThirdPartyConfigService:
    """ThirdPartyConfig 服务"""

    # 服务类型定义（名称 / 加密字段 / 必填字段）
    SERVICE_TYPES = {
        "aliyun_sms": {
            "name": "阿里云短信",
            "encrypted_fields": ["access_key_id", "access_key_secret"],
            "required_fields": ["access_key_id", "access_key_secret", "sign_name", "template_code"],
        },
        "alipay": {
            "name": "支付宝",
            "encrypted_fields": ["app_private_key", "alipay_public_key"],
            "required_fields": ["app_id", "app_private_key", "alipay_public_key", "sign_type"],
        },
        "wechat_pay": {
            "name": "微信支付",
            "encrypted_fields": ["api_key", "app_secret"],
            "required_fields": ["app_id", "mch_id", "api_key"],
        },
        "unionpay": {
            "name": "银联支付",
            "encrypted_fields": ["mer_key"],
            "required_fields": ["mer_id", "mer_key"],
        },
    }

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = ThirdPartyConfigCRUD(ThirdPartyConfig, auth=auth)

    @property
    def _db(self):
        return self.crud.db

    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    # ── 标准 CRUD ──
    async def get(self, id: str) -> ThirdPartyConfigSchema:
        return await self.crud.get_or_404(id=id, out_schema=ThirdPartyConfigSchema)

    async def list(self, page_no: int, page_size: int, order_by=None, search: dict | None = None):
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            out_schema=ThirdPartyConfigSchema,
        )

    async def create(self, data: ThirdPartyConfigCreateSchema) -> ThirdPartyConfigSchema:
        obj = await self.crud.create(data)
        uid = self._user_id
        if uid and hasattr(obj, "created_by"):
            setattr(obj, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return ThirdPartyConfigSchema.model_validate(obj)

    async def update(self, id: str, data: ThirdPartyConfigUpdateSchema) -> ThirdPartyConfigSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return ThirdPartyConfigSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 业务方法 ──
    async def _query_config(self, tenant_id: str, service_type: str) -> Optional[ThirdPartyConfig]:
        stmt = select(ThirdPartyConfig).where(
            ThirdPartyConfig.tenant_id == _to_uuid(tenant_id),
            ThirdPartyConfig.service_type == service_type,
            ThirdPartyConfig.deleted_at.is_(None),
        )
        result = await self._db.execute(stmt)
        return result.scalars().first()

    def encrypt_config(self, config_data: Dict[str, Any], encrypted_fields: List[str]) -> Dict[str, Any]:
        encrypted = config_data.copy()
        for field in encrypted_fields:
            if field in encrypted and encrypted[field]:
                val = encrypted[field]
                if isinstance(val, str) and val.startswith("encrypted_"):
                    continue
                encrypted[field] = encrypt_data(str(val))
        return encrypted

    def decrypt_config(self, config: ThirdPartyConfig) -> Dict[str, Any]:
        if config.config_data is None:
            config_data: Dict[str, Any] = {}
        elif isinstance(config.config_data, dict):
            config_data = config.config_data.copy()
        else:
            try:
                import json
                config_data = json.loads(config.config_data) if isinstance(config.config_data, str) else dict(config.config_data)
            except Exception:
                config_data = {}
        for field in (config.encrypted_fields or []):
            if field in config_data and config_data[field]:
                try:
                    config_data[field] = decrypt_data(config_data[field])
                except Exception as e:  # pragma: no cover
                    logger.warning(f"解密字段 {field} 失败: {e}")
        return {
            "id": str(config.id),
            "tenant_id": str(config.tenant_id),
            "service_type": config.service_type,
            "service_name": config.service_name,
            "is_enabled": config.is_enabled,
            "config_data": config_data,
            "created_at": config.created_at.isoformat() if config.created_at else None,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None,
        }

    def validate_config(self, service_type: str, config_data: Dict[str, Any]) -> None:
        if service_type not in self.SERVICE_TYPES:
            raise CustomException(msg=f"不支持的服务类型: {service_type}", code=400, status_code=400)
        for field in self.SERVICE_TYPES[service_type]["required_fields"]:
            if field not in config_data or not config_data[field]:
                raise CustomException(msg=f"缺少必填字段: {field}", code=400, status_code=400)

    async def get_config(self, tenant_id: str, service_type: str) -> Optional[Dict[str, Any]]:
        config = await self._query_config(tenant_id, service_type)
        if not config:
            return None
        return self.decrypt_config(config)

    async def save_config(
        self, tenant_id: str, service_type: str, config_data: Dict[str, Any], creator_id: Optional[str] = None
    ) -> Dict[str, Any]:
        if service_type not in self.SERVICE_TYPES:
            raise CustomException(msg=f"不支持的服务类型: {service_type}", code=400, status_code=400)
        self.validate_config(service_type, config_data)
        info = self.SERVICE_TYPES[service_type]
        encrypted = self.encrypt_config(config_data, info["encrypted_fields"])

        existing = await self._query_config(tenant_id, service_type)
        uid = creator_id or self._user_id
        if existing:
            existing.config_data = encrypted
            existing.is_enabled = config_data.get("is_enabled", True)
            if uid and hasattr(existing, "updated_by"):
                setattr(existing, "updated_by", uid)
            obj = existing
        else:
            obj = ThirdPartyConfig(
                tenant_id=_to_uuid(tenant_id),
                service_type=service_type,
                service_name=info["name"],
                is_enabled=config_data.get("is_enabled", True),
                config_data=encrypted,
                encrypted_fields=info["encrypted_fields"],
                created_by=_to_uuid(uid),
                updated_by=_to_uuid(uid),
            )
            self._db.add(obj)
        await self._db.commit()
        return self.decrypt_config(obj)

    async def delete_config(self, tenant_id: str, service_type: str) -> bool:
        config = await self._query_config(tenant_id, service_type)
        if not config:
            return False
        await self.crud.delete([str(config.id)])
        return True
