"""
系统管理数据仓库：科室、医生
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_

from app.api.v1.module_department.model import Department
from app.api.v1.module_doctor.model import Doctor
from app.core.exceptions import NotFoundException, BusinessException


class DepartmentRepository:
    """科室数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_department(self, department_data: dict, tenant_id: str) -> Department:
        """创建科室"""
        from uuid import UUID
        # 将tenant_id转换为UUID对象（如果模型使用UUID类型）
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        # 检查科室编码是否已存在（同一租户内）
        code = department_data.get("code", "").strip().upper()
        existing = self.db.query(Department).filter(
            and_(
                Department.tenant_id == tenant_id_uuid,
                Department.code == code,
                Department.deleted_at.is_(None)
            )
        ).first()
        if existing:
            raise BusinessException(f"科室编码 {code} 已存在")
        
        department = Department(
            tenant_id=tenant_id_uuid,
            name=department_data["name"],
            code=code,
            description=department_data.get("description"),
            status=department_data.get("status", "active"),
            sort_order=department_data.get("sort_order", 0),
        )
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        return department
    
    def get_department_by_id(self, department_id: str, tenant_id: str) -> Optional[Department]:
        """根据ID获取科室"""
        from uuid import UUID
        # 将ID转换为UUID对象（如果模型使用UUID类型）
        if isinstance(department_id, str):
            try:
                department_id_uuid = UUID(department_id)
            except (ValueError, TypeError):
                department_id_uuid = department_id
        else:
            department_id_uuid = department_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Department).filter(
            and_(
                Department.id == department_id_uuid,
                Department.tenant_id == tenant_id_uuid,
                Department.deleted_at.is_(None)
            )
        ).first()
    
    def get_departments(self, tenant_id: str, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> tuple[List[Department], int]:
        """获取科室列表"""
        from uuid import UUID
        # 将tenant_id转换为UUID对象（如果模型使用UUID类型）
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(Department).filter(
            and_(
                Department.tenant_id == tenant_id_uuid,
                Department.deleted_at.is_(None)
            )
        )
        
        if search:
            query = query.filter(
                or_(
                    Department.name.ilike(f"%{search}%"),
                    Department.code.ilike(f"%{search}%")
                )
            )
        
        total = query.count()
        departments = query.order_by(Department.sort_order, Department.created_at).offset(skip).limit(limit).all()
        
        return departments, total
    
    def update_department(self, department_id: str, tenant_id: str, department_data: dict) -> Department:
        """更新科室"""
        department = self.get_department_by_id(department_id, tenant_id)
        if not department:
            raise NotFoundException("科室", department_id)
        
        for key, value in department_data.items():
            setattr(department, key, value)
        
        self.db.commit()
        self.db.refresh(department)
        return department
    
    def delete_department(self, department_id: str, tenant_id: str) -> bool:
        """删除科室（软删除）"""
        department = self.get_department_by_id(department_id, tenant_id)
        if not department:
            raise NotFoundException("科室", department_id)
        
        department.soft_delete()
        self.db.commit()
        return True


class DoctorRepository:
    """医生数据仓库"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_doctor(self, doctor_data: dict, tenant_id: str) -> Doctor:
        """创建医生"""
        from uuid import UUID
        # 将tenant_id转换为UUID对象
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        # 转换department_id和user_id
        department_id = doctor_data.get("department_id")
        if department_id and isinstance(department_id, str):
            try:
                department_id = UUID(department_id)
            except (ValueError, TypeError):
                pass
        
        user_id = doctor_data.get("user_id")
        if user_id and isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except (ValueError, TypeError):
                pass
        
        from decimal import Decimal
        registration_fee = doctor_data.get("registration_fee")
        if registration_fee is not None:
            registration_fee = Decimal(str(registration_fee))
        else:
            registration_fee = Decimal("0")
        
        doctor = Doctor(
            tenant_id=tenant_id_uuid,
            name=doctor_data["name"],
            employee_no=doctor_data["employee_no"],
            department_id=department_id,
            title=doctor_data.get("title"),
            specialty=doctor_data.get("specialty"),
            phone=doctor_data.get("phone"),
            email=doctor_data.get("email"),
            registration_fee=registration_fee,
            status=doctor_data.get("status", "active"),
            user_id=user_id,
        )
        self.db.add(doctor)
        self.db.commit()
        self.db.refresh(doctor)
        return doctor
    
    def get_doctor_by_id(self, doctor_id: str, tenant_id: str) -> Optional[Doctor]:
        """根据ID获取医生"""
        from uuid import UUID
        # 将ID转换为UUID对象（如果模型使用UUID类型）
        if isinstance(doctor_id, str):
            try:
                doctor_id_uuid = UUID(doctor_id)
            except (ValueError, TypeError):
                doctor_id_uuid = doctor_id
        else:
            doctor_id_uuid = doctor_id
        
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        return self.db.query(Doctor).filter(
            and_(
                Doctor.id == doctor_id_uuid,
                Doctor.tenant_id == tenant_id_uuid,
                Doctor.deleted_at.is_(None)
            )
        ).first()
    
    def get_doctors(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        department_id: Optional[str] = None
    ) -> tuple[List[Doctor], int]:
        """获取医生列表"""
        from uuid import UUID
        # 将tenant_id转换为UUID对象
        if isinstance(tenant_id, str):
            try:
                tenant_id_uuid = UUID(tenant_id)
            except (ValueError, TypeError):
                tenant_id_uuid = tenant_id
        else:
            tenant_id_uuid = tenant_id
        
        query = self.db.query(Doctor).filter(
            and_(
                Doctor.tenant_id == tenant_id_uuid,
                Doctor.deleted_at.is_(None)
            )
        )
        
        if search:
            query = query.filter(
                (Doctor.name.ilike(f"%{search}%")) |
                (Doctor.employee_no.ilike(f"%{search}%"))
            )
        
        if department_id:
            # 将department_id转换为UUID对象
            if isinstance(department_id, str):
                try:
                    department_id_uuid = UUID(department_id)
                except (ValueError, TypeError):
                    department_id_uuid = department_id
            else:
                department_id_uuid = department_id
            query = query.filter(Doctor.department_id == department_id_uuid)
        
        total = query.count()
        doctors = query.order_by(Doctor.created_at.desc()).offset(skip).limit(limit).all()
        
        return doctors, total
    
    def update_doctor(self, doctor_id: str, tenant_id: str, doctor_data: dict) -> Doctor:
        """更新医生"""
        doctor = self.get_doctor_by_id(doctor_id, tenant_id)
        if not doctor:
            raise NotFoundException("医生", doctor_id)
        
        from decimal import Decimal
        # 处理registration_fee字段
        if "registration_fee" in doctor_data:
            registration_fee = doctor_data.get("registration_fee")
            if registration_fee is not None:
                doctor_data["registration_fee"] = Decimal(str(registration_fee))
            else:
                doctor_data["registration_fee"] = Decimal("0")
        
        for key, value in doctor_data.items():
            setattr(doctor, key, value)
        
        self.db.commit()
        self.db.refresh(doctor)
        return doctor
    
    def delete_doctor(self, doctor_id: str, tenant_id: str) -> bool:
        """删除医生（软删除）"""
        doctor = self.get_doctor_by_id(doctor_id, tenant_id)
        if not doctor:
            raise NotFoundException("医生", doctor_id)
        
        doctor.soft_delete()
        self.db.commit()
        return True

