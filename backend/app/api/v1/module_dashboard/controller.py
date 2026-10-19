"""
仪表盘统计控制器
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from .service import DashboardService


router = APIRouter()


@router.get("/data", summary="获取仪表盘统计数据", dependencies=[Depends(AuthPermission(permission=["dashboard:view"]))])
async def get_data(auth: AuthSchema = Depends(get_current_user)):
    data = await DashboardService(auth).get_stats()
    return SuccessResponse(data=data, msg="查询成功")


@router.get("/chart", summary="获取仪表盘趋势图", dependencies=[Depends(AuthPermission(permission=["dashboard:view"]))])
async def get_chart(
    auth: AuthSchema = Depends(get_current_user),
    type: Optional[str] = Query("week", description="week/month/year"),
):
    data = await DashboardService(auth).get_chart(type)
    return SuccessResponse(data=data, msg="查询成功")
