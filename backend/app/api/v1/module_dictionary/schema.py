"""
通用字典 Pydantic 模型
"""
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.core.base_schema import BaseSchema


class DictionarySchema(BaseSchema):
    """Dictionary Schema"""

    model_config = ConfigDict(from_attributes=True)

    category: str = Field(..., comment="一级分类 key")
    sub_type: str = Field(..., comment="二级子类型 key")
    content: str = Field(..., comment="字典内容")
    code: Optional[str] = Field(default=None, comment="编码")
    sort: int = Field(0, comment="排序")
    status: Optional[str] = Field(default=None, comment="状态 active/inactive")
    remark: Optional[str] = Field(default=None, comment="备注")

    @computed_field
    @property
    def creator(self) -> Optional[str]:
        user = getattr(self, "created_by_user", None)
        if user is not None:
            return getattr(user, "real_name", None) or getattr(user, "username", None)
        return None


class DictionaryCreateSchema(BaseModel):
    """Dictionary CreateSchema"""

    model_config = ConfigDict(from_attributes=True)

    category: str = Field(..., comment="一级分类 key")
    sub_type: str = Field(..., comment="二级子类型 key")
    content: str = Field(..., comment="字典内容")
    code: Optional[str] = Field(default=None, comment="编码")
    sort: int = Field(0, comment="排序")
    status: str = Field("active", comment="状态")
    remark: Optional[str] = Field(default=None, comment="备注")


class DictionaryUpdateSchema(BaseModel):
    """Dictionary UpdateSchema"""

    model_config = ConfigDict(from_attributes=True)

    category: Optional[str] = Field(default=None, comment="一级分类 key")
    sub_type: Optional[str] = Field(default=None, comment="二级子类型 key")
    content: Optional[str] = Field(default=None, comment="字典内容")
    code: Optional[str] = Field(default=None, comment="编码")
    sort: Optional[int] = Field(default=None, comment="排序")
    status: Optional[str] = Field(default=None, comment="状态")
    remark: Optional[str] = Field(default=None, comment="备注")
