"""
项目模块 Service
"""
from typing import Optional
from datetime import date, timedelta
from sqlalchemy import select, func
from app.core.base_crud import CRUDBase
from app.core.base_schema import AuthSchema
from app.core.exceptions import CustomException
from .model import ProjectCategory, Project, PatientProject, ProjectVerification
from .schema import (
    ProjectCategorySchema, ProjectCategoryCreateSchema, ProjectCategoryUpdateSchema,
    ProjectSchema, ProjectCreateSchema, ProjectUpdateSchema,
    PurchaseCreateSchema, VerificationCreateSchema,
)
from app.api.v1.module_patient.model import Patient
from app.api.v1.module_member.model import MemberLevel


class ProjectService:
    def __init__(self, auth: AuthSchema):
        self.auth = auth
        self.db = auth.db

    # ---------- 分类 ----------
    async def list_categories(self, page, page_size, keyword=None, status=None):
        search = {}
        if keyword:
            search["name"] = ("like", keyword)
        if status:
            search["status"] = status
        return await CRUDBase(ProjectCategory, self.auth, self.db).page(
            offset=(page - 1) * page_size, limit=page_size,
            order_by=[{"sort": "asc"}, {"created_at": "desc"}],
            search=search, out_schema=ProjectCategorySchema,
        )

    async def create_category(self, data: ProjectCategoryCreateSchema):
        obj = await CRUDBase(ProjectCategory, self.auth, self.db).create(data.model_dump())
        return ProjectCategorySchema.model_validate(obj).model_dump()

    async def update_category(self, cid, data: ProjectCategoryUpdateSchema):
        obj = await CRUDBase(ProjectCategory, self.auth, self.db).update(cid, data.model_dump(exclude_unset=True))
        return ProjectCategorySchema.model_validate(obj).model_dump()

    async def delete_category(self, ids: list):
        # 分类下存在项目则禁止删除
        for cid in ids:
            cnt = (await self.db.execute(
                select(func.count()).select_from(Project).where(Project.category_id == str(cid), Project.deleted_at.is_(None))
            )).scalar() or 0
            if cnt > 0:
                raise CustomException(msg="该分类下存在项目，无法删除")
        await CRUDBase(ProjectCategory, self.auth, self.db).delete(ids)
        return True

    # ---------- 项目 ----------
    async def list_projects(self, page, page_size, keyword=None, category_id=None, status=None):
        search = {}
        if keyword:
            search["name"] = ("like", keyword)
        if category_id:
            search["category_id"] = str(category_id)
        if status:
            search["status"] = status
        result = await CRUDBase(Project, self.auth, self.db).page(
            offset=(page - 1) * page_size, limit=page_size,
            order_by=[{"created_at": "desc"}], search=search, out_schema=ProjectSchema,
        )
        # 填充分类名称
        cats = (await self.db.execute(select(ProjectCategory))).scalars().all()
        cat_map = {str(c.id): c.name for c in cats}
        for item in result.items:
            item["category_name"] = cat_map.get(item.get("category_id"))
        return result

    async def create_project(self, data: ProjectCreateSchema):
        obj = await CRUDBase(Project, self.auth, self.db).create(data.model_dump())
        return ProjectSchema.model_validate(obj).model_dump()

    async def update_project(self, pid, data: ProjectUpdateSchema):
        obj = await CRUDBase(Project, self.auth, self.db).update(pid, data.model_dump(exclude_unset=True))
        return ProjectSchema.model_validate(obj).model_dump()

    async def delete_project(self, ids: list):
        await CRUDBase(Project, self.auth, self.db).delete(ids)
        return True

    # ---------- 购买 / 核销 ----------
    async def purchase(self, data: PurchaseCreateSchema):
        project = (await self.db.execute(
            select(Project).where(Project.id == data.project_id, Project.deleted_at.is_(None))
        )).scalars().first()
        if not project:
            raise CustomException(msg="项目不存在")
        # 计算折后单价
        unit_price = float(project.price or 0)
        if project.participate_member_discount:
            discount = await self._patient_discount(data.patient_id)
            unit_price = round(unit_price * discount, 2)
        total = round(unit_price * data.quantity, 2)

        remaining = None
        start_date = end_date = None
        if project.service_type == "count":
            remaining = (project.service_count or 1) * data.quantity
        else:
            if project.period_type == "year":
                start_date = date.today()
                end_date = start_date + timedelta(days=365)
            elif project.period_type == "month":
                start_date = date.today()
                end_date = start_date + timedelta(days=30)
            else:
                start_date = project.period_start
                end_date = project.period_end

        pp = PatientProject(
            patient_id=str(data.patient_id),
            project_id=str(project.id),
            project_name=project.name,
            quantity=data.quantity,
            unit_price=unit_price,
            total_amount=total,
            remaining_count=remaining,
            start_date=start_date,
            end_date=end_date,
            status="active",
            tenant_id=self.auth.tenant_id,
        )
        self.db.add(pp)
        await self.db.flush()
        await self.db.commit()
        return {"id": str(pp.id), "unit_price": unit_price, "total_amount": total, "remaining_count": remaining}

    async def my_services(self, patient_id: str):
        rows = (await self.db.execute(
            select(PatientProject).where(
                PatientProject.patient_id == str(patient_id),
                PatientProject.deleted_at.is_(None),
            ).order_by(PatientProject.created_at.desc())
        )).scalars().all()
        return [{**r.__dict__, "id": str(r.id)} for r in rows]

    async def verify(self, data: VerificationCreateSchema):
        pp = (await self.db.execute(
            select(PatientProject).where(PatientProject.id == data.patient_project_id, PatientProject.deleted_at.is_(None))
        )).scalars().first()
        if not pp:
            raise CustomException(msg="购买记录不存在")
        project = (await self.db.execute(
            select(Project).where(Project.id == pp.project_id, Project.deleted_at.is_(None))
        )).scalars().first()

        verify_amount = 0.0
        if project and project.service_type == "count":
            if (pp.remaining_count or 0) <= 0:
                raise CustomException(msg="剩余服务次数不足，无法核销")
            pp.remaining_count -= 1
            verify_amount = round(float(project.service_fee or 0) / max(project.service_count or 1, 1), 2)
            if pp.remaining_count <= 0:
                pp.status = "completed"

        v = ProjectVerification(
            patient_project_id=str(pp.id),
            project_id=str(pp.project_id),
            patient_id=str(pp.patient_id),
            technician_id=str(data.technician_id) if data.technician_id else None,
            verify_amount=verify_amount,
            tenant_id=self.auth.tenant_id,
        )
        self.db.add(v)
        await self.db.flush()
        await self.db.commit()
        return {"remaining_count": pp.remaining_count, "verify_amount": verify_amount}

    async def _patient_discount(self, patient_id) -> float:
        patient = (await self.db.execute(
            select(Patient).where(Patient.id == patient_id, Patient.deleted_at.is_(None))
        )).scalars().first()
        if not patient or not patient.member_level_id:
            return 1.0
        level = (await self.db.execute(
            select(MemberLevel).where(MemberLevel.id == patient.member_level_id)
        )).scalars().first()
        return float(level.discount_rate) if level else 1.0
