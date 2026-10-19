"""
服务层（对齐 FastapiAdmin: service.py，Python 3.12+）
"""
from __future__ import annotations
from app.core.base_schema import AuthSchema
from .model import OperationLog
from .schema import OperationLogSchema, OperationLogCreateSchema, OperationLogUpdateSchema
from .crud import OperationLogCRUD


class LogService:
    """Log 服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = OperationLogCRUD(OperationLog, auth=auth)

    async def get(self, id: str) -> OperationLogSchema:
        return await self.crud.get_or_404(id=id, out_schema=OperationLogSchema)

    async def list(self, page_no: int, page_size: int, order_by, search: dict | None):
        return await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{'created_at': 'desc'}],
            search=search or {},
            out_schema=OperationLogSchema,
        )

    async def create(self, data: OperationLogCreateSchema) -> OperationLogSchema:
        obj = await self.crud.create(data)
        return OperationLogSchema.model_validate(obj)

    async def update(self, id: str, data: OperationLogUpdateSchema) -> OperationLogSchema:
        obj = await self.crud.update(id, data)
        return OperationLogSchema.model_validate(obj)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])
