"""
数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）
"""
from app.core.base_crud import CRUDBase
from .model import Notification
from .schema import NotificationSchema, NotificationCreateSchema, NotificationUpdateSchema



class NotificationCRUD(CRUDBase[Notification, NotificationCreateSchema, NotificationUpdateSchema]):
    """Notification 数据层"""

    pass

