"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import Bill
from .schema import (
    BillSchema,
    BillCreateSchema,
    BillUpdateSchema,
    BillPayRequest,
    BillRefundRequest,
)
from .param import PaymentQueryParam
from .service import PaymentService


router = APIRouter()


@router.get("", summary="获取收费列表", dependencies=[Depends(AuthPermission(permission=["payment:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序"),
    patient_id: Optional[str] = Query(None, description="患者ID"),
    status: Optional[str] = Query(None, description="状态"),
    bill_type: Optional[str] = Query(None, description="账单类型"),
):
    params = PaymentQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    filters = {}
    if patient_id:
        filters["patient_id"] = patient_id
    if status:
        filters["status"] = status
    if bill_type:
        filters["bill_type"] = bill_type
    data = await PaymentService(auth).list(params.page_no, params.page_size, params.order_by, filters)
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建收费", dependencies=[Depends(AuthPermission(permission=["payment:create"]))])
async def create_(
    data: BillCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await PaymentService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取收费详情", dependencies=[Depends(AuthPermission(permission=["payment:get"]))])
async def get_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await PaymentService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新收费", dependencies=[Depends(AuthPermission(permission=["payment:update"]))])
async def update_(
    id: str,
    data: BillUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await PaymentService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除收费", dependencies=[Depends(AuthPermission(permission=["payment:delete"]))])
async def delete_(
    id: str,
    auth: AuthSchema = Depends(get_current_user),
):
    await PaymentService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


@router.post("/{id}/pay", summary="支付账单", dependencies=[Depends(AuthPermission(permission=["payment:update"]))])
async def pay_(
    id: str,
    data: BillPayRequest,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await PaymentService(auth).pay_bill(
        bill_id=id,
        payment_method=data.payment_method,
        amount=data.amount,
        transaction_id=data.transaction_id,
        use_balance=data.use_balance,
        use_points=data.use_points,
    )
    return SuccessResponse(data=result, msg="支付成功")


@router.post("/{id}/refund", summary="退费", dependencies=[Depends(AuthPermission(permission=["payment:update"]))])
async def refund_(
    id: str,
    data: BillRefundRequest,
    auth: AuthSchema = Depends(get_current_user),
):
    result = await PaymentService(auth).refund_bill(
        bill_id=id,
        refund_amount=data.refund_amount,
        reason=data.reason,
    )
    return SuccessResponse(data=result, msg="退费成功")


# 支付记录（Payment）单独资源：挂在 /payments/payments
payments_router = APIRouter()


@payments_router.get("", summary="获取支付记录列表", dependencies=[Depends(AuthPermission(permission=["payment:list"]))])
async def list_payments_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    bill_id: Optional[str] = Query(None, description="账单ID"),
    patient_id: Optional[str] = Query(None, description="患者ID"),
    status: Optional[str] = Query(None, description="状态"),
):
    rows, total = await PaymentService(auth).list_payments(
        bill_id=bill_id,
        patient_id=patient_id,
        status=status,
        skip=(page - 1) * page_size,
        limit=page_size,
    )
    return SuccessResponse(
        data={"items": rows, "total": total, "page": page, "page_size": page_size},
        msg="查询成功",
    )
