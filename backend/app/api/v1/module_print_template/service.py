"""
服务层（对齐 FastapiAdmin: service.py，Python 3.12+）
"""
from __future__ import annotations
from app.core.base_schema import AuthSchema
from .model import PrintTemplate
from .schema import PrintTemplateSchema, PrintTemplateCreateSchema, PrintTemplateUpdateSchema
from .crud import PrintTemplateCRUD


class Print_templateService:
    """Print_template 服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = PrintTemplateCRUD(PrintTemplate, auth=auth)

    async def get(self, id: str) -> PrintTemplateSchema:
        return await self.crud.get_or_404(id=id, out_schema=PrintTemplateSchema)

    async def list(self, page_no: int, page_size: int, order_by, search: dict | None):
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{'created_at': 'desc'}],
            search=search or {},
            out_schema=PrintTemplateSchema,
        )

    async def create(self, data: PrintTemplateCreateSchema) -> PrintTemplateSchema:
        obj = await self.crud.create(data)
        return PrintTemplateSchema.model_validate(obj)

    async def update(self, id: str, data: PrintTemplateUpdateSchema) -> PrintTemplateSchema:
        obj = await self.crud.update(id, data)
        return PrintTemplateSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    async def set_default(self, id: str) -> PrintTemplateSchema:
        """将指定模板设为同类型下的默认模板（同类型其余模板取消默认）"""
        from sqlalchemy import select, update as sa_update

        current = await self.crud.get_or_404(id=id, out_schema=PrintTemplateSchema)
        db = self.auth.db

        stmt = (
            sa_update(PrintTemplate)
            .where(
                PrintTemplate.type == current.type,
                PrintTemplate.id != id,
                PrintTemplate.deleted_at.is_(None),
            )
            .values(is_default=False)
        )
        tenant_id = getattr(self.auth, "tenant_id", None)
        if tenant_id is not None:
            stmt = stmt.where(PrintTemplate.tenant_id == tenant_id)
        await db.execute(stmt)

        obj = await self.crud.update(id, PrintTemplateUpdateSchema(
            name=current.name,
            type=current.type,
            template_config=current.template_config,
            is_default=True,
        ))
        return PrintTemplateSchema.model_validate(obj)

    async def duplicate(self, id: str, new_name: str | None = None) -> PrintTemplateSchema:
        """复制模板"""
        current = await self.crud.get_or_404(id=id, out_schema=PrintTemplateSchema)
        obj = await self.crud.create(PrintTemplateCreateSchema(
            name=new_name or f"{current.name}-副本",
            type=current.type,
            template_config=current.template_config,
            is_default=False,
        ))
        return PrintTemplateSchema.model_validate(obj)
