"""
Pydantic 模型（仪表盘统计）
"""
from typing import Optional, List, Any

from pydantic import BaseModel, Field
from app.core.base_schema import BaseSchema


class DashboardStatSchema(BaseModel):
    """仪表盘统计数据"""
    model_config = ConfigDict(from_attributes=True)

    today_registrations: int = Field(default=0, comment="今日挂号数")
    pending_registrations: int = Field(default=0, comment="待接诊数")
    today_revenue: float = Field(default=0.0, comment="今日营收")
    patient_total: int = Field(default=0, comment="患者总数")
    doctor_total: int = Field(default=0, comment="医生总数")
    drug_total: int = Field(default=0, comment="药品总数")
    recent_registrations: List[Any] = Field(default_factory=list, comment="最近挂号")
    chart: dict = Field(default_factory=dict, comment="趋势图数据")


class DashboardChartSchema(BaseModel):
    """仪表盘趋势图"""
    model_config = ConfigDict(from_attributes=True)

    dates: List[str] = Field(default_factory=list, comment="日期列表")
    registrations: List[int] = Field(default_factory=list, comment="每日挂号数")
    revenue: List[float] = Field(default_factory=list, comment="每日营收")
