"""
认证依赖（对齐 FastapiAdmin: app.core.dependencies）
复用 outpatient 既有 JWT 中间件写入 request.state 的 user / tenant_id，
封装为 AuthSchema 供 Controller → Service → CRUD 传递。
"""
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from types import SimpleNamespace
from typing import Any

from app.core.base_schema import AuthSchema
from app.core.database import get_async_db
from app.core.exceptions import CustomException
from app.core.logger import logger


class _PayloadUser(SimpleNamespace):
    """将 JWT payload（dict）包装为带属性的用户对象，供 CRUDBase / Permission 使用。

    注意：不要在此定义名为 is_superuser/roles/permissions 等的 property——
    SimpleNamespace 已把构造参数存为实例属性，同名 property 会作为数据描述符
    覆盖实例 __dict__，导致 getattr 自引用无限递归（RecursionError）。
    """



async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> AuthSchema:
    """
    从 request.state（JWT 中间件写入）构建 AuthSchema。
    未登录（白名单路径）时 user 为 None，由 Controller 自行决定是否放行。
    """
    user = getattr(request.state, "user", None)
    tenant_id = getattr(request.state, "tenant_id", None)

    auth = AuthSchema(db=db, tenant_id=tenant_id, check_data_scope=False)
    if user and isinstance(user, dict):
        # 兼容 dict 型 payload：暴露 id / is_superuser / roles / permissions
        # 权限实时从数据库读取（以用户角色的最新配置为准），
        # 避免 token 中冻结的旧权限导致新增资源后必须重新登录才生效。
        permissions = list(user.get("permissions", []))
        user_id = user.get("user_id")
        if user_id:
            try:
                from sqlalchemy import select
                from app.api.v1.module_role.model import (
                    Permission,
                    RolePermission,
                    UserRole,
                )

                res = await db.execute(
                    select(Permission.code)
                    .join(RolePermission, RolePermission.permission_id == Permission.id)
                    .join(UserRole, UserRole.role_id == RolePermission.role_id)
                    .where(UserRole.user_id == user_id, Permission.deleted_at.is_(None))
                    .distinct()
                )
                live_codes = [row[0] for row in res.all()]
                if live_codes:
                    permissions = live_codes
            except Exception as e:
                # 读取失败时回退到 token 中携带的权限，但记录日志便于排查
                logger.warning(f"实时读取用户权限失败，回退至 token 权限: {e}")
        auth.user = _PayloadUser(
            id=user.get("user_id"),
            tenant_id=user.get("tenant_id"),
            is_superuser=user.get("is_superuser", False),
            roles=user.get("roles", []),
            permissions=permissions,
        )
        auth.tenant_id = tenant_id or user.get("tenant_id")
    else:
        auth.user = user
    return auth


class AuthPermission:
    """
    权限验证类（对齐 FastapiAdmin: app.core.dependencies.AuthPermission）
    本系统权限标识可选；未配置 permission 列表时直接放行。
    """

    def __init__(
        self,
        permission: list[str] | None = None,
        permissions: list[str] | None = None,
        check_data_scope: bool = False,
    ) -> None:
        # 兼容 FastapiAdmin 的 permission= 与复数 permissions= 两种写法
        self.permissions = permission or permissions or []
        self.check_data_scope = check_data_scope

    async def __call__(self, auth: AuthSchema = Depends(get_current_user)) -> AuthSchema:
        auth = auth.model_copy(update={"check_data_scope": self.check_data_scope})

        if not self.permissions:
            return auth

        user = auth.get_user()
        if user is None:
            raise CustomException(msg="未授权访问", code=10401, status_code=401)

        # 平台/超级管理员直接通过
        if getattr(user, "is_superuser", False):
            return auth

        # 从 user 对象或 payload 收集权限集合
        user_perms = _collect_permissions(user)
        if not any(perm in user_perms for perm in self.permissions):
            raise CustomException(msg="无权限操作", code=10403, status_code=403)
        return auth


def _collect_permissions(user: Any) -> set[str]:
    perms: set[str] = set()

    def _add(code: str) -> None:
        # 同时保留原始码与去租户前缀码，与前端 permission.js matchesPermission 逻辑保持一致：
        # - 原始码：保证含下划线的资源名（如 print_template:list）不被误切
        # - 去前缀码：兼容历史带租户前缀的权限码（如 TEST001_treatment:list -> treatment:list），平滑过渡旧 JWT
        if not isinstance(code, str) or not code:
            return
        perms.add(code)
        if "_" in code:
            perms.add(code.split("_", 1)[1])

    # ORM 用户对象：roles -> permissions / menus.permission
    roles = getattr(user, "roles", None) or []
    for role in roles:
        for perm in getattr(role, "permissions", None) or []:
            if getattr(perm, "code", None):
                _add(perm.code)
        for menu in getattr(role, "menus", None) or []:
            if getattr(menu, "permission", None):
                _add(menu.permission)
    # 直接携带权限标识的用户：
    # - dict payload（旧式）：user["permissions"] 为权限码列表
    # - _PayloadUser 等包装对象（get_current_user 把 JWT payload 包成 SimpleNamespace）：
    #   user.permissions 同样为权限码列表，必须读取，否则 JWT 下发的权限被丢弃导致 403
    if isinstance(user, dict):
        for p in (user.get("permissions") or []):
            _add(p)
    else:
        obj_perms = getattr(user, "permissions", None)
        if obj_perms:
            for p in obj_perms:
                _add(p)
    return perms
