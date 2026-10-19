"""
控制器（对接模块，已迁移业务逻辑至 service.py）
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user

from .service import IntegrationService


router = APIRouter()


@router.post("/wechat-pay", summary="微信支付")
async def wechat_pay(
    auth: AuthSchema = Depends(get_current_user),
    bill_id: str = Query(..., description="账单ID"),
    amount: float = Query(..., description="金额（元）"),
    openid: Optional[str] = Query(None, description="微信OpenID")):
    data = await IntegrationService(auth).wechat_pay(bill_id=bill_id, amount=amount, openid=openid)
    return SuccessResponse(data=data, msg="微信支付创建成功")


@router.post("/alipay-pay", summary="支付宝支付")
async def alipay_pay(
    auth: AuthSchema = Depends(get_current_user),
    bill_id: str = Query(..., description="账单ID"),
    amount: float = Query(..., description="金额（元）")):
    data = await IntegrationService(auth).alipay_pay(bill_id=bill_id, amount=amount)
    return SuccessResponse(data=data, msg="支付宝支付创建成功")


@router.post("/unionpay-pay", summary="银联支付")
async def unionpay_pay(
    auth: AuthSchema = Depends(get_current_user),
    bill_id: str = Query(..., description="账单ID"),
    amount: float = Query(..., description="金额（元）")):
    data = await IntegrationService(auth).unionpay_pay(bill_id=bill_id, amount=amount)
    return SuccessResponse(data=data, msg="银联支付创建成功")


@router.post("/medical-insurance/verify", summary="医保验证")
async def medical_insurance_verify(
    auth: AuthSchema = Depends(get_current_user),
    patient_id: str = Query(..., description="患者ID"),
    id_card: str = Query(..., description="身份证号")):
    data = await IntegrationService(auth).medical_insurance_verify(patient_id=patient_id, id_card=id_card)
    return SuccessResponse(data=data, msg="医保验证成功")


@router.post("/medical-insurance/pay", summary="医保支付")
async def medical_insurance_pay(
    auth: AuthSchema = Depends(get_current_user),
    bill_id: str = Query(..., description="账单ID"),
    amount: float = Query(..., description="金额（元）")):
    data = await IntegrationService(auth).medical_insurance_pay(bill_id=bill_id, amount=amount)
    return SuccessResponse(data=data, msg="医保支付成功")


@router.post("/wechat-auth", summary="微信授权")
async def wechat_auth(
    auth: AuthSchema = Depends(get_current_user),
    code: str = Query(..., description="微信授权码")):
    data = await IntegrationService(auth).wechat_auth(code=code)
    return SuccessResponse(data=data, msg="微信授权成功")
