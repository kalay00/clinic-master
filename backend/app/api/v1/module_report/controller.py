"""
控制器（报表模块，已迁移业务逻辑至 service.py）
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user

from .service import ReportService


router = APIRouter()


@router.get("/revenue", summary="收入报表")
async def revenue_report(
    auth: AuthSchema = Depends(get_current_user),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期")):
    data = await ReportService(auth).get_revenue_report(start_date=start_date, end_date=end_date)
    return SuccessResponse(data=data, msg="查询成功")


@router.get("/visits", summary="就诊量报表")
async def visits_report(
    auth: AuthSchema = Depends(get_current_user),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期")):
    data = await ReportService(auth).get_visits_report(start_date=start_date, end_date=end_date)
    return SuccessResponse(data=data, msg="查询成功")


@router.get("/drugs", summary="药品销售报表")
async def drugs_report(
    auth: AuthSchema = Depends(get_current_user),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期")):
    data = await ReportService(auth).get_drugs_report(start_date=start_date, end_date=end_date)
    return SuccessResponse(data=data, msg="查询成功")


@router.get("/daily", summary="每日统计")
async def daily_report(
    auth: AuthSchema = Depends(get_current_user),
    target_date: Optional[date] = Query(None, description="目标日期（默认今天）")):
    data = await ReportService(auth).get_daily_statistics(target_date=target_date)
    return SuccessResponse(data=data, msg="查询成功")


@router.get("/dashboard", summary="工作台统计")
async def dashboard_report(
    auth: AuthSchema = Depends(get_current_user),
    target_date: Optional[date] = Query(None, description="目标日期（默认今天）")):
    data = await ReportService(auth).get_dashboard_stats(target_date=target_date)
    return SuccessResponse(data=data, msg="查询成功")


@router.get("/patients", summary="患者统计报表")
async def patients_report(
    auth: AuthSchema = Depends(get_current_user),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期")):
    data = await ReportService(auth).get_patients_report(start_date=start_date, end_date=end_date)
    return SuccessResponse(data=data, msg="查询成功")
