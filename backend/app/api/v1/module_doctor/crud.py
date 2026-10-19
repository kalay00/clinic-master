"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Doctor
from app.api.v1.module_department.model import Department
from .schema import DepartmentSchema, DepartmentCreateSchema, DepartmentUpdateSchema, DoctorSchema, DoctorCreateSchema, DoctorUpdateSchema



class DepartmentCRUD(CRUDBase[Department, DepartmentCreateSchema, DepartmentUpdateSchema]):
    """Department 数据层"""

    pass


class DoctorCRUD(CRUDBase[Doctor, DoctorCreateSchema, DoctorUpdateSchema]):
    """Doctor 数据层"""

    pass

