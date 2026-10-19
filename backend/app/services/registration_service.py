"""
挂号服务：排班管理和挂号管理
"""
from typing import Optional, List, Dict, Any
from datetime import date, time
from sqlalchemy.orm import Session

from app.api.v1.module_registration.model import Schedule, Registration
from app.repositories.registration_repository import ScheduleRepository, RegistrationRepository
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger
from app.utils.common import generate_id


class RegistrationService:
    """挂号服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.schedule_repo = ScheduleRepository(db)
        self.registration_repo = RegistrationRepository(db)
    
    # 排班管理
    def create_schedule(self, schedule_data: Dict[str, Any], tenant_id: str, creator_id: str) -> Schedule:
        """创建排班"""
        from datetime import date as dt_date
        from uuid import UUID
        
        doctor_id = schedule_data.get("doctor_id")
        schedule_date_str = schedule_data.get("schedule_date")
        time_slot = schedule_data.get("time_slot")
        
        # 检查全天排班冲突
        if doctor_id and schedule_date_str:
            # 解析日期
            if isinstance(schedule_date_str, str):
                schedule_date = dt_date.fromisoformat(schedule_date_str)
            else:
                schedule_date = schedule_date_str
            
            # 检查该医生在该日期是否已有排班
            existing_schedules, _ = self.schedule_repo.get_schedules(
                tenant_id=tenant_id,
                doctor_id=doctor_id,
                schedule_date=schedule_date,
                skip=0,
                limit=100
            )
            
            # 检查冲突：如果创建的是全天排班，不能有其他时间段排班
            if time_slot == 'full_day':
                if existing_schedules:
                    raise BusinessException(
                        f"该医生在{schedule_date_str}已有其他时间段排班，不能创建全天排班。请先删除其他时间段的排班。",
                        code=400
                    )
            else:
                # 如果创建的是其他时间段排班，检查是否已有全天排班
                has_full_day = any(s.time_slot == 'full_day' for s in existing_schedules)
                if has_full_day:
                    raise BusinessException(
                        f"该医生在{schedule_date_str}已有全天排班，不能创建其他时间段的排班。",
                        code=400
                    )
        
        # 如果未设置挂号费，使用医生的默认挂号费
        from decimal import Decimal
        price = schedule_data.get("price")
        if not price or Decimal(str(price)) <= 0:
            if doctor_id:
                from app.repositories.system_repository import DoctorRepository
                try:
                    doctor_repo = DoctorRepository(self.db)
                    doctor_id_uuid = UUID(doctor_id) if isinstance(doctor_id, str) else doctor_id
                    doctor = doctor_repo.get_doctor_by_id(str(doctor_id_uuid), tenant_id)
                    if doctor and doctor.registration_fee:
                        schedule_data["price"] = float(doctor.registration_fee)
                        logger.info(f"使用医生默认挂号费: {doctor.name}, 金额: {doctor.registration_fee}")
                except Exception as e:
                    logger.warning(f"获取医生默认挂号费失败: {str(e)}", exc_info=True)
        
        schedule = self.schedule_repo.create_schedule(schedule_data, tenant_id)
        schedule.created_by = creator_id
        self.db.commit()
        
        logger.info(f"创建排班: {schedule.id} by {creator_id}")
        return schedule
    
    def get_schedule(self, schedule_id: str, tenant_id: str) -> Schedule:
        """获取排班详情"""
        schedule = self.schedule_repo.get_schedule_by_id(schedule_id, tenant_id)
        if not schedule:
            raise NotFoundException("排班", schedule_id)
        return schedule
    
    def list_schedules(
        self,
        tenant_id: str,
        doctor_id: Optional[str] = None,
        department_id: Optional[str] = None,
        schedule_date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Schedule], int]:
        """获取排班列表"""
        return self.schedule_repo.get_schedules(
            tenant_id, doctor_id, department_id, schedule_date, start_date, end_date, skip, limit
        )
    
    def update_schedule(
        self,
        schedule_id: str,
        tenant_id: str,
        schedule_data: Dict[str, Any],
        updater_id: str
    ) -> Schedule:
        """更新排班"""
        from datetime import date as dt_date
        from uuid import UUID
        
        # 获取当前排班信息
        schedule = self.schedule_repo.get_schedule_by_id(schedule_id, tenant_id)
        if not schedule:
            raise NotFoundException("排班", schedule_id)
        
        # 确定要检查的医生ID和日期
        doctor_id = schedule_data.get("doctor_id") or str(schedule.doctor_id)
        schedule_date_str = schedule_data.get("schedule_date")
        if schedule_date_str:
            if isinstance(schedule_date_str, str):
                schedule_date = dt_date.fromisoformat(schedule_date_str)
            else:
                schedule_date = schedule_date_str
        else:
            schedule_date = schedule.schedule_date
        
        # 确定要检查的时间段
        time_slot = schedule_data.get("time_slot") or schedule.time_slot
        
        # 检查全天排班冲突（排除当前排班）
        if doctor_id and schedule_date:
            existing_schedules, _ = self.schedule_repo.get_schedules(
                tenant_id=tenant_id,
                doctor_id=doctor_id,
                schedule_date=schedule_date,
                skip=0,
                limit=100
            )
            
            # 排除当前排班
            existing_schedules = [s for s in existing_schedules if str(s.id) != schedule_id]
            
            # 检查冲突：如果更新为全天排班，不能有其他时间段排班
            if time_slot == 'full_day':
                if existing_schedules:
                    raise BusinessException(
                        f"该医生在{schedule_date.isoformat() if hasattr(schedule_date, 'isoformat') else schedule_date}已有其他时间段排班，不能更新为全天排班。请先删除其他时间段的排班。",
                        code=400
                    )
            else:
                # 如果更新为其他时间段排班，检查是否已有全天排班
                has_full_day = any(s.time_slot == 'full_day' for s in existing_schedules)
                if has_full_day:
                    raise BusinessException(
                        f"该医生在{schedule_date.isoformat() if hasattr(schedule_date, 'isoformat') else schedule_date}已有全天排班，不能更新为其他时间段的排班。",
                        code=400
                    )
        
        schedule = self.schedule_repo.update_schedule(schedule_id, tenant_id, schedule_data)
        schedule.updated_by = updater_id
        self.db.commit()
        
        logger.info(f"更新排班: {schedule_id} by {updater_id}")
        return schedule
    
    # 挂号管理
    def create_registration(
        self,
        registration_data: Dict[str, Any],
        tenant_id: str,
        creator_id: str
    ) -> Registration:
        """创建挂号"""
        # 生成挂号单号
        registration_no = f"REG{generate_id()[:8].upper()}"
        registration_data["registration_no"] = registration_no
        
        # 检查排班逻辑：如果提供了doctor_id和registration_date，必须检查是否有对应的排班
        if registration_data.get("doctor_id") and registration_data.get("registration_date") and not registration_data.get("schedule_id"):
            # 尝试查找对应的排班
            from datetime import date as dt_date
            registration_date = registration_data.get("registration_date")
            if isinstance(registration_date, str):
                registration_date = dt_date.fromisoformat(registration_date)
            
            # 查找该医生在该日期的排班
            schedules, _ = self.schedule_repo.get_schedules(
                tenant_id=tenant_id,
                doctor_id=registration_data.get("doctor_id"),
                schedule_date=registration_date,
                skip=0,
                limit=10
            )
            
            if not schedules:
                raise BusinessException("该医生在该日期没有排班，无法挂号。请先创建排班。", code=400)
            
            # 查找状态为active且有剩余号源的排班
            available_schedule = None
            for schedule in schedules:
                if schedule.status == "active" and schedule.used_quota < schedule.total_quota:
                    available_schedule = schedule
                    break
            
            if not available_schedule:
                raise BusinessException("该医生在该日期没有可用的排班（已暂停或号源已满），无法挂号。", code=400)
            
            # 使用找到的排班
            registration_data["schedule_id"] = str(available_schedule.id)
            registration_data["doctor_id"] = str(available_schedule.doctor_id)
            if available_schedule.department_id:
                registration_data["department_id"] = str(available_schedule.department_id)
            if not registration_data.get("price"):
                registration_data["price"] = float(available_schedule.price) if available_schedule.price else 0.0
        
        # 检查号源
        if registration_data.get("schedule_id"):
            schedule = self.schedule_repo.get_schedule_by_id(registration_data["schedule_id"], tenant_id)
            if not schedule:
                raise BusinessException("排班不存在", code=400)
            
            # 检查排班状态
            if schedule.status != "active":
                raise BusinessException(f"排班状态为{schedule.status}，无法挂号", code=400)
            
            # 检查号源是否已满
            if schedule.used_quota >= schedule.total_quota:
                raise BusinessException("号源已满，无法挂号", code=400)
            
            try:
                self.schedule_repo.increase_used_quota(
                    registration_data["schedule_id"],
                    tenant_id
                )
            except BusinessException:
                raise BusinessException("号源已满，无法挂号", code=400)
        
        registration = self.registration_repo.create_registration(registration_data, tenant_id)
        registration.created_by = creator_id
        
        # 如果挂号费大于0，自动创建账单
        price = float(registration.price) if registration.price else 0.0
        if price > 0:
            from app.repositories.payment_repository import BillRepository
            from decimal import Decimal
            
            bill_repo = BillRepository(self.db)
            bill_no = f"BILL{generate_id()[:8].upper()}"
            
            bill_data = {
                "bill_no": bill_no,
                "patient_id": str(registration.patient_id),
                "registration_id": str(registration.id),
                "bill_type": "registration",
                "total_amount": Decimal(str(price)),
                "paid_amount": Decimal("0"),
                "discount_amount": Decimal("0"),
                "insurance_amount": Decimal("0"),
                "status": "unpaid",
            }
            
            bill = bill_repo.create_bill(bill_data, tenant_id)
            bill.created_by = creator_id
            self.db.commit()
            logger.info(f"自动创建挂号账单: {bill.id} for registration {registration.id}")
        
        self.db.commit()
        
        logger.info(f"创建挂号: {registration.id} by {creator_id}")
        return registration
    
    def get_registration(self, registration_id: str, tenant_id: str) -> Registration:
        """获取挂号详情"""
        registration = self.registration_repo.get_registration_by_id(registration_id, tenant_id)
        if not registration:
            raise NotFoundException("挂号", registration_id)
        return registration
    
    def list_registrations(
        self,
        tenant_id: str,
        patient_id: Optional[str] = None,
        doctor_id: Optional[str] = None,
        registration_date: Optional[date] = None,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Registration], int]:
        """获取挂号列表"""
        return self.registration_repo.get_registrations(
            tenant_id, patient_id, doctor_id, registration_date, status, payment_status, skip, limit
        )
    
    def cancel_registration(self, registration_id: str, tenant_id: str, canceller_id: str) -> Registration:
        """取消挂号"""
        registration = self.registration_repo.cancel_registration(registration_id, tenant_id)
        
        # 如果已支付挂号费，自动退费
        paid_amount = float(registration.paid_amount) if registration.paid_amount else 0.0
        if paid_amount > 0:
            from decimal import Decimal
            registration.paid_amount = Decimal("0")
            registration.payment_status = "refunded"
            self.db.commit()
            logger.info(f"取消挂号自动退费: {registration_id}, 退费金额: {paid_amount}")
        
        # 释放号源
        if registration.schedule_id:
            self.schedule_repo.decrease_used_quota(
                str(registration.schedule_id),
                tenant_id
            )
        
        logger.info(f"取消挂号: {registration_id} by {canceller_id}")
        return registration

