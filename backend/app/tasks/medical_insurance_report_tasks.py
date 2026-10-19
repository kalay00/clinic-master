"""
医保数据上报异步任务
v2.0新增功能
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.core.database import get_db
from app.services.medical_insurance_data_reporter import MedicalInsuranceDataReporter
from app.core.logger import logger


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def report_settlement_task(
    self,
    settlement_id: str,
    tenant_id: str,
    user_id: str
) -> Dict[str, Any]:
    """
    上报医保结算数据异步任务
    
    Args:
        settlement_id: 结算记录ID
        tenant_id: 租户ID
        user_id: 操作用户ID
    
    Returns:
        Dict[str, Any]: 上报结果
    """
    try:
        # 获取数据库会话
        db = next(get_db())
        
        try:
            # 创建上报服务
            reporter = MedicalInsuranceDataReporter(db)
            
            # 执行上报（注意：这里需要同步调用，因为Celery任务本身不是async）
            # 如果reporter的方法需要async，需要在这里使用asyncio.run
            import asyncio
            result = asyncio.run(reporter.report_settlement(settlement_id, tenant_id, user_id))
            
            logger.info(f"医保结算数据上报任务完成: settlement_id={settlement_id}")
            
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"医保结算数据上报任务失败: settlement_id={settlement_id}, error={str(e)}")
        
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"重试上报任务: settlement_id={settlement_id}, retry_count={self.request.retries + 1}")
            raise self.retry(exc=e)
        else:
            # 达到最大重试次数，返回失败结果
            return {
                "success": False,
                "error_message": f"上报失败，已重试{self.max_retries}次: {str(e)}",
            }


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def report_batch_settlements_task(
    self,
    settlement_ids: List[str],
    tenant_id: str,
    user_id: str
) -> Dict[str, Any]:
    """
    批量上报医保结算数据异步任务
    
    Args:
        settlement_ids: 结算记录ID列表
        tenant_id: 租户ID
        user_id: 操作用户ID
    
    Returns:
        Dict[str, Any]: 批量上报结果统计
    """
    try:
        # 获取数据库会话
        db = next(get_db())
        
        try:
            # 创建上报服务
            reporter = MedicalInsuranceDataReporter(db)
            
            # 执行批量上报
            import asyncio
            result = asyncio.run(reporter.report_batch_settlements(settlement_ids, tenant_id, user_id))
            
            logger.info(f"批量医保结算数据上报任务完成: 总数={result.get('total')}, 成功={result.get('success')}, 失败={result.get('failure')}")
            
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"批量医保结算数据上报任务失败: error={str(e)}")
        
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f"重试批量上报任务: retry_count={self.request.retries + 1}")
            raise self.retry(exc=e)
        else:
            # 达到最大重试次数，返回失败结果
            return {
                "total": len(settlement_ids),
                "success": 0,
                "failure": len(settlement_ids),
                "error_message": f"批量上报失败，已重试{self.max_retries}次: {str(e)}",
            }

