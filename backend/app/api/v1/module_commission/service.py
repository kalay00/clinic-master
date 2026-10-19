"""
提成方案模块 Service
"""
from typing import Optional
from app.core.base_crud import CRUDBase
from app.core.base_schema import AuthSchema
from .model import CommissionPlan
from .schema import CommissionPlanSchema, CommissionPlanCreateSchema, CommissionPlanUpdateSchema


class CommissionPlanService:
    def __init__(self, auth: AuthSchema):
        self.auth = auth
        self.crud = CRUDBase(CommissionPlan, auth, auth.db)

    async def list_plans(self, page: int, page_size: int, keyword: Optional[str] = None, status: Optional[str] = None):
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
            out_schema=CommissionPlanSchema,
        )

    async def create(self, data: CommissionPlanCreateSchema):
        obj = await self.crud.create(data.model_dump())
        return CommissionPlanSchema.model_validate(obj).model_dump()

    async def update(self, plan_id, data: CommissionPlanUpdateSchema):
        obj = await self.crud.update(plan_id, data.model_dump(exclude_unset=True))
        return CommissionPlanSchema.model_validate(obj).model_dump()

    async def delete(self, plan_ids: list):
        await self.crud.delete(plan_ids)
        return True

    @staticmethod
    def calc_commission(plan, base_amount: float) -> float:
        """根据方案计算提成金额"""
        if not plan or plan.status != "active":
            return 0
        if base_amount < (plan.min_amount or 0):
            return 0
        if plan.type == "fixed":
            return float(plan.fixed_amount or 0)
        if plan.type == "percentage":
            return round(base_amount * float(plan.percentage_rate or 0), 2)
        return 0
