"""
用户数据仓库：用户、角色、权限的数据库操作
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from uuid import UUID

from app.api.v1.module_user.model import User
from app.api.v1.module_role.model import Role, Permission, UserRole, RolePermission
from app.core.database import BaseModel
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class UserRepository:
    """用户数据仓库"""
    
    def __init__(self, db: Session):
        """
        初始化用户仓库
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def create_user(self, user_data: dict, tenant_id: str) -> User:
        """
        创建用户
        
        Args:
            user_data: 用户数据
            tenant_id: 租户ID
        
        Returns:
            User: 用户对象
        """
        user = User(
            tenant_id=tenant_id,
            username=user_data["username"],
            password_hash=user_data["password_hash"],
            real_name=user_data.get("real_name"),
            phone=user_data.get("phone"),
            email=user_data.get("email"),
            avatar_url=user_data.get("avatar_url"),
            status=user_data.get("status", "active"),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: str, tenant_id: str) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID
        
        Returns:
            Optional[User]: 用户对象
        """
        return self.db.query(User).filter(
            and_(
                User.id == user_id,
                User.tenant_id == tenant_id,
                User.deleted_at.is_(None)
            )
        ).first()
    
    def get_user_by_username(self, username: str, tenant_id: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            tenant_id: 租户ID（字符串或UUID对象）
        
        Returns:
            Optional[User]: 用户对象
        """
        from uuid import UUID
        # 将tenant_id转换为UUID对象（如果模型使用UUID类型）
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(User).filter(
            and_(
                User.username == username,
                User.tenant_id == tenant_id_uuid,
                User.deleted_at.is_(None)
            )
        ).first()
    
    def get_users_by_username(self, username: str) -> List[User]:
        """
        根据用户名获取所有用户（跨租户，用于多租户登录）
        
        Args:
            username: 用户名
        
        Returns:
            List[User]: 用户列表
        """
        return self.db.query(User).filter(
            and_(
                User.username == username,
                User.deleted_at.is_(None)
            )
        ).all()
    
    def get_users(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """
        获取用户列表
        
        Args:
            tenant_id: 租户ID
            skip: 跳过数量
            limit: 限制数量
            search: 搜索关键词
        
        Returns:
            tuple[List[User], int]: 用户列表和总数
        """
        # 使用joinedload预加载roles关系，避免懒加载问题
        query = self.db.query(User).options(joinedload(User.roles)).filter(
            and_(
                User.tenant_id == tenant_id,
                User.deleted_at.is_(None)
            )
        )
        
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.real_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def update_user(self, user_id: str, tenant_id: str, user_data: dict) -> User:
        """
        更新用户
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID
            user_data: 用户数据
        
        Returns:
            User: 用户对象
        
        Raises:
            NotFoundException: 用户不存在
        """
        user = self.get_user_by_id(user_id, tenant_id)
        if not user:
            raise NotFoundException("用户", user_id)
        
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: str, tenant_id: str) -> bool:
        """
        删除用户（软删除）
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID
        
        Returns:
            bool: 是否成功
        
        Raises:
            NotFoundException: 用户不存在
        """
        user = self.get_user_by_id(user_id, tenant_id)
        if not user:
            raise NotFoundException("用户", user_id)
        
        user.deleted_at = datetime.now()
        self.db.commit()
        return True


class RoleRepository:
    """角色数据仓库"""
    
    def __init__(self, db: Session):
        """
        初始化角色仓库
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def create_role(self, role_data: dict, tenant_id: str) -> Role:
        """
        创建角色
        
        Args:
            role_data: 角色数据
            tenant_id: 租户ID
        
        Returns:
            Role: 角色对象
        """
        role = Role(
            tenant_id=tenant_id,
            name=role_data["name"],
            code=role_data["code"],
            description=role_data.get("description"),
            is_system=role_data.get("is_system", False),
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def get_role_by_id(self, role_id: str, tenant_id: str) -> Optional[Role]:
        """
        根据ID获取角色
        
        Args:
            role_id: 角色ID
            tenant_id: 租户ID
        
        Returns:
            Optional[Role]: 角色对象
        """
        # 使用joinedload预加载permissions关系
        return self.db.query(Role).options(joinedload(Role.permissions)).filter(
            and_(
                Role.id == role_id,
                Role.tenant_id == tenant_id,
                Role.deleted_at.is_(None)
            )
        ).first()
    
    def get_roles(self, tenant_id: str) -> List[Role]:
        """
        获取角色列表
        
        Args:
            tenant_id: 租户ID
        
        Returns:
            List[Role]: 角色列表
        """
        # 使用joinedload预加载users和permissions关系
        return self.db.query(Role).options(
            joinedload(Role.users),
            joinedload(Role.permissions)
        ).filter(
            and_(
                Role.tenant_id == tenant_id,
                Role.deleted_at.is_(None)
            )
        ).all()
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """
        为用户分配角色
        
        Args:
            user_id: 用户ID
            role_id: 角色ID
        
        Returns:
            bool: 是否成功
        """
        # 检查是否已存在
        existing = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        ).first()
        
        if existing:
            return True
        
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        self.db.commit()
        return True
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """
        获取用户角色列表
        
        Args:
            user_id: 用户ID
        
        Returns:
            List[Role]: 角色列表
        """
        return self.db.query(Role).join(UserRole).filter(
            UserRole.user_id == user_id
        ).all()
    
    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """
        获取角色权限列表
        
        Args:
            role_id: 角色ID
        
        Returns:
            List[Permission]: 权限列表
        """
        return self.db.query(Permission).join(RolePermission).filter(
            RolePermission.role_id == role_id
        ).all()
    
    def assign_permission_to_role(self, role_id: str, permission_id: str) -> bool:
        """
        为角色分配权限
        
        Args:
            role_id: 角色ID
            permission_id: 权限ID
        
        Returns:
            bool: 是否成功
        """
        # 检查是否已存在
        existing = self.db.query(RolePermission).filter(
            and_(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            )
        ).first()
        
        if existing:
            return True
        
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(role_permission)
        self.db.commit()
        return True


class PermissionRepository:
    """权限数据仓库"""
    
    def __init__(self, db: Session):
        """
        初始化权限仓库
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def get_permissions(self, tenant_id: Optional[str] = None) -> List[Permission]:
        """
        获取权限列表
        
        Args:
            tenant_id: 租户ID（None表示获取系统权限）
        
        Returns:
            List[Permission]: 权限列表
        """
        query = self.db.query(Permission).filter(
            Permission.deleted_at.is_(None)
        )
        
        if tenant_id:
            query = query.filter(
                or_(
                    Permission.tenant_id == tenant_id,
                    Permission.tenant_id.is_(None)  # 系统权限
                )
            )
        else:
            query = query.filter(Permission.tenant_id.is_(None))
        
        return query.all()
    
    def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """
        根据编码获取权限
        
        Args:
            code: 权限编码
        
        Returns:
            Optional[Permission]: 权限对象
        """
        return self.db.query(Permission).filter(
            and_(
                Permission.code == code,
                Permission.deleted_at.is_(None)
            )
        ).first()
    
    def get_user_permissions(self, user_id: str, tenant_id: str) -> List[Permission]:
        """
        获取用户权限列表（通过角色）
        
        Args:
            user_id: 用户ID
            tenant_id: 租户ID
        
        Returns:
            List[Permission]: 权限列表
        """
        # 将字符串转换为UUID对象（如果模型使用UUID类型）
        if isinstance(user_id, str):
            try:
                user_id_uuid = UUID(user_id)
            except (ValueError, TypeError):
                user_id_uuid = user_id
        else:
            user_id_uuid = user_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        # 通过用户角色获取权限
        return self.db.query(Permission).join(
            RolePermission
        ).join(
            Role
        ).join(
            UserRole
        ).filter(
            and_(
                UserRole.user_id == user_id_uuid,
                Role.tenant_id == tenant_id_uuid,
                Permission.deleted_at.is_(None)
            )
        ).distinct().all()

