"""
提成方案模块 CRUD
"""
from app.core.base_crud import CRUDBase
from .model import CommissionPlan


class CommissionPlanCRUD(CRUDBase):
    def __init__(self, auth=None, session=None):
        super().__init__(CommissionPlan, auth, session)
