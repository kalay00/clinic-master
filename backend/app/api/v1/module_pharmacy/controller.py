"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import Drug
from .schema import DrugSchema, DrugCreateSchema, DrugUpdateSchema, DispenseRequestSchema, PriceAdjustmentSchema, PriceAdjustmentCreateSchema
from .service import PharmacyService


router = APIRouter()


@router.post("/dispense", summary="处方发药", dependencies=[Depends(AuthPermission(permission=["pharmacy:dispense"]))])
async def dispense_prescription_(
    data: DispenseRequestSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    """按处方发药：扣减库存、生成发药记录、更新处方状态为已发药。

    注意：该路由必须注册在 "/{id}" 之前，否则 POST /pharmacy/dispense 会被
    "/{id}" 误匹配为 id="dispense"（该路由仅支持 GET/PUT/DELETE）→ 返回 405。
    """
    items = [it.model_dump() for it in data.items]
    result = await PharmacyService(auth).dispense_prescription(
        prescription_id=data.prescription_id,
        dispense_items=items,
        operator_id=auth.user_id if hasattr(auth, "user_id") else None,
    )
    return SuccessResponse(data=result, msg="发药成功")


@router.get("/dispenses", summary="发药记录列表（按处方）", dependencies=[Depends(AuthPermission(permission=["pharmacy:list"]))])
async def list_dispenses_(
    auth: AuthSchema = Depends(get_current_user),
    prescription_id: Optional[str] = Query(None, description="处方ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=200),
):
    """发药记录列表：可按处方ID过滤，供发药详情页展示发药明细。"""
    items, total = await PharmacyService(auth).list_dispenses(
        prescription_id=prescription_id,
        skip=(page - 1) * page_size,
        limit=page_size,
    )
    return SuccessResponse(
        data={"items": [it.model_dump() for it in items], "total": total, "page": page, "page_size": page_size},
        msg="查询成功",
    )


@router.get("", summary="获取药房列表", dependencies=[Depends(AuthPermission(permission=["pharmacy:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="关键词（药品名/编码）"),
    category: Optional[str] = Query(None, description="药品分类（分类ID 或旧的分类名）"),
    status: Optional[str] = Query(None, description="状态：active/inactive"),
):
    """药品列表：关联供应商表返回 supplier_name。

    注意：使用 list_drugs（带供应商名称）而非通用 list（仅 DrugSchema，无供应商名称）。
    """
    items, total = await PharmacyService(auth).list_drugs(
        search=search,
        category=category,
        status=status,
        skip=(page - 1) * page_size,
        limit=page_size,
    )
    return SuccessResponse(data={"items": items, "total": total, "page": page, "page_size": page_size}, msg="查询成功")


@router.post("", summary="创建药房", dependencies=[Depends(AuthPermission(permission=["pharmacy:create"]))])
async def create_(
    data: DrugCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await PharmacyService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/low-stock", summary="库存预警", dependencies=[Depends(AuthPermission(permission=["pharmacy:list"]))])
async def low_stock_(
    auth: AuthSchema = Depends(get_current_user),
):
    """库存预警：低库存 / 过期 / 即将过期。

    注意：该路由必须注册在 "/{id}" 之前，否则 GET /pharmacy/drugs/low-stock 会被
    "/{id}" 误匹配为 id="low-stock"（UUID 校验失败 → 500）。
    """
    result = await PharmacyService(auth).get_inventory_warnings()
    return SuccessResponse(data=result, msg="查询成功")


@router.get("/inventory", summary="库存管理列表", dependencies=[Depends(AuthPermission(permission=["pharmacy:list"]))])
async def inventory_list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词（药品名/编码）"),
    category: Optional[str] = Query(None, description="药品分类"),
):
    """库存管理列表：关联药品表，返回药品信息 + 库存数量/批次/有效期等。

    注意：该路由必须注册在 "/{id}" 之前，否则 GET /pharmacy/drugs/inventory 会被
    "/{id}" 误匹配为 id="inventory"。
    """
    result = await PharmacyService(auth).list_inventory(
        page_no=page, page_size=page_size, keyword=keyword, category=category
    )
    return SuccessResponse(data=result, msg="查询成功")


@router.get("/{id}", summary="获取药房详情", dependencies=[Depends(AuthPermission(permission=["pharmacy:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await PharmacyService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新药房", dependencies=[Depends(AuthPermission(permission=["pharmacy:update"]))])
async def update_(
    id: str,
    data: DrugUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await PharmacyService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除药房", dependencies=[Depends(AuthPermission(permission=["pharmacy:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await PharmacyService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


# ─────────────────────────────────────────────────────────────────────────────
# 药品调价（独立路由，完整路径 /pharmacy/price-adjustments）
# ─────────────────────────────────────────────────────────────────────────────
price_router = APIRouter()


@price_router.get("", summary="获取调价单列表", dependencies=[Depends(AuthPermission(permission=["pharmacy:list"]))])
async def list_price_adjustments_(
    auth: AuthSchema = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(10, ge=1, le=200, description="每页数量"),
    status: Optional[str] = Query(None, description="状态"),
):
    result = await PharmacyService(auth).list_price_adjustments(skip=skip, limit=limit, status=status)
    return SuccessResponse(data=result, msg="查询成功")


@price_router.get("/{id}", summary="获取调价单详情", dependencies=[Depends(AuthPermission(permission=["pharmacy:get"]))])
async def get_price_adjustment_(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await PharmacyService(auth).get_price_adjustment(id)
    return SuccessResponse(data=result.model_dump(), msg="查询成功")


@price_router.post("", summary="创建调价单", dependencies=[Depends(AuthPermission(permission=["pharmacy:create"]))])
async def create_price_adjustment_(data: PriceAdjustmentCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    result = await PharmacyService(auth).create_price_adjustment(data.model_dump())
    return SuccessResponse(data=result.model_dump(), msg="创建成功")


@price_router.post("/{id}/approve", summary="审批调价单（更新药品售价）", dependencies=[Depends(AuthPermission(permission=["pharmacy:update"]))])
async def approve_price_adjustment_(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await PharmacyService(auth).approve_price_adjustment(id)
    return SuccessResponse(data=result.model_dump(), msg="审批成功")


@price_router.delete("/{id}", summary="删除调价单", dependencies=[Depends(AuthPermission(permission=["pharmacy:delete"]))])
async def delete_price_adjustment_(id: str, auth: AuthSchema = Depends(get_current_user)):
    await PharmacyService(auth).delete_price_adjustment(id)
    return SuccessResponse(msg="删除成功")
