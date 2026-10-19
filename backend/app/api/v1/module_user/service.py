"""
用户服务（对齐旧 services/user_service.py，迁移为异步 + CRUDBase，Python 3.12+）

业务规则：
- 用户名在同一租户内唯一
- 创建/更新时维护密码哈希（password_hash 字段透传，兼容前端预哈希契约）
- 角色分配 / 撤销 / 权限查询
"""
from __future__ import annotations
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select

from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from app.core.logger import logger

from .model import User as UserModel
from app.api.v1.module_role.model import (
    Role as RoleModel,
    Permission as PermissionModel,
    UserRole as UserRoleModel,
    RolePermission as RolePermissionModel,
)
from .schema import (
    UserSchema,
    UserCreateSchema,
    UserUpdateSchema,
    RoleSchema,
    PermissionSchema,
)
from .crud import (
    UserCRUD,
    RoleCRUD,
    PermissionCRUD,
    UserRoleCRUD,
    RolePermissionCRUD,
)


def _to_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return value


class UserService:
    """User 服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = UserCRUD(UserModel, auth=auth)
        self.role_crud = RoleCRUD(RoleModel, auth=auth)
        self.permission_crud = PermissionCRUD(PermissionModel, auth=auth)
        self.user_role_crud = UserRoleCRUD(UserRoleModel, auth=auth)
        self.role_permission_crud = RolePermissionCRUD(RolePermissionModel, auth=auth)

    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    @property
    def _tenant_id(self) -> Optional[str]:
        return self.auth.tenant_id if self.auth else None

    @property
    def _db(self):
        return self.crud.db

    # ── 标准 CRUD ──
    async def create(self, data: UserCreateSchema) -> UserSchema:
        # 用户名唯一性校验（同租户）
        await self._ensure_username_available(data.username, None)
        payload = data.model_dump()
        tenant_id = self._tenant_id or payload.get("tenant_id")
        if tenant_id:
            payload["tenant_id"] = tenant_id
        user = await self.crud.create(payload)
        uid = self._user_id
        if uid and hasattr(user, "created_by"):
            setattr(user, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        logger.info(f"创建用户: {user.id} by {uid}")
        return UserSchema.model_validate(user)

    async def get(self, id: str) -> UserSchema:
        return await self.crud.get_or_404(id=id, out_schema=UserSchema)

    async def list(self, page_no: int, page_size: int, order_by=None, search: dict | None = None):
        page_res = await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search or {},
            out_schema=UserSchema,
        )
        # 为每个用户聚合角色名称，便于前端列表展示
        for item in page_res.items:
            try:
                roles = await self.get_user_roles(item.get("id"))
                item["roles"] = [r.name for r in roles]
            except Exception:
                item["roles"] = []
        return page_res

    async def update(self, id: str, data: UserUpdateSchema) -> UserSchema:
        await self._ensure_username_available(data.username, id)
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return UserSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    # ── 业务方法 ──
    async def _ensure_username_available(self, username: str, exclude_id: Optional[str]) -> None:
        tenant_id = _to_uuid(self._tenant_id)
        stmt = select(UserModel).where(
            UserModel.username == username,
            UserModel.tenant_id == tenant_id,
            UserModel.deleted_at.is_(None),
        )
        if exclude_id:
            stmt = stmt.where(UserModel.id != _to_uuid(exclude_id))
        result = await self._db.execute(stmt)
        if result.scalars().first():
            raise CustomException(msg="用户名已存在", code=400, status_code=400)

    async def assign_role(self, user_id: str, role_id: str) -> bool:
        """为用户分配角色（幂等）"""
        uid = _to_uuid(user_id)
        rid = _to_uuid(role_id)
        stmt = select(UserRoleModel).where(
            UserRoleModel.user_id == uid, UserRoleModel.role_id == rid
        )
        result = await self._db.execute(stmt)
        if result.scalars().first():
            return True
        self._db.add(UserRoleModel(user_id=uid, role_id=rid))
        await self._db.commit()
        logger.info(f"分配角色: user={user_id} role={role_id}")
        return True

    async def revoke_role(self, user_id: str, role_id: str) -> bool:
        """撤销用户角色"""
        uid = _to_uuid(user_id)
        rid = _to_uuid(role_id)
        stmt = select(UserRoleModel).where(
            UserRoleModel.user_id == uid, UserRoleModel.role_id == rid
        )
        result = await self._db.execute(stmt)
        ur = result.scalars().first()
        if ur:
            await self._db.delete(ur)
            await self._db.commit()
            logger.info(f"撤销角色: user={user_id} role={role_id}")
        return True

    async def get_user_roles(self, user_id: str) -> List[RoleSchema]:
        stmt = (
            select(RoleModel)
            .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
            .where(UserRoleModel.user_id == _to_uuid(user_id), RoleModel.deleted_at.is_(None))
        )
        result = await self._db.execute(stmt)
        return [RoleSchema.model_validate(r) for r in result.scalars().all()]

    async def get_user_permissions(self, user_id: str) -> List[PermissionSchema]:
        stmt = (
            select(PermissionModel)
            .join(RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id)
            .join(UserRoleModel, UserRoleModel.role_id == RolePermissionModel.role_id)
            .where(UserRoleModel.user_id == _to_uuid(user_id), PermissionModel.deleted_at.is_(None))
            .distinct()
        )
        result = await self._db.execute(stmt)
        return [PermissionSchema.model_validate(p) for p in result.scalars().all()]
