"""
平台管理员服务
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.api.v1.module_platform.model import PlatformAdmin
from app.api.v1.module_tenant.model import Tenant
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException, NotFoundException, BusinessException
from app.core.logger import logger


class PlatformAdminService:
    """平台管理员服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def login(self, username: str, password: str, request_ip: str) -> Dict[str, Any]:
        """
        平台管理员登录
        
        Args:
            username: 用户名
            password: 密码
            request_ip: 请求IP
        
        Returns:
            Dict[str, Any]: 包含Token和用户信息
        
        Raises:
            UnauthorizedException: 登录失败
        """
        # 获取平台管理员
        admin = self.db.query(PlatformAdmin).filter(
            PlatformAdmin.username == username,
            PlatformAdmin.deleted_at.is_(None)
        ).first()
        
        if not admin:
            raise UnauthorizedException("用户名或密码错误")
        
        # 验证密码
        if not verify_password(password, admin.password_hash):
            raise UnauthorizedException("用户名或密码错误")
        
        # 检查状态
        if admin.status != "active":
            raise BusinessException(f"管理员状态异常: {admin.status}", code=403)
        
        # 更新最后登录信息
        admin.last_login_at = datetime.now()
        admin.last_login_ip = request_ip
        self.db.commit()
        
        # 生成Token（平台管理员的tenant_id为"platform"）
        token_data = {
            "user_id": str(admin.id),
            "tenant_id": "platform",  # 平台管理员特殊标识
            "username": admin.username,
            "role": "platform_admin",
            "permissions": ["platform:*"]  # 平台管理员拥有所有平台权限
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(admin.id),
                "username": admin.username,
                "real_name": admin.real_name,
                "email": admin.email,
                "role": "platform_admin",
                "tenant_id": None
            }
        }
    
    def get_platform_admin(self, admin_id: str) -> PlatformAdmin:
        """获取平台管理员"""
        admin = self.db.query(PlatformAdmin).filter(
            PlatformAdmin.id == admin_id,
            PlatformAdmin.deleted_at.is_(None)
        ).first()
        
        if not admin:
            raise NotFoundException("平台管理员", admin_id)
        
        return admin
    
    def list_tenants(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Tenant], int]:
        """
        获取所有租户列表（平台管理员）
        
        Args:
            search: 搜索关键词（名称、代码）
            status: 状态过滤
            skip: 跳过数量
            limit: 限制数量
        
        Returns:
            tuple[List[Tenant], int]: 租户列表和总数
        """
        query = self.db.query(Tenant).filter(
            Tenant.deleted_at.is_(None)
        )
        
        if search:
            query = query.filter(
                (Tenant.name.ilike(f"%{search}%")) |
                (Tenant.code.ilike(f"%{search}%"))
            )
        
        if status:
            query = query.filter(Tenant.status == status)
        
        total = query.count()
        tenants = query.order_by(Tenant.created_at.desc()).offset(skip).limit(limit).all()
        
        return tenants, total
    
    def create_tenant(self, tenant_data: Dict[str, Any], creator_id: str) -> Tenant:
        """
        创建租户（平台管理员）
        
        创建租户时会自动创建租户管理员账号（用户名：admin，默认密码：111111）
        
        Args:
            tenant_data: 租户数据
            creator_id: 创建人ID
        
        Returns:
            Tenant: 创建的租户对象
        """
        # 检查租户代码是否已存在
        existing = self.db.query(Tenant).filter(
            Tenant.code == tenant_data["code"],
            Tenant.deleted_at.is_(None)
        ).first()
        
        if existing:
            raise BusinessException(f"租户代码已存在: {tenant_data['code']}", code=400)
        
        # 检查域名是否已存在
        if tenant_data.get("domain"):
            existing_domain = self.db.query(Tenant).filter(
                Tenant.domain == tenant_data["domain"],
                Tenant.deleted_at.is_(None)
            ).first()
            
            if existing_domain:
                raise BusinessException(f"租户域名已存在: {tenant_data['domain']}", code=400)
        
        tenant = Tenant(**tenant_data)
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        
        # 创建租户管理员账号
        try:
            from app.services.user_service import UserService
            from app.api.v1.module_role.model import Role
            from app.api.v1.module_role.model import UserRole
            from app.core.security import get_password_hash
            
            user_service = UserService(self.db)
            
            # 创建租户管理员用户
            admin_username = "admin"
            admin_password = "111111"  # 默认密码
            admin_user_data = {
                "username": admin_username,
                "password": admin_password,
                "real_name": f"{tenant.name}管理员",
                "phone": tenant_data.get("contact_phone", ""),
                "email": tenant_data.get("contact_email", ""),
                "status": "active"
            }
            
            admin_user = user_service.create_user(
                user_data=admin_user_data,
                tenant_id=str(tenant.id),
                creator_id=creator_id
            )
            
            # 查找"admin"角色并分配给用户
            admin_role = self.db.query(Role).filter(
                Role.tenant_id == tenant.id,
                Role.code == "admin",
                Role.deleted_at.is_(None)
            ).first()
            
            if admin_role:
                # 分配角色
                user_role = UserRole(
                    user_id=admin_user.id,
                    role_id=admin_role.id
                )
                self.db.add(user_role)
                self.db.commit()
                logger.info(f"为租户管理员 {admin_user.username} 分配角色: {admin_role.name}")
            else:
                logger.warning(f"租户 {tenant.code} 未找到admin角色，跳过角色分配")
            
            logger.info(f"平台管理员 {creator_id} 创建租户: {tenant.code}，并创建租户管理员: {admin_username}")
        except Exception as e:
            # 如果创建管理员失败，记录错误但不影响租户创建
            logger.error(f"创建租户管理员失败: {str(e)}", exc_info=True)
        
        return tenant
    
    def update_tenant(self, tenant_id: str, tenant_data: Dict[str, Any], updater_id: str) -> Tenant:
        """
        更新租户（平台管理员）
        
        Args:
            tenant_id: 租户ID
            tenant_data: 更新数据
            updater_id: 更新人ID
        
        Returns:
            Tenant: 更新后的租户对象
        """
        tenant = self.db.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.deleted_at.is_(None)
        ).first()
        
        if not tenant:
            raise NotFoundException("租户", tenant_id)
        
        # 更新字段
        for key, value in tenant_data.items():
            if hasattr(tenant, key) and value is not None:
                setattr(tenant, key, value)
        
        self.db.commit()
        self.db.refresh(tenant)
        
        logger.info(f"平台管理员 {updater_id} 更新租户: {tenant.code}")
        return tenant
    
    def delete_tenant(self, tenant_id: str, deleter_id: str) -> bool:
        """
        删除租户（软删除，平台管理员）
        
        Args:
            tenant_id: 租户ID
            deleter_id: 删除人ID
        
        Returns:
            bool: 是否成功
        """
        tenant = self.db.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.deleted_at.is_(None)
        ).first()
        
        if not tenant:
            raise NotFoundException("租户", tenant_id)
        
        # 软删除
        tenant.deleted_at = datetime.now()
        self.db.commit()
        
        logger.info(f"平台管理员 {deleter_id} 删除租户: {tenant.code}")
        return True
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """
        获取平台统计数据（跨所有租户）
        
        Returns:
            Dict[str, Any]: 平台统计数据
        """
        from app.api.v1.module_user.model import User
        from app.api.v1.module_patient.model import Patient
        from app.api.v1.module_platform.model import PlatformAdmin
        from app.api.v1.module_tenant.model import Tenant
        from app.api.v1.module_payment.model import Bill
        from app.api.v1.module_registration.model import Registration
        from app.api.v1.module_treatment.model import MedicalRecord
        from sqlalchemy import func, and_
        from datetime import datetime, timedelta
        
        # 总租户数
        total_tenants = self.db.query(func.count(Tenant.id)).filter(
            Tenant.deleted_at.is_(None)
        ).scalar() or 0
        
        # 活跃租户数（状态为active）
        active_tenants = self.db.query(func.count(Tenant.id)).filter(
            Tenant.deleted_at.is_(None),
            Tenant.status == "active"
        ).scalar() or 0
        
        # 总用户数（所有租户的用户，不包括平台管理员）
        total_users = self.db.query(func.count(User.id)).filter(
            User.deleted_at.is_(None)
        ).scalar() or 0
        
        # 总患者数（所有租户的患者）
        total_patients = self.db.query(func.count(Patient.id)).filter(
            Patient.deleted_at.is_(None)
        ).scalar() or 0
        
        # 总挂号数
        total_registrations = self.db.query(func.count(Registration.id)).filter(
            Registration.deleted_at.is_(None)
        ).scalar() or 0
        
        # 总病历数
        total_medical_records = self.db.query(func.count(MedicalRecord.id)).filter(
            MedicalRecord.deleted_at.is_(None)
        ).scalar() or 0
        
        # 总收入（所有已支付账单）
        total_revenue = self.db.query(func.sum(Bill.paid_amount)).filter(
            Bill.deleted_at.is_(None),
            Bill.status == "paid"
        ).scalar() or 0
        
        # 今日收入
        today = datetime.now().date()
        today_revenue = self.db.query(func.sum(Bill.paid_amount)).filter(
            Bill.deleted_at.is_(None),
            Bill.status == "paid",
            func.date(Bill.payment_time) == today
        ).scalar() or 0
        
        # 本月收入
        first_day_of_month = datetime.now().replace(day=1).date()
        month_revenue = self.db.query(func.sum(Bill.paid_amount)).filter(
            Bill.deleted_at.is_(None),
            Bill.status == "paid",
            func.date(Bill.payment_time) >= first_day_of_month
        ).scalar() or 0
        
        # 总账单数（已支付）
        total_bills = self.db.query(func.count(Bill.id)).filter(
            Bill.deleted_at.is_(None),
            Bill.status == "paid"
        ).scalar() or 0
        
        # 今日新增患者数
        today_new_patients = self.db.query(func.count(Patient.id)).filter(
            Patient.deleted_at.is_(None),
            func.date(Patient.created_at) == today
        ).scalar() or 0
        
        # 本月新增患者数
        month_new_patients = self.db.query(func.count(Patient.id)).filter(
            Patient.deleted_at.is_(None),
            func.date(Patient.created_at) >= first_day_of_month
        ).scalar() or 0
        
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
            "month_new_patients": month_new_patients
        }
    
    def change_password(
        self,
        admin_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        修改平台管理员密码
        
        Args:
            admin_id: 管理员ID
            old_password: 旧密码
            new_password: 新密码
        
        Returns:
            bool: 是否成功
        
        Raises:
            UnauthorizedException: 旧密码错误
            BusinessException: 新密码不符合要求
        """
        admin = self.get_platform_admin(admin_id)
        
        # 验证旧密码
        if not verify_password(old_password, admin.password_hash):
            raise UnauthorizedException("旧密码错误")
        
        # 验证新密码长度
        if len(new_password) < 6:
            raise BusinessException("新密码长度至少为6位", code=400)
        
        # 更新密码
        admin.password_hash = get_password_hash(new_password)
        self.db.commit()
        
        logger.info(f"平台管理员 {admin_id} 修改密码成功")
        return True
    
    def update_tenant_admin_password(
        self,
        tenant_id: str,
        new_password: str,
        updater_id: str
    ) -> bool:
        """
        修改租户管理员密码（平台管理员）
        
        Args:
            tenant_id: 租户ID
            new_password: 新密码
            updater_id: 更新人ID（平台管理员ID）
        
        Returns:
            bool: 是否成功
        
        Raises:
            NotFoundException: 租户不存在或租户管理员不存在
            BusinessException: 新密码不符合要求
        """
        # 验证租户是否存在
        tenant = self.db.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.deleted_at.is_(None)
        ).first()
        
        if not tenant:
            raise NotFoundException("租户", tenant_id)
        
        # 验证新密码长度
        if len(new_password) < 6:
            raise BusinessException("新密码长度至少为6位", code=400)
        
        # 查找租户管理员（用户名为admin的用户）
        from app.api.v1.module_user.model import User
        
        admin_user = self.db.query(User).filter(
            User.tenant_id == tenant_id,
            User.username == "admin",
            User.deleted_at.is_(None)
        ).first()
        
        if not admin_user:
            raise NotFoundException("租户管理员", f"租户 {tenant.code} 的管理员账号")
        
        # 更新密码
        from app.core.security import get_password_hash
        admin_user.password_hash = get_password_hash(new_password)
        admin_user.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"平台管理员 {updater_id} 修改租户 {tenant.code} 的管理员密码成功")
        return True

