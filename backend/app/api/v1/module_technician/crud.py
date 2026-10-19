"""
技师模块 CRUD
"""
from app.core.base_crud import CRUDBase
from .model import Technician


class TechnicianCRUD(CRUDBase):
    def __init__(self, auth=None, session=None):
        super().__init__(Technician, auth, session)
