"""
角色服务（对齐旧 services/user_service.py 中的角色逻辑，迁移为异步 + CRUDBase，Python 3.12+）

业务规则：
- 角色 CRUD
- 角色权限分配 / 撤销 / 查询
"""
from __future__ import annotations
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import Role as RoleModel, Permission as PermissionModel, RolePermission as RolePermissionModel
from .schema import RoleSchema, RoleCreateSchema, RoleUpdateSchema, PermissionSchema
from .crud import RoleCRUD, PermissionCRUD, RolePermissionCRUD


def _to_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return value


class RoleService:
    """Role 服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = RoleCRUD(RoleModel, auth=auth)
        self.permission_crud = PermissionCRUD(PermissionModel, auth=auth)
        self.role_permission_crud = RolePermissionCRUD(RolePermissionModel, auth=auth)

    @property
    def _db(self):
        return self.crud.db

    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    @property
    def _tenant_id(self) -> Optional[str]:
        return self.auth.tenant_id if self.auth else None

    # ── 标准 CRUD ──
    async def get(self, id: str) -> RoleSchema:
        return await self.crud.get_or_404(
            id=id, preload=["permissions"], out_schema=RoleSchema
        )

    async def list(self, page_no: int, page_size: int, order_by=None, search: dict | None = None):
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            out_schema=RoleSchema,
            preload=["permissions"],
        )

    async def create(self, data: RoleCreateSchema) -> RoleSchema:
        obj = await self.crud.create(data)
        uid = self._user_id
        if uid and hasattr(obj, "created_by"):
            setattr(obj, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        return RoleSchema.model_validate(obj)

    async def update(self, id: str, data: RoleUpdateSchema) -> RoleSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return RoleSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 业务方法：权限 ──
    async def assign_permission(self, role_id: str, permission_id: str) -> bool:
        """为角色分配权限（幂等）"""
        rid = _to_uuid(role_id)
        pid = _to_uuid(permission_id)
        stmt = select(RolePermissionModel).where(
            RolePermissionModel.role_id == rid, RolePermissionModel.permission_id == pid
        )
        result = await self._db.execute(stmt)
        if result.scalars().first():
            return True
        self._db.add(RolePermissionModel(role_id=rid, permission_id=pid))
        await self._db.commit()
        logger.info(f"角色分配权限: role={role_id} permission={permission_id}")
        return True

    async def revoke_permission(self, role_id: str, permission_id: str) -> bool:
        """撤销角色权限"""
        rid = _to_uuid(role_id)
        pid = _to_uuid(permission_id)
        stmt = select(RolePermissionModel).where(
            RolePermissionModel.role_id == rid, RolePermissionModel.permission_id == pid
        )
        result = await self._db.execute(stmt)
        rp = result.scalars().first()
        if rp:
            await self._db.delete(rp)
            await self._db.commit()
            logger.info(f"撤销角色权限: role={role_id} permission={permission_id}")
        return True

    async def get_permissions(self, role_id: str) -> List[PermissionSchema]:
        """获取角色权限列表"""
        stmt = (
            select(PermissionModel)
            .join(RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id)
            .where(RolePermissionModel.role_id == _to_uuid(role_id), PermissionModel.deleted_at.is_(None))
        )
        result = await self._db.execute(stmt)
        return [PermissionSchema.model_validate(p) for p in result.scalars().all()]
