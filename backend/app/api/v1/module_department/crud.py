"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Department
from app.api.v1.module_doctor.model import Doctor
from .schema import DepartmentSchema, DepartmentCreateSchema, DepartmentUpdateSchema, DoctorSchema, DoctorCreateSchema, DoctorUpdateSchema



class DepartmentCRUD(CRUDBase[Department, DepartmentCreateSchema, DepartmentUpdateSchema]):
    """Department 数据层"""

    pass


class DoctorCRUD(CRUDBase[Doctor, DoctorCreateSchema, DoctorUpdateSchema]):
    """Doctor 数据层"""

    pass

