"""
技师模块 Service
"""
from typing import Optional
from app.core.base_crud import CRUDBase
from app.core.base_schema import AuthSchema
from .model import Technician
from .schema import TechnicianSchema, TechnicianCreateSchema, TechnicianUpdateSchema


class TechnicianService:
    def __init__(self, auth: AuthSchema):
        self.auth = auth
        self.crud = CRUDBase(Technician, auth, auth.db)

    async def list_technicians(self, page: int, page_size: int, keyword: Optional[str] = None, status: Optional[str] = None):
        search = {}
        if keyword:
            search["name"] = ("like", keyword)
        if status:
            search["status"] = status
        return await self.crud.page(
            offset=(page - 1) * page_size,
            limit=page_size,
            order_by=[{"created_at": "desc"}],
            search=search,
            out_schema=TechnicianSchema,
        )

    async def create(self, data: TechnicianCreateSchema):
        obj = await self.crud.create(data.model_dump())
        return TechnicianSchema.model_validate(obj).model_dump()

    async def update(self, tech_id, data: TechnicianUpdateSchema):
        obj = await self.crud.update(tech_id, data.model_dump(exclude_unset=True))
        return TechnicianSchema.model_validate(obj).model_dump()

    async def delete(self, tech_ids: list):
        await self.crud.delete(tech_ids)
        return True
