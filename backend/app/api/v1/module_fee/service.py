"""
服务层（对齐 FastapiAdmin: service.py，Python 3.12+）
"""
from __future__ import annotations
from typing import Optional

from app.core.base_schema import AuthSchema
from .model import Fee
from .schema import FeeSchema, FeeCreateSchema, FeeUpdateSchema
from .crud import FeeCRUD


class FeeService:
    """Fee 服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = FeeCRUD(Fee, auth=auth)

    async def get(self, id: str) -> FeeSchema:
        return await self.crud.get_or_404(id=id, out_schema=FeeSchema)

    async def list(self, page_no: int, page_size: int, order_by, search: Optional[dict]):
        search = search or {}
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{'sort': 'asc'}, {'created_at': 'desc'}],
            search=search,
            out_schema=FeeSchema,
        )

    async def create(self, data: FeeCreateSchema) -> FeeSchema:
        obj = await self.crud.create(data)
        return FeeSchema.model_validate(obj)

    async def update(self, id: str, data: FeeUpdateSchema) -> FeeSchema:
        obj = await self.crud.update(id, data)
        return FeeSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])
