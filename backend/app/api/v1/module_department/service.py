"""
服务层（对齐 FastapiAdmin: service.py，Python 3.12+）
"""
from __future__ import annotations
from app.core.base_schema import AuthSchema
from .model import Department
from .schema import DepartmentSchema, DepartmentCreateSchema, DepartmentUpdateSchema
from .crud import DepartmentCRUD


class DepartmentService:
    """Department 服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = DepartmentCRUD(Department, auth=auth)

    async def get(self, id: str) -> DepartmentSchema:
        return await self.crud.get_or_404(id=id, out_schema=DepartmentSchema)

    async def list(self, page_no: int, page_size: int, order_by, search: dict | None):
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{'created_at': 'desc'}],
            search=search or {},
            out_schema=DepartmentSchema,
        )

    async def create(self, data: DepartmentCreateSchema) -> DepartmentSchema:
        obj = await self.crud.create(data)
        return DepartmentSchema.model_validate(obj)

    async def update(self, id: str, data: DepartmentUpdateSchema) -> DepartmentSchema:
        obj = await self.crud.update(id, data)
        return DepartmentSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])
