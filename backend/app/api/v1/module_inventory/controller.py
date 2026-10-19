"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from datetime import datetime, date

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import Supplier
from .schema import SupplierSchema, SupplierCreateSchema, SupplierUpdateSchema
from .param import InventoryQueryParam
from .service import InventoryService


def _parse_date_param(value):
    """将 YYYY-MM-DD 字符串解析为 date，非法值返回 None。"""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


router = APIRouter()


@router.get("", summary="获取进销存列表", dependencies=[Depends(AuthPermission(permission=["inventory:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
):
    params = InventoryQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await InventoryService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建进销存", dependencies=[Depends(AuthPermission(permission=["inventory:create"]))])
async def create_(
    data: SupplierCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await InventoryService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取进销存详情", dependencies=[Depends(AuthPermission(permission=["inventory:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await InventoryService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新进销存", dependencies=[Depends(AuthPermission(permission=["inventory:update"]))])
async def update_(
    id: str,
    data: SupplierUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await InventoryService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除进销存", dependencies=[Depends(AuthPermission(permission=["inventory:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await InventoryService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


# ─────────────────────────────────────────────────────────────────────────────
# 采购单（独立路由，挂载前缀为 /inventory，故完整路径 /inventory/purchase-orders）
# ─────────────────────────────────────────────────────────────────────────────
purchase_router = APIRouter()


def _parse_date_param(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@purchase_router.get("/purchase-orders", summary="获取采购单列表", dependencies=[Depends(AuthPermission(permission=["inventory:list"]))])
async def list_purchase_orders_(
    auth: AuthSchema = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(10, ge=1, le=200, description="每页数量"),
    search: Optional[str] = Query(None, description="采购单号模糊搜索"),
    supplier_id: Optional[str] = Query(None, description="供应商ID"),
    status: Optional[str] = Query(None, description="状态"),
    start_date: Optional[str] = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
):
    rows, total = await InventoryService(auth).list_purchase_orders(
        skip=skip,
        limit=limit,
        search=search,
        supplier_id=supplier_id,
        status=status,
        start_date=_parse_date_param(start_date),
        end_date=_parse_date_param(end_date),
    )
    page = skip // limit + 1 if limit else 1
    data = {
        "items": rows,
        "pagination": {
            "page": page,
            "page_size": limit,
            "total": total,
            "pages": (total + limit - 1) // limit if limit else 1,
        },
    }
    return SuccessResponse(data=data, msg="查询成功")


@purchase_router.get("/purchase-orders/{id}", summary="获取采购单详情", dependencies=[Depends(AuthPermission(permission=["inventory:get"]))])
async def get_purchase_order_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await InventoryService(auth).get_purchase_order_detail(id)
    return SuccessResponse(data=result, msg="查询成功")


@purchase_router.post("/purchase-orders", summary="创建采购单", dependencies=[Depends(AuthPermission(permission=["inventory:create"]))])
async def create_purchase_order_(
    data: dict,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await InventoryService(auth).create_purchase_order(data)
    return SuccessResponse(data=result.model_dump(), msg="创建成功")


@purchase_router.put("/purchase-orders/{id}", summary="更新采购单", dependencies=[Depends(AuthPermission(permission=["inventory:update"]))])
async def update_purchase_order_(
    id: str,
    data: dict,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await InventoryService(auth).update_purchase_order(id, data)
    return SuccessResponse(data=result.model_dump(), msg="更新成功")


@purchase_router.post("/purchase-orders/{id}/approve", summary="审核采购单", dependencies=[Depends(AuthPermission(permission=["inventory:update"]))])
async def approve_purchase_order_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await InventoryService(auth).approve_purchase_order(id)
    return SuccessResponse(data=result.model_dump(), msg="审核成功")


@purchase_router.post("/purchase-orders/{id}/receive", summary="采购入库", dependencies=[Depends(AuthPermission(permission=["inventory:update"]))])
async def receive_purchase_order_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await InventoryService(auth).receive_purchase_order(id)
    return SuccessResponse(data=result.model_dump(), msg="入库成功")


@purchase_router.delete("/purchase-orders/{id}", summary="删除采购单", dependencies=[Depends(AuthPermission(permission=["inventory:delete"]))])
async def delete_purchase_order_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await InventoryService(auth).delete_purchase_order(id)
    return SuccessResponse(msg="删除成功")


# ─────────────────────────────────────────────────────────────────────────────
# 盘点单（独立路由，完整路径 /inventory/checks）
# ─────────────────────────────────────────────────────────────────────────────
check_router = APIRouter()


@check_router.get("/checks", summary="获取盘点单列表", dependencies=[Depends(AuthPermission(permission=["inventory:list"]))])
async def list_checks_(
    auth: AuthSchema = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(10, ge=1, le=200, description="每页数量"),
    status: Optional[str] = Query(None, description="状态"),
    start_date: Optional[str] = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
):
    rows, total = await InventoryService(auth).list_inventory_checks(
        skip=skip, limit=limit, status=status,
        start_date=_parse_date_param(start_date), end_date=_parse_date_param(end_date),
    )
    page = skip // limit + 1 if limit else 1
    return SuccessResponse(data={
        "items": [r.model_dump() for r in rows],
        "pagination": {"page": page, "page_size": limit, "total": total, "pages": (total + limit - 1) // limit if limit else 1},
    }, msg="查询成功")


@check_router.get("/checks/{id}", summary="获取盘点单详情", dependencies=[Depends(AuthPermission(permission=["inventory:get"]))])
async def get_check_(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await InventoryService(auth).get_inventory_check(id)
    return SuccessResponse(data=result.model_dump(), msg="查询成功")


@check_router.post("/checks", summary="创建盘点单", dependencies=[Depends(AuthPermission(permission=["inventory:create"]))])
async def create_check_(data: dict, auth: AuthSchema = Depends(get_current_user)):
    result = await InventoryService(auth).create_inventory_check(data)
    return SuccessResponse(data=result.model_dump(), msg="创建成功")


@check_router.post("/checks/{id}/complete", summary="完成盘点单", dependencies=[Depends(AuthPermission(permission=["inventory:update"]))])
async def complete_check_(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await InventoryService(auth).complete_inventory_check(id)
    return SuccessResponse(data=result.model_dump(), msg="盘点完成")


@check_router.delete("/checks/{id}", summary="删除盘点单", dependencies=[Depends(AuthPermission(permission=["inventory:delete"]))])
async def delete_check_(id: str, auth: AuthSchema = Depends(get_current_user)):
    await InventoryService(auth).delete_inventory_check(id)
    return SuccessResponse(msg="删除成功")


# ─────────────────────────────────────────────────────────────────────────────
# 退货单（独立路由，完整路径 /inventory/return-orders）
# ─────────────────────────────────────────────────────────────────────────────
return_router = APIRouter()


@return_router.get("/return-orders", summary="获取退货单列表", dependencies=[Depends(AuthPermission(permission=["inventory:list"]))])
async def list_return_orders_(
    auth: AuthSchema = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(10, ge=1, le=200, description="每页数量"),
    search: Optional[str] = Query(None, description="退货单号模糊搜索"),
    purchase_order_id: Optional[str] = Query(None, description="采购单ID"),
    status: Optional[str] = Query(None, description="状态"),
    start_date: Optional[str] = Query(None, description="起始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
):
    rows, total = await InventoryService(auth).list_return_orders(
        skip=skip, limit=limit, search=search, purchase_order_id=purchase_order_id, status=status,
        start_date=_parse_date_param(start_date), end_date=_parse_date_param(end_date),
    )
    page = skip // limit + 1 if limit else 1
    return SuccessResponse(data={
        "items": [r.model_dump() for r in rows],
        "pagination": {"page": page, "page_size": limit, "total": total, "pages": (total + limit - 1) // limit if limit else 1},
    }, msg="查询成功")


@return_router.get("/return-orders/{id}", summary="获取退货单详情", dependencies=[Depends(AuthPermission(permission=["inventory:get"]))])
async def get_return_order_(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await InventoryService(auth).get_return_order(id)
    return SuccessResponse(data=result.model_dump(), msg="查询成功")


@return_router.post("/return-orders", summary="创建退货单", dependencies=[Depends(AuthPermission(permission=["inventory:create"]))])
async def create_return_order_(data: dict, auth: AuthSchema = Depends(get_current_user)):
    result = await InventoryService(auth).create_return_order(data)
    return SuccessResponse(data=result.model_dump(), msg="创建成功")


@return_router.put("/return-orders/{id}", summary="更新退货单", dependencies=[Depends(AuthPermission(permission=["inventory:update"]))])
async def update_return_order_(id: str, data: dict, auth: AuthSchema = Depends(get_current_user)):
    result = await InventoryService(auth).update_return_order(id, data)
    return SuccessResponse(data=result.model_dump(), msg="更新成功")


@return_router.post("/return-orders/{id}/approve", summary="审核退货单", dependencies=[Depends(AuthPermission(permission=["inventory:update"]))])
async def approve_return_order_(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await InventoryService(auth).approve_return_order(id)
    return SuccessResponse(data=result.model_dump(), msg="审核成功")


@return_router.post("/return-orders/{id}/complete", summary="完成退货单", dependencies=[Depends(AuthPermission(permission=["inventory:update"]))])
async def complete_return_order_(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await InventoryService(auth).complete_return_order(id)
    return SuccessResponse(data=result.model_dump(), msg="退货完成")


@return_router.delete("/return-orders/{id}", summary="删除退货单", dependencies=[Depends(AuthPermission(permission=["inventory:delete"]))])
async def delete_return_order_(id: str, auth: AuthSchema = Depends(get_current_user)):
    await InventoryService(auth).delete_return_order(id)
    return SuccessResponse(msg="删除成功")
