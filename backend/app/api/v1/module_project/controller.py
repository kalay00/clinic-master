"""
项目模块 路由
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from uuid import UUID
from app.core.dependencies import AuthPermission, get_current_user
from app.core.base_schema import AuthSchema
from app.common.response import SuccessResponse
from .service import ProjectService
from .schema import (
    ProjectCategoryCreateSchema, ProjectCategoryUpdateSchema,
    ProjectCreateSchema, ProjectUpdateSchema,
    PurchaseCreateSchema, VerificationCreateSchema,
)

router = APIRouter(tags=["项目管理"])


# ---------- 分类 ----------
@router.get("/categories", summary="项目分类列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:list"]))])
async def list_categories(auth: AuthSchema = Depends(get_current_user), page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=200), keyword: Optional[str] = Query(None), status: Optional[str] = Query(None)):
    return SuccessResponse(data=await ProjectService(auth).list_categories(page, page_size, keyword, status))


@router.post("/categories", summary="新增项目分类", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:create"]))])
async def create_category(data: ProjectCategoryCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await ProjectService(auth).create_category(data))


@router.put("/categories/{cid}", summary="编辑项目分类", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:update"]))])
async def update_category(cid: UUID, data: ProjectCategoryUpdateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await ProjectService(auth).update_category(cid, data))


@router.delete("/categories", summary="删除项目分类", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:delete"]))])
async def delete_category(ids: List[UUID], auth: AuthSchema = Depends(get_current_user)):
    await ProjectService(auth).delete_category(ids)
    return SuccessResponse(message="删除成功")


# ---------- 项目 ----------
@router.get("", summary="项目列表", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:list"]))])
async def list_projects(auth: AuthSchema = Depends(get_current_user), page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100), keyword: Optional[str] = Query(None), category_id: Optional[UUID] = Query(None), status: Optional[str] = Query(None)):
    return SuccessResponse(data=await ProjectService(auth).list_projects(page, page_size, keyword, category_id, status))


@router.post("", summary="新增项目", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:create"]))])
async def create_project(data: ProjectCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await ProjectService(auth).create_project(data))


@router.put("/{project_id}", summary="编辑项目", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:update"]))])
async def update_project(project_id: UUID, data: ProjectUpdateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await ProjectService(auth).update_project(project_id, data))


@router.delete("", summary="删除项目", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:delete"]))])
async def delete_project(ids: List[UUID], auth: AuthSchema = Depends(get_current_user)):
    await ProjectService(auth).delete_project(ids)
    return SuccessResponse(message="删除成功")


# ---------- 购买 / 核销 ----------
@router.post("/purchase", summary="患者购买项目", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:create"]))])
async def purchase(data: PurchaseCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await ProjectService(auth).purchase(data))


@router.get("/my-services", summary="患者已购项目", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:list"]))])
async def my_services(patient_id: str = Query(..., description="患者ID"), auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await ProjectService(auth).my_services(patient_id))


@router.post("/verify", summary="项目服务核销", response_model=None, dependencies=[Depends(AuthPermission(permission=["project:update"]))])
async def verify(data: VerificationCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    return SuccessResponse(data=await ProjectService(auth).verify(data))
