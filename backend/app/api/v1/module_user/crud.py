"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import User
from app.api.v1.module_role.model import Role, Permission, UserRole, RolePermission
from .schema import UserSchema, UserCreateSchema, UserUpdateSchema, RoleSchema, RoleCreateSchema, RoleUpdateSchema, PermissionSchema, PermissionCreateSchema, PermissionUpdateSchema, UserRoleSchema, UserRoleCreateSchema, UserRoleUpdateSchema, RolePermissionSchema, RolePermissionCreateSchema, RolePermissionUpdateSchema



class UserCRUD(CRUDBase[User, UserCreateSchema, UserUpdateSchema]):
    """User 数据层"""

    pass


class RoleCRUD(CRUDBase[Role, RoleCreateSchema, RoleUpdateSchema]):
    """Role 数据层"""

    pass


class PermissionCRUD(CRUDBase[Permission, PermissionCreateSchema, PermissionUpdateSchema]):
    """Permission 数据层"""

    pass


class UserRoleCRUD(CRUDBase[UserRole, UserRoleCreateSchema, UserRoleUpdateSchema]):
    """UserRole 数据层"""

    pass


class RolePermissionCRUD(CRUDBase[RolePermission, RolePermissionCreateSchema, RolePermissionUpdateSchema]):
    """RolePermission 数据层"""

    pass

