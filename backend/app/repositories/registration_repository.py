"""
挂号数据仓库：排班和挂号的数据操作
"""
from typing import Optional, List
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.api.v1.module_registration.model import Schedule, Registration
from app.core.exceptions import NotFoundException, BusinessException
from app.core.logger import logger


class ScheduleRepository:
    """排班数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_schedule(self, schedule_data: dict, tenant_id: str) -> Schedule:
        """创建排班"""
        schedule = Schedule(
            tenant_id=tenant_id,
            **schedule_data
        )
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def get_schedule_by_id(self, schedule_id: str, tenant_id: str) -> Optional[Schedule]:
        """根据ID获取排班"""
        return self.db.query(Schedule).filter(
            and_(
                Schedule.id == schedule_id,
                Schedule.tenant_id == tenant_id,
                Schedule.deleted_at.is_(None)
            )
        ).first()
    
    def get_schedules(
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
        from sqlalchemy.orm import joinedload
        from uuid import UUID
        from app.api.v1.module_doctor.model import Doctor
        from app.api.v1.module_department.model import Department
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(Schedule).options(
            joinedload(Schedule.doctor),
            joinedload(Schedule.department)
        ).filter(
            and_(
                Schedule.tenant_id == tenant_id_uuid,
                Schedule.deleted_at.is_(None)
            )
        )
        
        if doctor_id:
            if isinstance(doctor_id, str):
                try:
                    doctor_id_uuid = UUID(doctor_id)
                except (ValueError, TypeError):
                    doctor_id_uuid = doctor_id
            else:
                doctor_id_uuid = doctor_id
            query = query.filter(Schedule.doctor_id == doctor_id_uuid)
        if department_id:
            if isinstance(department_id, str):
                try:
                    department_id_uuid = UUID(department_id)
                except (ValueError, TypeError):
                    department_id_uuid = department_id
            else:
                department_id_uuid = department_id
            query = query.filter(Schedule.department_id == department_id_uuid)
        
        # 日期筛选：优先使用日期范围，其次使用单个日期
        if start_date and end_date:
            query = query.filter(
                and_(
                    Schedule.schedule_date >= start_date,
                    Schedule.schedule_date <= end_date
                )
            )
        elif schedule_date:
            query = query.filter(Schedule.schedule_date == schedule_date)
        
        total = query.count()
        schedules = query.order_by(Schedule.schedule_date.asc(), Schedule.start_time).offset(skip).limit(limit).all()
        return schedules, total
    
    def update_schedule(self, schedule_id: str, tenant_id: str, schedule_data: dict) -> Schedule:
        """更新排班"""
        schedule = self.get_schedule_by_id(schedule_id, tenant_id)
        if not schedule:
            raise NotFoundException("排班", schedule_id)
        
        for key, value in schedule_data.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)
        
        self.db.commit()
        self.db.refresh(schedule)
        return schedule
    
    def increase_used_quota(self, schedule_id: str, tenant_id: str) -> bool:
        """增加已用号源"""
        schedule = self.get_schedule_by_id(schedule_id, tenant_id)
        if not schedule:
            return False
        
        if schedule.used_quota >= schedule.total_quota:
            raise BusinessException("号源已满", code=400)
        
        schedule.used_quota += 1
        self.db.commit()
        return True
    
    def decrease_used_quota(self, schedule_id: str, tenant_id: str) -> bool:
        """减少已用号源"""
        schedule = self.get_schedule_by_id(schedule_id, tenant_id)
        if not schedule:
            return False
        
        if schedule.used_quota > 0:
            schedule.used_quota -= 1
            self.db.commit()
        return True


class RegistrationRepository:
    """挂号数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_registration(self, registration_data: dict, tenant_id: str) -> Registration:
        """创建挂号"""
        registration = Registration(
            tenant_id=tenant_id,
            **registration_data
        )
        self.db.add(registration)
        self.db.commit()
        self.db.refresh(registration)
        return registration
    
    def get_registration_by_id(self, registration_id: str, tenant_id: str) -> Optional[Registration]:
        """根据ID获取挂号"""
        from sqlalchemy.orm import joinedload
        from uuid import UUID
        
        # 转换ID为UUID
        if isinstance(registration_id, str):
            try:
                registration_id_uuid = UUID(registration_id)
            except (ValueError, TypeError):
                registration_id_uuid = registration_id
        else:
            registration_id_uuid = registration_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Registration).options(
            joinedload(Registration.patient),
            joinedload(Registration.doctor),
            joinedload(Registration.department),
            joinedload(Registration.schedule)
        ).filter(
            and_(
                Registration.id == registration_id_uuid,
                Registration.tenant_id == tenant_id_uuid,
                Registration.deleted_at.is_(None)
            )
        ).first()
    
    def get_registrations(
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
        from sqlalchemy.orm import joinedload
        from uuid import UUID
        
        # 转换tenant_id为UUID
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(Registration).options(
            joinedload(Registration.patient),
            joinedload(Registration.doctor),
            joinedload(Registration.department),
            joinedload(Registration.schedule)  # 加载排班关系，用于获取预约时间
        ).filter(
            and_(
                Registration.tenant_id == tenant_id_uuid,
                Registration.deleted_at.is_(None)
            )
        )
        
        if patient_id:
            if isinstance(patient_id, str):
                try:
                    patient_id_uuid = UUID(patient_id)
                except (ValueError, TypeError):
                    patient_id_uuid = patient_id
            else:
                patient_id_uuid = patient_id
            query = query.filter(Registration.patient_id == patient_id_uuid)
        if doctor_id:
            if isinstance(doctor_id, str):
                try:
                    doctor_id_uuid = UUID(doctor_id)
                except (ValueError, TypeError):
                    doctor_id_uuid = doctor_id
            else:
                doctor_id_uuid = doctor_id
            query = query.filter(Registration.doctor_id == doctor_id_uuid)
        if registration_date:
            query = query.filter(Registration.registration_date == registration_date)
        if status:
            query = query.filter(Registration.status == status)
        if payment_status:
            query = query.filter(Registration.payment_status == payment_status)
        
        total = query.count()
        # 按创建时间倒序排列（最新的在前）
        registrations = query.order_by(Registration.created_at.desc()).offset(skip).limit(limit).all()
        return registrations, total
    
    def update_registration(self, registration_id: str, tenant_id: str, registration_data: dict) -> Registration:
        """更新挂号"""
        registration = self.get_registration_by_id(registration_id, tenant_id)
        if not registration:
            raise NotFoundException("挂号", registration_id)
        
        for key, value in registration_data.items():
            if hasattr(registration, key):
                setattr(registration, key, value)
        
        self.db.commit()
        self.db.refresh(registration)
        return registration
    
    def cancel_registration(self, registration_id: str, tenant_id: str) -> Registration:
        """取消挂号"""
        registration = self.get_registration_by_id(registration_id, tenant_id)
        if not registration:
            raise NotFoundException("挂号", registration_id)
        
        if registration.status == "cancelled":
            raise BusinessException("挂号已取消", code=400)
        
        registration.status = "cancelled"
        self.db.commit()
        self.db.refresh(registration)
        return registration

