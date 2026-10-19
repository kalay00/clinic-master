"""
控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）
"""
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, Query, Body

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from .model import Notification
from .schema import NotificationSchema, NotificationCreateSchema, NotificationUpdateSchema
from .param import NotificationQueryParam
from .service import NotificationService


router = APIRouter()


@router.get("", summary="获取通知列表", dependencies=[Depends(AuthPermission(permission=["notification:list"]))])
async def list_(
    auth: AuthSchema = Depends(get_current_user),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    order_by: Optional[str] = Query(None, description="排序")):
    params = NotificationQueryParam(page_no=page, page_size=page_size, order_by=order_by)
    data = await NotificationService(auth).list(params.page_no, params.page_size, params.order_by, {})
    return SuccessResponse(data=data, msg="查询成功")


@router.post("", summary="创建通知", dependencies=[Depends(AuthPermission(permission=["notification:create"]))])
async def create_(data: NotificationCreateSchema, auth: AuthSchema = Depends(get_current_user)):
    result = await NotificationService(auth).create(data)
    return SuccessResponse(data=result, msg="创建成功")


@router.get("/{id}", summary="获取通知详情", dependencies=[Depends(AuthPermission(permission=["notification:get"]))])
async def get_(id: str, auth: AuthSchema = Depends(get_current_user)):
    result = await NotificationService(auth).get(id)
    return SuccessResponse(data=result, msg="查询成功")


@router.put("/{id}", summary="更新通知", dependencies=[Depends(AuthPermission(permission=["notification:update"]))])
async def update_(id: str, data: NotificationUpdateSchema, auth: AuthSchema = Depends(get_current_user)):
    result = await NotificationService(auth).update(id, data)
    return SuccessResponse(data=result, msg="更新成功")


@router.delete("/{id}", summary="删除通知", dependencies=[Depends(AuthPermission(permission=["notification:delete"]))])
async def delete_(id: str, auth: AuthSchema = Depends(get_current_user)):
    await NotificationService(auth).delete(id)
    return SuccessResponse(msg="删除成功")


@router.post("/send-sms", summary="发送短信通知")
async def send_sms(
    phone: str = Body(..., embed=True, description="手机号"),
    message: str = Body(..., embed=True, description="消息内容"),
    tenant_id: Optional[str] = Body(None, embed=True, description="租户ID"),
    auth: AuthSchema = Depends(get_current_user)):
    result = await NotificationService(auth).send_sms(phone, message, tenant_id)
    return SuccessResponse(data={"ok": result}, msg="发送成功" if result else "发送失败")


@router.post("/send-wechat", summary="发送微信通知")
async def send_wechat(
    openid: str = Body(..., embed=True, description="微信OpenID"),
    template_id: str = Body(..., embed=True, description="模板ID"),
    data: Dict[str, Any] = Body(..., embed=True, description="模板数据"),
    tenant_id: Optional[str] = Body(None, embed=True, description="租户ID"),
    auth: AuthSchema = Depends(get_current_user)):
    result = await NotificationService(auth).send_wechat(openid, template_id, data, tenant_id)
    return SuccessResponse(data={"ok": result}, msg="发送成功" if result else "发送失败")


@router.post("/send-appointment-reminder", summary="发送预约提醒")
async def send_appointment_reminder(
    patient_id: str = Body(..., embed=True, description="患者ID"),
    appointment_time: str = Body(..., embed=True, description="预约时间"),
    phone: Optional[str] = Body(None, embed=True, description="手机号"),
    openid: Optional[str] = Body(None, embed=True, description="OpenID"),
    tenant_id: Optional[str] = Body(None, embed=True, description="租户ID"),
    auth: AuthSchema = Depends(get_current_user)):
    result = await NotificationService(auth).send_appointment_reminder(patient_id, appointment_time, phone, openid, tenant_id)
    return SuccessResponse(data={"ok": result}, msg="发送成功" if result else "发送失败")


@router.post("/send-payment-notification", summary="发送支付通知")
async def send_payment_notification(
    patient_id: str = Body(..., embed=True, description="患者ID"),
    amount: float = Body(..., embed=True, description="金额"),
    phone: Optional[str] = Body(None, embed=True, description="手机号"),
    openid: Optional[str] = Body(None, embed=True, description="OpenID"),
    tenant_id: Optional[str] = Body(None, embed=True, description="租户ID"),
    auth: AuthSchema = Depends(get_current_user)):
    result = await NotificationService(auth).send_payment_notification(patient_id, amount, phone, openid, tenant_id)
    return SuccessResponse(data={"ok": result}, msg="发送成功" if result else "发送失败")
