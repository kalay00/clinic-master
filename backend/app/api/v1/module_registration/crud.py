"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Schedule, Registration
from .schema import ScheduleSchema, ScheduleCreateSchema, ScheduleUpdateSchema, RegistrationSchema, RegistrationCreateSchema, RegistrationUpdateSchema



class ScheduleCRUD(CRUDBase[Schedule, ScheduleCreateSchema, ScheduleUpdateSchema]):
    """Schedule 数据层"""

    pass


class RegistrationCRUD(CRUDBase[Registration, RegistrationCreateSchema, RegistrationUpdateSchema]):
    """Registration 数据层"""

    pass

