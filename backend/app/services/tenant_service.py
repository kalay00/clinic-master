"""
租户服务：租户配置管理
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import json

from app.api.v1.module_tenant.model import Tenant
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class TenantService:
    """租户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_tenant_by_code(self, tenant_code: str) -> Tenant:
        """
        根据租户代码获取租户
        
        Args:
            tenant_code: 租户代码
        
        Returns:
            Tenant: 租户对象
        
        Raises:
            NotFoundException: 租户不存在
        """
        tenant = self.db.query(Tenant).filter(
            Tenant.code == tenant_code,
            Tenant.deleted_at.is_(None),
            Tenant.status == "active"
        ).first()
        
        if not tenant:
            raise NotFoundException("租户", tenant_code)
        
        return tenant
    
    def get_tenant_by_domain(self, domain: str) -> Tenant:
        """
        根据域名获取租户
        
        Args:
            domain: 租户域名（如：test001.his.example.com）
        
        Returns:
            Tenant: 租户对象
        
        Raises:
            NotFoundException: 租户不存在
        """
        tenant = self.db.query(Tenant).filter(
            Tenant.domain == domain,
            Tenant.deleted_at.is_(None),
            Tenant.status == "active"
        ).first()
        
        if not tenant:
            raise NotFoundException("租户", domain)
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Tenant:
        """
        获取租户信息
        
        Args:
            tenant_id: 租户ID
        
        Returns:
            Tenant: 租户对象
        
        Raises:
            NotFoundException: 租户不存在
        """
        tenant = self.db.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.deleted_at.is_(None)
        ).first()
        
        if not tenant:
            raise NotFoundException("租户", tenant_id)
        
        return tenant
    
    def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """
        获取租户配置
        
        Args:
            tenant_id: 租户ID
        
        Returns:
            Dict[str, Any]: 租户配置字典
        """
        tenant = self.get_tenant(tenant_id)
        
        # 如果配置为空，返回默认配置
        if tenant.config is None:
            return self.get_default_config()
        
        # 合并默认配置和现有配置
        default_config = self.get_default_config()
        user_config = tenant.config if isinstance(tenant.config, dict) else {}
        default_config.update(user_config)
        
        return default_config
    
    def update_tenant_config(
        self,
        tenant_id: str,
        config_updates: Dict[str, Any],
        updater_id: str
    ) -> Tenant:
        """
        更新租户配置
        
        Args:
            tenant_id: 租户ID
            config_updates: 配置更新项
            updater_id: 更新人ID
        
        Returns:
            Tenant: 更新后的租户对象
        
        Raises:
            NotFoundException: 租户不存在
            BusinessException: 配置验证失败
        """
        tenant = self.get_tenant(tenant_id)
        
        # 获取当前配置
        current_config = tenant.config if tenant.config else {}
        if not isinstance(current_config, dict):
            current_config = {}
        
        # 合并配置更新
        updated_config = {**current_config, **config_updates}
        
        # 验证配置
        self.validate_config(updated_config)
        
        # 更新配置
        tenant.config = updated_config
        self.db.commit()
        self.db.refresh(tenant)
        
        logger.info(f"更新租户配置: {tenant_id} by {updater_id}")
        return tenant
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return {
            # 药师审核设置
            "pharmacist_review_enabled": True,  # 药师审核开关，默认开启
            
            # 挂号设置
            "registration": {
                "max_advance_days": 30,  # 最大提前预约天数
                "default_fee": 10.0,  # 默认挂号费
                "allow_same_day": True,  # 允许当天挂号
                "auto_complete_visit": False,  # 自动完成就诊（支付后自动完成）
            },
            
            # 处方设置
            "prescription": {
                "validity_days": 7,  # 处方有效期（天）
                "default_type": "western",  # 默认处方类型：western/traditional/chinese_medicine
                "require_doctor_signature": True,  # 需要医生签名
                "allow_edit_after_save": False,  # 保存后允许编辑
            },
            
            # 打印设置
            "print": {
                "default_bill_template": None,  # 默认账单打印模板ID
                "default_prescription_template": None,  # 默认处方打印模板ID
                "default_medical_record_template": None,  # 默认病历打印模板ID
                "auto_print_after_payment": False,  # 支付后自动打印
            },
            
            # 系统设置
            "system": {
                "session_timeout": 3600,  # 会话超时时间（秒）
                "password_min_length": 6,  # 密码最小长度
                "require_password_change": False,  # 首次登录要求修改密码
                "enable_audit_log": True,  # 启用审计日志
            },
        }
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """
        验证配置
        
        Args:
            config: 配置字典
        
        Raises:
            BusinessException: 配置验证失败
        """
        # 验证药师审核开关
        if "pharmacist_review_enabled" in config:
            if not isinstance(config["pharmacist_review_enabled"], bool):
                raise BusinessException("药师审核开关必须是布尔值", code=400)
        
        # 验证挂号设置
        if "registration" in config:
            reg_config = config["registration"]
            if not isinstance(reg_config, dict):
                raise BusinessException("挂号设置必须是对象", code=400)
            if "max_advance_days" in reg_config:
                if not isinstance(reg_config["max_advance_days"], int) or reg_config["max_advance_days"] < 1:
                    raise BusinessException("最大提前预约天数必须是大于0的整数", code=400)
            if "default_fee" in reg_config:
                if not isinstance(reg_config["default_fee"], (int, float)) or reg_config["default_fee"] < 0:
                    raise BusinessException("默认挂号费必须是非负数", code=400)
        
        # 验证处方设置
        if "prescription" in config:
            pres_config = config["prescription"]
            if not isinstance(pres_config, dict):
                raise BusinessException("处方设置必须是对象", code=400)
            if "validity_days" in pres_config:
                if not isinstance(pres_config["validity_days"], int) or pres_config["validity_days"] < 1:
                    raise BusinessException("处方有效期必须是大于0的整数", code=400)
            if "default_type" in pres_config:
                if pres_config["default_type"] not in ["western", "traditional", "chinese_medicine"]:
                    raise BusinessException("默认处方类型必须是 western/traditional/chinese_medicine", code=400)
        
        # 验证系统设置
        if "system" in config:
            sys_config = config["system"]
            if not isinstance(sys_config, dict):
                raise BusinessException("系统设置必须是对象", code=400)
            if "session_timeout" in sys_config:
                if not isinstance(sys_config["session_timeout"], int) or sys_config["session_timeout"] < 300:
                    raise BusinessException("会话超时时间必须是不小于300秒的整数", code=400)
            if "password_min_length" in sys_config:
                if not isinstance(sys_config["password_min_length"], int) or sys_config["password_min_length"] < 6:
                    raise BusinessException("密码最小长度必须是不小于6的整数", code=400)
    
    def is_pharmacist_review_enabled(self, tenant_id: str) -> bool:
        """
        检查药师审核是否启用
        
        Args:
            tenant_id: 租户ID
        
        Returns:
            bool: 是否启用药师审核
        """
        config = self.get_tenant_config(tenant_id)
        return config.get("pharmacist_review_enabled", True)

