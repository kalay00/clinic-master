"""
打印模板数据仓库
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID

from app.api.v1.module_print_template.model import PrintTemplate
from app.core.exceptions import NotFoundException
from app.core.logger import logger


class PrintTemplateRepository:
    """打印模板数据仓库"""
    
    def __init__(self, db: Session):
        """
        初始化打印模板仓库
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def create(self, template_data: dict, tenant_id: str) -> PrintTemplate:
        """
        创建打印模板
        
        Args:
            template_data: 模板数据字典，包含name, type, template_config, is_default等
            tenant_id: 租户ID
            
        Returns:
            PrintTemplate: 创建的模板对象
        """
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        template = PrintTemplate(
            tenant_id=tenant_id_uuid,
            name=template_data["name"],
            type=template_data["type"],
            template_config=template_data["template_config"],
            is_default=template_data.get("is_default", False)
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def update(self, template_id: str, template_data: dict, tenant_id: str) -> PrintTemplate:
        """
        更新打印模板
        
        Args:
            template_id: 模板ID
            template_data: 更新的模板数据
            tenant_id: 租户ID
            
        Returns:
            PrintTemplate: 更新后的模板对象
            
        Raises:
            NotFoundException: 模板不存在
        """
        template = self.get_by_id(template_id, tenant_id)
        if not template:
            raise NotFoundException("打印模板", template_id)
        
        # 更新字段
        if "name" in template_data:
            template.name = template_data["name"]
        if "type" in template_data:
            template.type = template_data["type"]
        if "template_config" in template_data:
            template.template_config = template_data["template_config"]
        if "is_default" in template_data:
            template.is_default = template_data["is_default"]
        
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def delete(self, template_id: str, tenant_id: str) -> bool:
        """
        删除打印模板（软删除）
        
        Args:
            template_id: 模板ID
            tenant_id: 租户ID
            
        Returns:
            bool: 删除成功返回True
            
        Raises:
            NotFoundException: 模板不存在
        """
        template = self.get_by_id(template_id, tenant_id)
        if not template:
            raise NotFoundException("打印模板", template_id)
        
        template.soft_delete()
        self.db.commit()
        return True
    
    def get_by_id(self, template_id: str, tenant_id: str) -> Optional[PrintTemplate]:
        """
        根据ID获取打印模板
        
        Args:
            template_id: 模板ID
            tenant_id: 租户ID
            
        Returns:
            Optional[PrintTemplate]: 模板对象，不存在返回None
        """
        # 转换ID为UUID
        if isinstance(template_id, str):
            try:
                template_id_uuid = UUID(template_id)
            except (ValueError, TypeError):
                template_id_uuid = template_id
        else:
            template_id_uuid = template_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(PrintTemplate).filter(
            and_(
                PrintTemplate.id == template_id_uuid,
                PrintTemplate.tenant_id == tenant_id_uuid,
                PrintTemplate.deleted_at.is_(None)
            )
        ).first()
    
    def list_by_type(
        self,
        tenant_id: str,
        template_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[PrintTemplate], int]:
        """
        获取打印模板列表
        
        Args:
            tenant_id: 租户ID
            template_type: 模板类型（可选：bill/prescription/medical_record）
            skip: 跳过的记录数
            limit: 每页记录数
            
        Returns:
            tuple[List[PrintTemplate], int]: (模板列表, 总数)
        """
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(PrintTemplate).filter(
            and_(
                PrintTemplate.tenant_id == tenant_id_uuid,
                PrintTemplate.deleted_at.is_(None)
            )
        )
        
        if template_type:
            query = query.filter(PrintTemplate.type == template_type)
        
        total = query.count()
        templates = query.order_by(
            PrintTemplate.is_default.desc(),  # 默认模板排在前面
            PrintTemplate.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return templates, total
    
    def get_default_template(self, tenant_id: str, template_type: str) -> Optional[PrintTemplate]:
        """
        获取指定类型的默认模板
        
        Args:
            tenant_id: 租户ID
            template_type: 模板类型
            
        Returns:
            Optional[PrintTemplate]: 默认模板，不存在返回None
        """
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(PrintTemplate).filter(
            and_(
                PrintTemplate.tenant_id == tenant_id_uuid,
                PrintTemplate.type == template_type,
                PrintTemplate.is_default == True,
                PrintTemplate.deleted_at.is_(None)
            )
        ).first()
    
    def set_default_template(self, template_id: str, tenant_id: str) -> PrintTemplate:
        """
        设置默认模板（会取消同类型的其他默认模板）
        
        Args:
            template_id: 模板ID
            tenant_id: 租户ID
            
        Returns:
            PrintTemplate: 更新后的模板对象
            
        Raises:
            NotFoundException: 模板不存在
        """
        template = self.get_by_id(template_id, tenant_id)
        if not template:
            raise NotFoundException("打印模板", template_id)
        
        # 取消同类型的其他默认模板
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        self.db.query(PrintTemplate).filter(
            and_(
                PrintTemplate.tenant_id == tenant_id_uuid,
                PrintTemplate.type == template.type,
                PrintTemplate.id != template.id,
                PrintTemplate.is_default == True,
                PrintTemplate.deleted_at.is_(None)
            )
        ).update({"is_default": False})
        
        # 设置当前模板为默认
        template.is_default = True
        self.db.commit()
        self.db.refresh(template)
        return template

