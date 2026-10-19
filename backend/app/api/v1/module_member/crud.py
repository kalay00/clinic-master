"""
会员模块 CRUD
"""
from app.core.base_crud import CRUDBase
from .model import MemberLevel


class MemberLevelCRUD(CRUDBase):
    """会员等级数据层"""

    def __init__(self, auth=None, session=None):
        super().__init__(MemberLevel, auth, session)
