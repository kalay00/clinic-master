"""
医保局监管API
v2.0新增功能
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_user_id, get_current_tenant_id
from app.services.medical_insurance_regulatory_service import MedicalInsuranceRegulatoryService
from app.services.medical_insurance_data_reporter import MedicalInsuranceDataReporter
from app.tasks.medical_insurance_report_tasks import report_settlement_task, report_batch_settlements_task
from app.core.exceptions import NotFoundException
from app.core.response import success_response, error_response
from app.core.logger import logger

router = APIRouter(prefix="/medical-insurance", tags=["医保监管"])


# ==================== 请求模型 ====================

class ReportSettlementRequest(BaseModel):
    """上报结算数据请求"""
    settlement_id: str
    async_report: bool = True  # 是否异步上报


class ReportBatchSettlementsRequest(BaseModel):
    """批量上报结算数据请求"""
    settlement_ids: List[str]
    async_report: bool = True  # 是否异步上报


# ==================== 结算管理API ====================

@router.get(
    "/settlements",
    summary="获取医保结算记录列表",
    description="获取医保结算记录列表，支持多种查询条件",
)
async def list_settlements(
    request: Request,
    bill_id: Optional[str] = Query(None, description="账单ID"),
    patient_id: Optional[str] = Query(None, description="患者ID"),
    status: Optional[str] = Query(None, description="结算状态"),
    report_status: Optional[str] = Query(None, description="上报状态"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="每页记录数"),
    db: Session = Depends(get_db)
):
    """获取医保结算记录列表"""
    try:
        tenant_id = get_current_tenant_id(request)
        service = MedicalInsuranceRegulatoryService(db)
        
        settlements, total = service.list_settlements(
            tenant_id, bill_id, patient_id, status, report_status, None, None, skip, limit
        )
        
        settlement_list = []
        for settlement in settlements:
            settlement_list.append({
                "id": str(settlement.id),
                "settlement_no": settlement.settlement_no,
                "bill_id": str(settlement.bill_id),
                "patient_id": str(settlement.patient_id),
                "total_amount": float(settlement.total_amount) if settlement.total_amount else 0,
                "insurance_amount": float(settlement.insurance_amount) if settlement.insurance_amount else 0,
                "personal_amount": float(settlement.personal_amount) if settlement.personal_amount else 0,
                "status": settlement.status,
                "report_status": settlement.report_status,
                "settlement_time": settlement.settlement_time.isoformat() if settlement.settlement_time else None,
                "reported_at": settlement.reported_at.isoformat() if settlement.reported_at else None,
                "created_at": settlement.created_at.isoformat() if settlement.created_at else None,
            })
        
        return success_response(data={
            "items": settlement_list,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        })
        
    except Exception as e:
        logger.error(f"获取医保结算记录列表失败: {str(e)}", exc_info=True)
        return error_response(message=f"获取医保结算记录列表失败: {str(e)}", code=500)


@router.get(
    "/settlements/{settlement_id}",
    summary="获取医保结算记录详情",
    description="获取医保结算记录的详细信息",
)
async def get_settlement(
    settlement_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """获取医保结算记录详情"""
    try:
        tenant_id = get_current_tenant_id(request)
        service = MedicalInsuranceRegulatoryService(db)
        
        settlement = service.get_settlement(settlement_id, tenant_id)
        
        return success_response(data={
            "id": str(settlement.id),
            "settlement_no": settlement.settlement_no,
            "bill_id": str(settlement.bill_id),
            "patient_id": str(settlement.patient_id),
            "medical_record_id": str(settlement.medical_record_id) if settlement.medical_record_id else None,
            "insurance_card_no": settlement.insurance_card_no,
            "insurance_type": settlement.insurance_type,
            "total_amount": float(settlement.total_amount) if settlement.total_amount else 0,
            "insurance_amount": float(settlement.insurance_amount) if settlement.insurance_amount else 0,
            "personal_amount": float(settlement.personal_amount) if settlement.personal_amount else 0,
            "reimbursement_ratio": float(settlement.reimbursement_ratio) if settlement.reimbursement_ratio else None,
            "status": settlement.status,
            "report_status": settlement.report_status,
            "settlement_time": settlement.settlement_time.isoformat() if settlement.settlement_time else None,
            "reported_at": settlement.reported_at.isoformat() if settlement.reported_at else None,
            "settlement_details": settlement.settlement_details,
            "error_message": settlement.error_message,
            "report_error": settlement.report_error,
            "created_at": settlement.created_at.isoformat() if settlement.created_at else None,
        })
        
    except NotFoundException as e:
        return error_response(message=str(e), code=404)
    except Exception as e:
        logger.error(f"获取医保结算记录详情失败: {str(e)}", exc_info=True)
        return error_response(message=f"获取医保结算记录详情失败: {str(e)}", code=500)


@router.post(
    "/settlements/{settlement_id}/report",
    summary="上报医保结算数据",
    description="向监管系统上报医保结算数据，支持同步和异步上报",
)
async def report_settlement(
    settlement_id: str,
    request: Request,
    async_report: bool = Query(True, description="是否异步上报"),
    db: Session = Depends(get_db)
):
    """上报医保结算数据"""
    try:
        tenant_id = get_current_tenant_id(request)
        user_id = get_current_user_id(request)
        
        if async_report:
            # 异步上报（使用Celery任务）
            task = report_settlement_task.delay(settlement_id, tenant_id, user_id)
            
            return success_response(data={
                "task_id": task.id,
                "settlement_id": settlement_id,
                "async": True,
                "message": "上报任务已提交，正在异步处理",
            })
        else:
            # 同步上报
            reporter = MedicalInsuranceDataReporter(db)
            result = await reporter.report_settlement(settlement_id, tenant_id, user_id)
            
            return success_response(data={
                "settlement_id": settlement_id,
                "async": False,
                "result": result,
            })
            
    except NotFoundException as e:
        return error_response(message=str(e), code=404)
    except Exception as e:
        logger.error(f"上报医保结算数据失败: {str(e)}", exc_info=True)
        return error_response(message=f"上报医保结算数据失败: {str(e)}", code=500)


@router.post(
    "/settlements/batch-report",
    summary="批量上报医保结算数据",
    description="批量向监管系统上报医保结算数据，支持同步和异步上报",
)
async def report_batch_settlements(
    request_body: ReportBatchSettlementsRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """批量上报医保结算数据"""
    try:
        tenant_id = get_current_tenant_id(request)
        user_id = get_current_user_id(request)
        
        if request_body.async_report:
            # 异步上报（使用Celery任务）
            task = report_batch_settlements_task.delay(
                request_body.settlement_ids, tenant_id, user_id
            )
            
            return success_response(data={
                "task_id": task.id,
                "total": len(request_body.settlement_ids),
                "async": True,
                "message": "批量上报任务已提交，正在异步处理",
            })
        else:
            # 同步上报
            reporter = MedicalInsuranceDataReporter(db)
            result = await reporter.report_batch_settlements(
                request_body.settlement_ids, tenant_id, user_id
            )
            
            return success_response(data={
                "total": result.get("total"),
                "success": result.get("success"),
                "failure": result.get("failure"),
                "async": False,
                "results": result.get("results"),
            })
            
    except Exception as e:
        logger.error(f"批量上报医保结算数据失败: {str(e)}", exc_info=True)
        return error_response(message=f"批量上报医保结算数据失败: {str(e)}", code=500)


# ==================== 违规管理API ====================

@router.get(
    "/violations",
    summary="获取医保违规记录列表",
    description="获取医保违规记录列表，支持多种查询条件",
)
async def list_violations(
    request: Request,
    violation_type: Optional[str] = Query(None, description="违规类型"),
    violation_level: Optional[str] = Query(None, description="违规级别"),
    status: Optional[str] = Query(None, description="处理状态"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="每页记录数"),
    db: Session = Depends(get_db)
):
    """获取医保违规记录列表"""
    try:
        tenant_id = get_current_tenant_id(request)
        service = MedicalInsuranceRegulatoryService(db)
        
        violations, total = service.list_violations(
            tenant_id, violation_type, violation_level, status, None, None, None, skip, limit
        )
        
        violation_list = []
        for violation in violations:
            violation_list.append({
                "id": str(violation.id),
                "violation_no": violation.violation_no,
                "violation_type": violation.violation_type,
                "violation_level": violation.violation_level,
                "violation_desc": violation.violation_desc,
                "violation_amount": float(violation.violation_amount) if violation.violation_amount else None,
                "status": violation.status,
                "detected_at": violation.detected_at.isoformat() if violation.detected_at else None,
                "created_at": violation.created_at.isoformat() if violation.created_at else None,
            })
        
        return success_response(data={
            "items": violation_list,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        })
        
    except Exception as e:
        logger.error(f"获取医保违规记录列表失败: {str(e)}", exc_info=True)
        return error_response(message=f"获取医保违规记录列表失败: {str(e)}", code=500)


# ==================== 政策管理API ====================

@router.get(
    "/policies",
    summary="获取医保政策列表",
    description="获取医保政策列表，支持按类型和状态筛选",
)
async def list_policies(
    request: Request,
    policy_type: Optional[str] = Query(None, description="政策类型"),
    is_active: Optional[bool] = Query(None, description="是否生效"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="每页记录数"),
    db: Session = Depends(get_db)
):
    """获取医保政策列表"""
    try:
        tenant_id = get_current_tenant_id(request)
        service = MedicalInsuranceRegulatoryService(db)
        
        policies, total = service.list_policies(
            tenant_id, policy_type, is_active, None, skip, limit
        )
        
        policy_list = []
        for policy in policies:
            policy_list.append({
                "id": str(policy.id),
                "policy_name": policy.policy_name,
                "policy_code": policy.policy_code,
                "policy_type": policy.policy_type,
                "version": policy.version,
                "is_active": policy.is_active,
                "effective_date": policy.effective_date.isoformat() if policy.effective_date else None,
                "expiry_date": policy.expiry_date.isoformat() if policy.expiry_date else None,
                "created_at": policy.created_at.isoformat() if policy.created_at else None,
            })
        
        return success_response(data={
            "items": policy_list,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        })
        
    except Exception as e:
        logger.error(f"获取医保政策列表失败: {str(e)}", exc_info=True)
        return error_response(message=f"获取医保政策列表失败: {str(e)}", code=500)

