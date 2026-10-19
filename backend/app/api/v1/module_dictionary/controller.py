"""
通用字典 路由
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from uuid import UUID

from app.core.dependencies import AuthPermission, get_current_user
from app.core.base_schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.base_crud import CRUDBase
from .model import Dictionary
from .schema import DictionarySchema, DictionaryCreateSchema, DictionaryUpdateSchema

router = APIRouter(tags=["通用字典"])


@router.get("", summary="字典列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["dictionary:list"]))])
async def list_dictionaries(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
    category: Optional[str] = Query(None, description="一级分类 key"),
    sub_type: Optional[str] = Query(None, description="二级子类型 key"),
    keyword: Optional[str] = Query(None, description="内容关键字"),
    status: Optional[str] = Query(None),
):
    search = {}
    if category:
        search["category"] = category
    if sub_type:
        search["sub_type"] = sub_type
    if keyword:
        search["content"] = ("like", keyword)
    if status:
        search["status"] = status
    result = await CRUDBase(Dictionary, auth, auth.db).page(
        offset=(page - 1) * page_size,
        limit=page_size,
        order_by=[{"sort": "asc"}, {"created_at": "desc"}],
        search=search,
        out_schema=DictionarySchema,
    )
    return SuccessResponse(data=result)


@router.post("", summary="新增字典项", response_model=None, dependencies=[Depends(AuthPermission(permission=["dictionary:create"]))])
async def create_dictionary(data: DictionaryCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    obj = await CRUDBase(Dictionary, auth, auth.db).create(data.model_dump())
    return SuccessResponse(data=DictionarySchema.model_validate(obj).model_dump())


@router.get("/{did}", summary="字典详情", response_model=None, dependencies=[Depends(AuthPermission(permission=["dictionary:get"]))])
async def get_dictionary(did: UUID, auth: AuthSchema = Depends(get_current_user)):
    obj = await CRUDBase(Dictionary, auth, auth.db).get_or_404(id=did, out_schema=DictionarySchema)
    return SuccessResponse(data=obj.model_dump())


@router.put("/{did}", summary="编辑字典项", response_model=None, dependencies=[Depends(AuthPermission(permission=["dictionary:update"]))])
async def update_dictionary(did: UUID, data: DictionaryUpdateSchema, auth: AuthSchema = Depends(get_current_user)):
    obj = await CRUDBase(Dictionary, auth, auth.db).update(did, data.model_dump(exclude_unset=True))
    return SuccessResponse(data=DictionarySchema.model_validate(obj).model_dump())


@router.delete("/{did}", summary="删除字典项", response_model=None, dependencies=[Depends(AuthPermission(permission=["dictionary:delete"]))])
async def delete_dictionary(did: UUID, auth: AuthSchema = Depends(get_current_user)):
    await CRUDBase(Dictionary, auth, auth.db).delete([did])
    return SuccessResponse(message="删除成功")
