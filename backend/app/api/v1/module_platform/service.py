"""
平台管理员服务（对齐旧 services/platform_admin_service.py，异步，Python 3.12+）

业务规则（平台级，跨租户，不走租户隔离 CRUD）：
- 平台管理员登录态维护（密码校验）
- 创建租户时自动创建租户管理员账号（admin / 111111）并分配 admin 角色
- 跨租户统计
- 平台管理员 / 租户管理员密码修改
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID

from sqlalchemy import select, func

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.core.security import get_password_hash, verify_password

from app.api.v1.module_platform.model import PlatformAdmin
from app.api.v1.module_tenant.model import Tenant
from app.api.v1.module_user.model import User
from app.api.v1.module_role.model import Role, UserRole
from app.api.v1.module_patient.model import Patient
from app.api.v1.module_payment.model import Bill
from app.api.v1.module_registration.model import Registration
from app.api.v1.module_treatment.model import MedicalRecord
from app.api.v1.module_log.model import AuditLog

from .model import PlatformAdmin as PlatformAdminModel
from .schema import PlatformAdminSchema, PlatformAdminCreateSchema, PlatformAdminUpdateSchema
from .crud import PlatformAdminCRUD
from app.api.v1.module_tenant.schema import TenantSchema


def _to_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return value


class PlatformService:
    """Platform 服务（平台级，跨租户）"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = PlatformAdminCRUD(PlatformAdminModel, auth=auth)

    @property
    def _db(self):
        return self.crud.db

    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    # ── 平台管理员 CRUD（仍走租户隔离 CRUD，平台管理员 tenant_id 为 platform）──
    async def get(self, id: str) -> PlatformAdminSchema:
        return await self.crud.get_or_404(id=id, out_schema=PlatformAdminSchema)

    async def list(self, page_no: int, page_size: int, order_by=None, search: dict | None = None):
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            out_schema=PlatformAdminSchema,
        )

    async def create(self, data: PlatformAdminCreateSchema) -> PlatformAdminSchema:
        obj = await self.crud.create(data)
        uid = self._user_id
        if uid and hasattr(obj, "created_by"):
            setattr(obj, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return PlatformAdminSchema.model_validate(obj)

    async def update(self, id: str, data: PlatformAdminUpdateSchema) -> PlatformAdminSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return PlatformAdminSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 业务方法：跨租户 ──
    async def get_platform_admin(self, admin_id: str) -> PlatformAdmin:
        stmt = select(PlatformAdmin).where(
            PlatformAdmin.id == _to_uuid(admin_id), PlatformAdmin.deleted_at.is_(None)
        )
        result = await self._db.execute(stmt)
        admin = result.scalars().first()
        if not admin:
            raise CustomException(msg="平台管理员不存在", code=404, status_code=404)
        return admin

    async def list_tenants(
        self, search: Optional[str] = None, status: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> tuple[List[dict], int]:
        stmt = select(Tenant).where(Tenant.deleted_at.is_(None))
        count_stmt = select(func.count(Tenant.id)).where(Tenant.deleted_at.is_(None))
        if search:
            stmt = stmt.where(
                or_like(Tenant.name, search) | or_like(Tenant.code, search)
            )
            count_stmt = count_stmt.where(
                or_like(Tenant.name, search) | or_like(Tenant.code, search)
            )
        if status:
            stmt = stmt.where(Tenant.status == status)
            count_stmt = count_stmt.where(Tenant.status == status)
        total = (await self._db.execute(count_stmt)).scalar() or 0
        stmt = stmt.order_by(Tenant.created_at.desc()).offset(skip).limit(limit)
        rows = (await self._db.execute(stmt)).scalars().all()
        items = [TenantSchema.model_validate(t).model_dump() for t in rows]
        return items, total

    async def get_tenant(self, tenant_id: str) -> dict:
        tenant = (await self._db.execute(
            select(Tenant).where(Tenant.id == _to_uuid(tenant_id), Tenant.deleted_at.is_(None))
        )).scalars().first()
        if not tenant:
            raise CustomException(msg="租户不存在", code=404, status_code=404)
        return TenantSchema.model_validate(tenant).model_dump()

    async def list_audit_logs(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        operation_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[dict], int]:
        """跨租户查询审计日志，并补充租户名/用户名及前端别名字段。"""
        from datetime import datetime as _dt

        stmt = (
            select(AuditLog, Tenant.name, User.real_name)
            .select_from(AuditLog)
            .outerjoin(Tenant, AuditLog.tenant_id == Tenant.id)
            .outerjoin(User, AuditLog.user_id == User.id)
        )
        count_stmt = select(func.count(AuditLog.id))

        if tenant_id:
            stmt = stmt.where(AuditLog.tenant_id == _to_uuid(tenant_id))
            count_stmt = count_stmt.where(AuditLog.tenant_id == _to_uuid(tenant_id))
        if user_id:
            stmt = stmt.where(AuditLog.user_id == _to_uuid(user_id))
            count_stmt = count_stmt.where(AuditLog.user_id == _to_uuid(user_id))
        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
            count_stmt = count_stmt.where(AuditLog.resource_type == resource_type)
        if operation_type:
            stmt = stmt.where(AuditLog.audit_type == operation_type)
            count_stmt = count_stmt.where(AuditLog.audit_type == operation_type)
        if start_date:
            sd = _dt.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
            stmt = stmt.where(AuditLog.created_at >= sd)
            count_stmt = count_stmt.where(AuditLog.created_at >= sd)
        if end_date:
            ed = _dt.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            stmt = stmt.where(AuditLog.created_at <= ed)
            count_stmt = count_stmt.where(AuditLog.created_at <= ed)

        total = (await self._db.execute(count_stmt)).scalar() or 0
        stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        rows = (await self._db.execute(stmt)).all()

        items: List[dict] = []
        for log, tenant_name, user_name in rows:
            items.append({
                "id": str(log.id),
                "tenant_id": str(log.tenant_id),
                "user_id": str(log.user_id),
                "audit_type": log.audit_type,
                "operation_type": log.audit_type,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id) if log.resource_id else None,
                "audit_desc": log.audit_desc,
                "operation_desc": log.audit_desc,
                "request_ip": log.request_ip,
                "ip_address": log.request_ip,
                "user_agent": log.user_agent,
                "before_data": log.before_data,
                "after_data": log.after_data,
                "risk_level": log.risk_level,
                "regulatory_type": log.regulatory_type,
                "regulatory_operation": log.regulatory_operation,
                "regulatory_status": log.regulatory_status,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "tenant_name": tenant_name or "系统",
                "user_name": user_name or "未知",
            })
        return items, total

    async def create_tenant(self, tenant_data: Dict[str, Any], creator_id: Optional[str] = None) -> dict:
        """创建租户，并自动创建租户管理员账号（admin / 111111）"""
        code = tenant_data.get("code")
        if not code:
            raise CustomException(msg="租户编码必填", code=400, status_code=400)
        existing = (await self._db.execute(
            select(Tenant).where(Tenant.code == code, Tenant.deleted_at.is_(None))
        )).scalars().first()
        if existing:
            raise CustomException(msg=f"租户代码已存在: {code}", code=400, status_code=400)
        if tenant_data.get("domain"):
            dup = (await self._db.execute(
                select(Tenant).where(Tenant.domain == tenant_data["domain"], Tenant.deleted_at.is_(None))
            )).scalars().first()
            if dup:
                raise CustomException(msg=f"租户域名已存在: {tenant_data['domain']}", code=400, status_code=400)

        tenant = Tenant(**{k: v for k, v in tenant_data.items() if k != "password"})
        self._db.add(tenant)
        await self._db.flush()
        await self._db.commit()

        # 创建租户管理员用户
        try:
            admin_user = User(
                tenant_id=tenant.id,
                username="admin",
                password_hash=get_password_hash("111111"),
                real_name=f"{tenant.name}管理员",
                phone=tenant_data.get("contact_phone", ""),
                email=tenant_data.get("contact_email", ""),
                status="active",
            )
            self._db.add(admin_user)
            await self._db.flush()

            admin_role = (await self._db.execute(
                select(Role).where(
                    Role.tenant_id == tenant.id, Role.code == "admin", Role.deleted_at.is_(None)
                )
            )).scalars().first()
            if admin_role:
                self._db.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))
                await self._db.commit()
                logger.info(f"为租户管理员 {admin_user.username} 分配角色: {admin_role.name}")
            else:
                logger.warning(f"租户 {tenant.code} 未找到 admin 角色，跳过角色分配")
        except Exception as e:  # pragma: no cover
            logger.error(f"创建租户管理员失败: {e}", exc_info=True)

        logger.info(f"平台管理员 {creator_id} 创建租户: {tenant.code}")
        await self._db.refresh(tenant)
        return TenantSchema.model_validate(tenant).model_dump()

    async def update_tenant(self, tenant_id: str, tenant_data: Dict[str, Any], updater_id: Optional[str] = None) -> dict:
        tenant = (await self._db.execute(
            select(Tenant).where(Tenant.id == _to_uuid(tenant_id), Tenant.deleted_at.is_(None))
        )).scalars().first()
        if not tenant:
            raise CustomException(msg="租户不存在", code=404, status_code=404)
        for key, value in tenant_data.items():
            if hasattr(tenant, key) and value is not None:
                setattr(tenant, key, value)
        await self._db.commit()
        await self._db.refresh(tenant)
        logger.info(f"平台管理员 {updater_id} 更新租户: {tenant.code}")
        return TenantSchema.model_validate(tenant).model_dump()

    async def delete_tenant(self, tenant_id: str, deleter_id: Optional[str] = None) -> bool:
        tenant = (await self._db.execute(
            select(Tenant).where(Tenant.id == _to_uuid(tenant_id), Tenant.deleted_at.is_(None))
        )).scalars().first()
        if not tenant:
            raise CustomException(msg="租户不存在", code=404, status_code=404)
        tenant.deleted_at = datetime.now()
        await self._db.commit()
        logger.info(f"平台管理员 {deleter_id} 删除租户: {tenant.code}")
        return True

    async def get_platform_statistics(self) -> Dict[str, Any]:
        """跨所有租户的平台统计"""
        total_tenants = (await self._db.execute(
            select(func.count(Tenant.id)).where(Tenant.deleted_at.is_(None))
        )).scalar() or 0
        active_tenants = (await self._db.execute(
            select(func.count(Tenant.id)).where(Tenant.deleted_at.is_(None), Tenant.status == "active")
        )).scalar() or 0
        total_users = (await self._db.execute(
            select(func.count(User.id)).where(User.deleted_at.is_(None))
        )).scalar() or 0
        total_patients = (await self._db.execute(
            select(func.count(Patient.id)).where(Patient.deleted_at.is_(None))
        )).scalar() or 0
        total_registrations = (await self._db.execute(
            select(func.count(Registration.id)).where(Registration.deleted_at.is_(None))
        )).scalar() or 0
        total_medical_records = (await self._db.execute(
            select(func.count(MedicalRecord.id)).where(MedicalRecord.deleted_at.is_(None))
        )).scalar() or 0
        total_revenue = (await self._db.execute(
            select(func.sum(Bill.paid_amount)).where(Bill.deleted_at.is_(None), Bill.status == "paid")
        )).scalar() or 0
        today = date.today()
        today_revenue = (await self._db.execute(
            select(func.sum(Bill.paid_amount)).where(
                Bill.deleted_at.is_(None), Bill.status == "paid", func.date(Bill.payment_time) == today
            )
        )).scalar() or 0
        first_day = today.replace(day=1)
        month_revenue = (await self._db.execute(
            select(func.sum(Bill.paid_amount)).where(
                Bill.deleted_at.is_(None), Bill.status == "paid", func.date(Bill.payment_time) >= first_day
            )
        )).scalar() or 0
        total_bills = (await self._db.execute(
            select(func.count(Bill.id)).where(Bill.deleted_at.is_(None), Bill.status == "paid")
        )).scalar() or 0
        today_new_patients = (await self._db.execute(
            select(func.count(Patient.id)).where(Patient.deleted_at.is_(None), func.date(Patient.created_at) == today)
        )).scalar() or 0
        month_new_patients = (await self._db.execute(
            select(func.count(Patient.id)).where(
                Patient.deleted_at.is_(None), func.date(Patient.created_at) >= first_day
            )
        )).scalar() or 0
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "total_users": total_users,
            "total_patients": total_patients,
            "total_registrations": total_registrations,
            "total_medical_records": total_medical_records,
            "total_revenue": float(total_revenue),
            "today_revenue": float(today_revenue),
            "month_revenue": float(month_revenue),
            "total_bills": total_bills,
            "today_new_patients": today_new_patients,
            "month_new_patients": month_new_patients,
        }

    async def change_password(self, admin_id: str, old_password: str, new_password: str) -> bool:
        admin = await self.get_platform_admin(admin_id)
        if not verify_password(old_password, admin.password_hash):
            raise CustomException(msg="旧密码错误", code=400, status_code=400)
        if len(new_password) < 6:
            raise CustomException(msg="新密码长度至少为6位", code=400, status_code=400)
        admin.password_hash = get_password_hash(new_password)
        await self._db.commit()
        logger.info(f"平台管理员 {admin_id} 修改密码成功")
        return True

    async def update_tenant_admin_password(self, tenant_id: str, new_password: str, updater_id: Optional[str] = None) -> bool:
        if len(new_password) < 6:
            raise CustomException(msg="新密码长度至少为6位", code=400, status_code=400)
        tenant = (await self._db.execute(
            select(Tenant).where(Tenant.id == _to_uuid(tenant_id), Tenant.deleted_at.is_(None))
        )).scalars().first()
        if not tenant:
            raise CustomException(msg="租户不存在", code=404, status_code=404)
        admin_user = (await self._db.execute(
            select(User).where(
                User.tenant_id == _to_uuid(tenant_id), User.username == "admin", User.deleted_at.is_(None)
            )
        )).scalars().first()
        if not admin_user:
            raise CustomException(msg="租户管理员不存在", code=404, status_code=404)
        admin_user.password_hash = get_password_hash(new_password)
        if updater_id:
            admin_user.updated_by = _to_uuid(updater_id)
        await self._db.commit()
        logger.info(f"平台管理员 {updater_id} 修改租户 {tenant.code} 的管理员密码成功")
        return True


def or_like(column, value):
    from sqlalchemy import or_
    return or_(column.ilike(f"%{value}%"))
