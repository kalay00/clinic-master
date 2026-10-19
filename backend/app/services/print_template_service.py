"""
打印模板服务：模板管理、模板渲染
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import json

from app.api.v1.module_print_template.model import PrintTemplate
from app.repositories.print_template_repository import PrintTemplateRepository
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class PrintTemplateService:
    """打印模板服务类"""
    
    def __init__(self, db: Session):
        """
        初始化打印模板服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.template_repo = PrintTemplateRepository(db)
    
    def create_template(
        self,
        template_data: Dict[str, Any],
        tenant_id: str,
        creator_id: Optional[str] = None
    ) -> PrintTemplate:
        """
        创建打印模板
        
        Args:
            template_data: 模板数据，包含name, type, template_config, is_default
            tenant_id: 租户ID
            creator_id: 创建人ID
            
        Returns:
            PrintTemplate: 创建的模板对象
            
        Raises:
            BusinessException: 数据验证失败
        """
        # 验证模板数据
        self._validate_template_data(template_data)
        
        # 如果设置为默认模板，需要取消同类型的其他默认模板
        if template_data.get("is_default", False):
            # 在创建前检查是否有默认模板
            existing_default = self.template_repo.get_default_template(
                tenant_id, template_data["type"]
            )
            if existing_default:
                # 取消现有默认模板
                existing_default.is_default = False
                self.db.commit()
        
        # 创建模板
        template = self.template_repo.create(template_data, tenant_id)
        
        if creator_id:
            template.created_by = creator_id
            self.db.commit()
        
        logger.info(f"创建打印模板: {template.id} ({template.name}) by {creator_id}")
        return template
    
    def update_template(
        self,
        template_id: str,
        template_data: Dict[str, Any],
        tenant_id: str,
        updater_id: Optional[str] = None
    ) -> PrintTemplate:
        """
        更新打印模板
        
        Args:
            template_id: 模板ID
            template_data: 更新的模板数据
            tenant_id: 租户ID
            updater_id: 更新人ID
            
        Returns:
            PrintTemplate: 更新后的模板对象
            
        Raises:
            NotFoundException: 模板不存在
            BusinessException: 数据验证失败
        """
        # 验证模板数据
        if "template_config" in template_data:
            self._validate_template_config(template_data["template_config"])
        
        # 如果设置为默认模板，需要取消同类型的其他默认模板
        if template_data.get("is_default", False):
            template = self.template_repo.get_by_id(template_id, tenant_id)
            if not template:
                raise NotFoundException("打印模板", template_id)
            
            existing_default = self.template_repo.get_default_template(
                tenant_id, template.type
            )
            if existing_default and existing_default.id != template_id:
                # 取消现有默认模板
                existing_default.is_default = False
                self.db.commit()
        
        # 更新模板
        template = self.template_repo.update(template_id, template_data, tenant_id)
        
        if updater_id:
            template.updated_by = updater_id
            self.db.commit()
        
        logger.info(f"更新打印模板: {template.id} ({template.name}) by {updater_id}")
        return template
    
    def delete_template(
        self,
        template_id: str,
        tenant_id: str
    ) -> bool:
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
        template = self.template_repo.get_by_id(template_id, tenant_id)
        if not template:
            raise NotFoundException("打印模板", template_id)
        
        # 如果是默认模板，删除后需要设置同类型的第一个模板为默认
        if template.is_default:
            templates, _ = self.template_repo.list_by_type(
                tenant_id, template.type, skip=0, limit=1
            )
            # 排除当前要删除的模板
            other_templates = [t for t in templates if t.id != template_id]
            if other_templates:
                # 设置第一个为默认
                other_templates[0].is_default = True
                self.db.commit()
        
        result = self.template_repo.delete(template_id, tenant_id)
        logger.info(f"删除打印模板: {template_id}")
        return result
    
    def get_template(self, template_id: str, tenant_id: str) -> PrintTemplate:
        """
        获取打印模板详情
        
        Args:
            template_id: 模板ID
            tenant_id: 租户ID
            
        Returns:
            PrintTemplate: 模板对象
            
        Raises:
            NotFoundException: 模板不存在
        """
        template = self.template_repo.get_by_id(template_id, tenant_id)
        if not template:
            raise NotFoundException("打印模板", template_id)
        return template
    
    def list_templates(
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
            template_type: 模板类型（可选）
            skip: 跳过的记录数
            limit: 每页记录数
            
        Returns:
            tuple[List[PrintTemplate], int]: (模板列表, 总数)
        """
        return self.template_repo.list_by_type(tenant_id, template_type, skip, limit)
    
    def set_default_template(
        self,
        template_id: str,
        tenant_id: str
    ) -> PrintTemplate:
        """
        设置默认模板
        
        Args:
            template_id: 模板ID
            tenant_id: 租户ID
            
        Returns:
            PrintTemplate: 更新后的模板对象
            
        Raises:
            NotFoundException: 模板不存在
        """
        template = self.template_repo.set_default_template(template_id, tenant_id)
        logger.info(f"设置默认模板: {template.id} ({template.name})")
        return template
    
    def render_template(
        self,
        template_id: str,
        data: Dict[str, Any],
        tenant_id: str
    ) -> str:
        """
        渲染打印模板为HTML
        
        Args:
            template_id: 模板ID
            data: 要填充的数据
            tenant_id: 租户ID
            
        Returns:
            str: 渲染后的HTML字符串
            
        Raises:
            NotFoundException: 模板不存在
            BusinessException: 渲染失败
        """
        template = self.get_template(template_id, tenant_id)
        config = template.template_config
        
        try:
            html = self._render_template_config(config, data)
            return html
        except Exception as e:
            logger.error(f"渲染模板失败: {str(e)}", exc_info=True)
            raise BusinessException(f"渲染模板失败: {str(e)}")
    
    def _validate_template_data(self, template_data: Dict[str, Any]) -> None:
        """
        验证模板数据
        
        Args:
            template_data: 模板数据
            
        Raises:
            BusinessException: 验证失败
        """
        # 验证必需字段
        if "name" not in template_data or not template_data["name"]:
            raise BusinessException("模板名称不能为空")
        
        if len(template_data["name"]) > 100:
            raise BusinessException("模板名称长度不能超过100个字符")
        
        if "type" not in template_data or not template_data["type"]:
            raise BusinessException("模板类型不能为空")
        
        valid_types = ["bill", "prescription", "medical_record", "purchase_return"]
        if template_data["type"] not in valid_types:
            raise BusinessException(f"模板类型必须是: {', '.join(valid_types)}")
        
        if "template_config" not in template_data:
            raise BusinessException("模板配置不能为空")
        
        # 验证模板配置
        self._validate_template_config(template_data["template_config"])
    
    def _validate_template_config(self, config: Dict[str, Any]) -> None:
        """
        验证模板配置JSON结构
        
        Args:
            config: 模板配置字典
            
        Raises:
            BusinessException: 验证失败
        """
        if not isinstance(config, dict):
            raise BusinessException("模板配置必须是JSON对象")
        
        # 验证版本
        if "version" not in config:
            raise BusinessException("模板配置缺少version字段")
        
        # 验证页面设置
        if "page" not in config:
            raise BusinessException("模板配置缺少page字段")
        
        # 验证区域
        if "sections" not in config:
            raise BusinessException("模板配置缺少sections字段")
        
        if not isinstance(config["sections"], list):
            raise BusinessException("sections必须是数组")
    
    def _render_template_config(self, config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        渲染模板配置为HTML
        
        Args:
            config: 模板配置
            data: 数据
            
        Returns:
            str: HTML字符串
        """
        # 获取页面设置
        page = config.get("page", {})
        width = page.get("width", 210)
        height = page.get("height", 297)
        unit = page.get("unit", "mm")
        margin = page.get("margin", {})
        
        # 开始构建HTML
        html_parts = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>打印</title>',
            '<style>',
            '@media print {',
            f'  @page {{ size: {width}{unit} {height}{unit}; margin: {margin.get("top", 10)}{unit} {margin.get("right", 10)}{unit} {margin.get("bottom", 10)}{unit} {margin.get("left", 10)}{unit}; }}',
            '}',
            '.print-template {',
            f'  width: {width}{unit};',
            f'  min-height: {height}{unit};',
            '  margin: 0 auto;',
            '  padding: 0;',
            '}',
            '.section {',
            '  position: relative;',
            '  margin-bottom: 10px;',
            '}',
            '.field {',
            '  margin: 5px 0;',
            '}',
            '.field-label {',
            '  font-weight: bold;',
            '  margin-right: 5px;',
            '}',
            'table {',
            '  width: 100%;',
            '  border-collapse: collapse;',
            '  margin: 10px 0;',
            '}',
            'table th, table td {',
            '  border: 1px solid #000;',
            '  padding: 5px;',
            '  text-align: left;',
            '}',
            '</style>',
            '</head>',
            '<body>',
            '<div class="print-template">'
        ]
        
        # 渲染各个区域
        sections = config.get("sections", [])
        for section in sections:
            section_id = section.get("id", "")
            section_name = section.get("name", "")
            fields = section.get("fields", [])
            
            html_parts.append(f'<div class="section section-{section_id}">')
            
            # 渲染字段
            for field in fields:
                field_html = self._render_field(field, data)
                html_parts.append(field_html)
            
            html_parts.append('</div>')
        
        # 结束HTML
        html_parts.extend([
            '</div>',
            '</body>',
            '</html>'
        ])
        
        return '\n'.join(html_parts)
    
    def _render_field(self, field: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        渲染单个字段
        
        Args:
            field: 字段配置
            data: 数据
            
        Returns:
            str: HTML字符串
        """
        field_type = field.get("type", "text")
        field_name = field.get("name", "")
        field_label = field.get("label", "")
        field_value = field.get("value", "")
        style = field.get("style", {})
        
        # 构建样式字符串
        style_str = self._build_style_string(style)
        
        if field_type == "text":
            # 静态文本
            return f'<div class="field" style="{style_str}">{field_value}</div>'
        
        elif field_type == "data":
            # 动态数据字段
            value = data.get(field_name, "")
            if field_label:
                return f'<div class="field" style="{style_str}"><span class="field-label">{field_label}:</span>{value}</div>'
            else:
                return f'<div class="field" style="{style_str}">{value}</div>'
        
        elif field_type == "table":
            # 表格数据
            table_data = data.get(field_name, [])
            if not isinstance(table_data, list):
                table_data = []
            
            html = f'<table style="{style_str}">'
            
            # 表头
            columns = field.get("columns", [])
            if columns:
                html += '<thead><tr>'
                for col in columns:
                    html += f'<th>{col.get("label", "")}</th>'
                html += '</tr></thead>'
            
            # 表体
            html += '<tbody>'
            for row in table_data:
                html += '<tr>'
                for col in columns:
                    col_name = col.get("name", "")
                    value = row.get(col_name, "")
                    html += f'<td>{value}</td>'
                html += '</tr>'
            html += '</tbody></table>'
            
            return html
        
        elif field_type == "image":
            # 图片
            image_url = field_value or data.get(field_name, "")
            return f'<img src="{image_url}" style="{style_str}" />'
        
        elif field_type == "line":
            # 分隔线
            return f'<hr style="{style_str}" />'
        
        else:
            # 未知类型，返回空
            return ""
    
    def _build_style_string(self, style: Dict[str, Any]) -> str:
        """
        构建CSS样式字符串
        
        Args:
            style: 样式字典
            
        Returns:
            str: CSS样式字符串
        """
        if not style:
            return ""
        
        style_parts = []
        
        # 字体大小
        if "fontSize" in style:
            style_parts.append(f"font-size: {style['fontSize']}px;")
        
        # 字体粗细
        if "fontWeight" in style:
            style_parts.append(f"font-weight: {style['fontWeight']};")
        
        # 文本对齐
        if "textAlign" in style:
            style_parts.append(f"text-align: {style['textAlign']};")
        
        # 颜色
        if "color" in style:
            style_parts.append(f"color: {style['color']};")
        
        # 位置（如果需要）
        if "position" in style:
            pos = style["position"]
            if "x" in pos:
                style_parts.append(f"left: {pos['x']}px;")
            if "y" in pos:
                style_parts.append(f"top: {pos['y']}px;")
        
        return " ".join(style_parts)

