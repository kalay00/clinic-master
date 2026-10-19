"""
药品分类 路由
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from uuid import UUID
from app.core.dependencies import AuthPermission, get_current_user
from app.core.base_schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.base_crud import CRUDBase
from .model import DrugCategory
from .schema import DrugCategorySchema, DrugCategoryCreateSchema, DrugCategoryUpdateSchema

category_router = APIRouter(tags=["药品分类"])


@category_router.get("", summary="药品分类列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["drug:list"]))])
async def list_categories(auth: AuthSchema = Depends(get_current_user), page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=200), keyword: Optional[str] = Query(None), status: Optional[str] = Query(None), category_type: Optional[str] = Query(None)):
    search = {}
    if keyword:
        search["name"] = ("like", keyword)
    if status:
        search["status"] = status
    if category_type and category_type != "all":
        search["category_type"] = category_type
    result = await CRUDBase(DrugCategory, auth, auth.db).page(
        offset=(page - 1) * page_size, limit=page_size,
        order_by=[{"sort": "asc"}, {"created_at": "desc"}], search=search,
        out_schema=DrugCategorySchema,
    )
    return SuccessResponse(data=result)


@category_router.post("", summary="新增药品分类", response_model=None, dependencies=[Depends(AuthPermission(permission=["drug:create"]))])
async def create_category(data: DrugCategoryCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    obj = await CRUDBase(DrugCategory, auth, auth.db).create(data.model_dump())
    return DrugCategorySchema.model_validate(obj).model_dump()


@category_router.put("/{cid}", summary="编辑药品分类", response_model=None, dependencies=[Depends(AuthPermission(permission=["drug:update"]))])
async def update_category(cid: UUID, data: DrugCategoryUpdateSchema, auth: AuthSchema = Depends(get_current_user)):
    obj = await CRUDBase(DrugCategory, auth, auth.db).update(cid, data.model_dump(exclude_unset=True))
    return DrugCategorySchema.model_validate(obj).model_dump()


@category_router.delete("", summary="删除药品分类", response_model=None, dependencies=[Depends(AuthPermission(permission=["drug:delete"]))])
async def delete_category(ids: List[UUID], auth: AuthSchema = Depends(get_current_user)):
    await CRUDBase(DrugCategory, auth, auth.db).delete(ids)
    return SuccessResponse(message="删除成功")
