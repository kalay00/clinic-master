"""
租户服务（对齐旧 services/tenant_service.py，迁移为异步 + CRUDBase，Python 3.12+）

业务规则：
- 租户配置默认 / 合并 / 校验
- 药师审核开关、按 code / domain 查询
"""
from __future__ import annotations
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import Tenant
from .schema import TenantSchema, TenantCreateSchema, TenantUpdateSchema, TenantCurrentSchema, TenantCurrentUpdateSchema
from .crud import TenantCRUD

# 延迟导入避免循环依赖
User = None


def _get_user_model():
    global User
    if User is None:
        from app.api.v1.module_user.model import User as _User
        User = _User
    return User


def _to_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return value


class TenantService:
    """Tenant 服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = TenantCRUD(Tenant, auth=auth)

    @property
    def _db(self):
        return self.crud.db

    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    # ── 标准 CRUD ──
    async def get(self, id: str) -> TenantSchema:
        return await self.crud.get_or_404(id=id, out_schema=TenantSchema)

    async def list(self, page_no: int, page_size: int, order_by=None, search: dict | None = None):
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            out_schema=TenantSchema,
        )

    async def create(self, data: TenantCreateSchema) -> TenantSchema:
        obj = await self.crud.create(data)
        uid = self._user_id
        if uid and hasattr(obj, "created_by"):
            setattr(obj, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return TenantSchema.model_validate(obj)

    async def update(self, id: str, data: TenantUpdateSchema) -> TenantSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return TenantSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 业务方法：配置 ──
    def get_default_config(self) -> Dict[str, Any]:
        """默认租户配置"""
        return {
            "pharmacist_review_enabled": True,
            "registration": {
                "max_advance_days": 30,
                "default_fee": 10.0,
                "allow_same_day": True,
                "auto_complete_visit": False,
            },
            "prescription": {
                "validity_days": 7,
                "default_type": "western",
                "require_doctor_signature": True,
                "allow_edit_after_save": False,
            },
            "print": {
                "default_bill_template": None,
                "default_prescription_template": None,
                "default_medical_record_template": None,
                "auto_print_after_payment": False,
            },
            "system": {
                "session_timeout": 3600,
                "password_min_length": 6,
                "require_password_change": False,
                "enable_audit_log": True,
            },
            "loyalty": {
                # 消费 1 元赠送多少积分
                "points_per_yuan": 1,
                # 多少积分抵扣 1 元
                "points_to_yuan": 100,
                # 充值赠送比例（0~1）：充值 100 元按 0.1 赠送 10 元
                "recharge_bonus_ratio": 0,
            },
        }

    def validate_config(self, config: Dict[str, Any]) -> None:
        """校验配置（非法抛 CustomException）"""
        if "pharmacist_review_enabled" in config and not isinstance(config["pharmacist_review_enabled"], bool):
            raise CustomException(msg="药师审核开关必须是布尔值", code=400, status_code=400)
        if "registration" in config:
            reg = config["registration"]
            if not isinstance(reg, dict):
                raise CustomException(msg="挂号设置必须是对象", code=400, status_code=400)
            if "max_advance_days" in reg and (not isinstance(reg["max_advance_days"], int) or reg["max_advance_days"] < 1):
                raise CustomException(msg="最大提前预约天数必须是大于0的整数", code=400, status_code=400)
            if "default_fee" in reg and (not isinstance(reg["default_fee"], (int, float)) or reg["default_fee"] < 0):
                raise CustomException(msg="默认挂号费必须是非负数", code=400, status_code=400)
        if "prescription" in config:
            pres = config["prescription"]
            if not isinstance(pres, dict):
                raise CustomException(msg="处方设置必须是对象", code=400, status_code=400)
            if "validity_days" in pres and (not isinstance(pres["validity_days"], int) or pres["validity_days"] < 1):
                raise CustomException(msg="处方有效期必须是大于0的整数", code=400, status_code=400)
            if "default_type" in pres and pres["default_type"] not in ["western", "traditional", "chinese_medicine"]:
                raise CustomException(msg="默认处方类型必须是 western/traditional/chinese_medicine", code=400, status_code=400)
        if "system" in config:
            sys_cfg = config["system"]
            if not isinstance(sys_cfg, dict):
                raise CustomException(msg="系统设置必须是对象", code=400, status_code=400)
            if "session_timeout" in sys_cfg and (not isinstance(sys_cfg["session_timeout"], int) or sys_cfg["session_timeout"] < 300):
                raise CustomException(msg="会话超时时间必须是不小于300秒的整数", code=400, status_code=400)
            if "password_min_length" in sys_cfg and (not isinstance(sys_cfg["password_min_length"], int) or sys_cfg["password_min_length"] < 6):
                raise CustomException(msg="密码最小长度必须是不小于6的整数", code=400, status_code=400)
        if "loyalty" in config:
            loyalty = config["loyalty"]
            if not isinstance(loyalty, dict):
                raise CustomException(msg="会员积分设置必须是对象", code=400, status_code=400)
            for key in ("points_per_yuan", "points_to_yuan", "recharge_bonus_ratio"):
                if key in loyalty and (not isinstance(loyalty[key], (int, float)) or loyalty[key] < 0):
                    raise CustomException(msg=f"会员积分设置 {key} 必须是非负数", code=400, status_code=400)

    async def _get_tenant(self, tenant_id: str) -> Tenant:
        stmt = select(Tenant).where(Tenant.id == _to_uuid(tenant_id), Tenant.deleted_at.is_(None))
        result = await self._db.execute(stmt)
        tenant = result.scalars().first()
        if not tenant:
            raise CustomException(msg="租户不存在", code=404, status_code=404)
        return tenant

    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """获取合并后的租户配置（默认 + 用户配置）"""
        tenant = await self._get_tenant(tenant_id)
        if tenant.config is None:
            return self.get_default_config()
        default = self.get_default_config()
        user_config = tenant.config if isinstance(tenant.config, dict) else {}
        default.update(user_config)
        return default

    async def update_tenant_config(self, tenant_id: str, config_updates: Dict[str, Any], updater_id: Optional[str] = None) -> Dict[str, Any]:
        """更新租户配置（合并 + 校验）"""
        tenant = await self._get_tenant(tenant_id)
        current = tenant.config if isinstance(tenant.config, dict) else {}
        updated = {**current, **config_updates}
        self.validate_config(updated)
        tenant.config = updated
        uid = updater_id or self._user_id
        if uid and hasattr(tenant, "updated_by"):
            setattr(tenant, "updated_by", uid)
        await self._db.commit()
        logger.info(f"更新租户配置: {tenant_id} by {uid}")
        return updated

    async def is_pharmacist_review_enabled(self, tenant_id: str) -> bool:
        """药师审核开关是否启用（默认开启）"""
        config = await self.get_tenant_config(tenant_id)
        return bool(config.get("pharmacist_review_enabled", True))

    async def get_tenant_by_code(self, tenant_code: str) -> TenantSchema:
        stmt = select(Tenant).where(
            Tenant.code == tenant_code, Tenant.deleted_at.is_(None), Tenant.status == "active"
        )
        result = await self._db.execute(stmt)
        tenant = result.scalars().first()
        if not tenant:
            raise CustomException(msg="租户不存在", code=404, status_code=404)
        return TenantSchema.model_validate(tenant)

    async def get_tenant_by_domain(self, domain: str) -> TenantSchema:
        stmt = select(Tenant).where(
            Tenant.domain == domain, Tenant.deleted_at.is_(None), Tenant.status == "active"
        )
        result = await self._db.execute(stmt)
        tenant = result.scalars().first()
        if not tenant:
            raise CustomException(msg="租户不存在", code=404, status_code=404)
        return TenantSchema.model_validate(tenant)

    async def _count_tenant_users(self, tenant_id: str) -> int:
        """统计租户下有效用户数量"""
        UserModel = _get_user_model()
        stmt = select(func.count(UserModel.id)).where(
            UserModel.tenant_id == _to_uuid(tenant_id),
            UserModel.status != "deleted"
        )
        result = await self._db.execute(stmt)
        return result.scalar() or 0

    async def get_current(self, tenant_id: str) -> Dict[str, Any]:
        """获取当前诊所信息（供诊所信息维护页面使用）"""
        tenant = await self._get_tenant(tenant_id)
        config = tenant.config if isinstance(tenant.config, dict) else {}
        user_count = await self._count_tenant_users(tenant_id)
        return {
            "id": tenant.id,
            "code": tenant.code,
            "name": tenant.name,
            "contact_name": tenant.contact_name,
            "contact_phone": tenant.contact_phone,
            "contact_email": tenant.contact_email,
            "address": tenant.address,
            "status": tenant.status,
            "expires_at": tenant.expires_at,
            "logo": config.get("logo"),
            "introduction": config.get("introduction"),
            "user_count": user_count,
        }

    async def update_current(self, tenant_id: str, data: TenantCurrentUpdateSchema) -> Dict[str, Any]:
        """更新当前诊所信息"""
        tenant = await self._get_tenant(tenant_id)
        update_data = data.model_dump(exclude_unset=True)

        # config 中的字段单独处理
        config_fields = {"logo", "introduction"}
        config_updates = {k: update_data.pop(k) for k in list(update_data.keys()) if k in config_fields}

        # 更新 Tenant 表字段
        for key, value in update_data.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)

        # 更新 config JSON
        if config_updates:
            current_config = tenant.config if isinstance(tenant.config, dict) else {}
            tenant.config = {**current_config, **config_updates}

        uid = self._user_id
        if uid and hasattr(tenant, "updated_by"):
            setattr(tenant, "updated_by", uid)
        await self._db.commit()
        logger.info(f"更新当前诊所信息: {tenant_id} by {uid}")
        return await self.get_current(tenant_id)
