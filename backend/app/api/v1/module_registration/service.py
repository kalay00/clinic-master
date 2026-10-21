"""
挂号服务（对齐旧 services/registration_service.py，迁移为异步 + CRUDBase，Python 3.12+）

业务规则：
- 排班冲突校验（全天排班 vs 时段排班互斥）
- 挂号自动生成单号、号源占用/释放
- 挂号费 > 0 时自动创建 registration 账单
- 取消挂号自动退费（paid_amount 清零）并释放号源
"""
from __future__ import annotations
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import joinedload

from app.core.base_schema import AuthSchema, PageResultSchema
from app.core.exceptions import CustomException
from app.core.logger import logger
from app.api.v1.module_payment.model import Bill
from app.api.v1.module_patient.model import Patient
from app.utils.common import generate_id

from .model import Schedule, Registration
from .schema import (
    RegistrationSchema,
    RegistrationCreateSchema,
    RegistrationUpdateSchema,
    ScheduleSchema,
    ScheduleCreateSchema,
    ScheduleUpdateSchema,
)
from .crud import RegistrationCRUD, ScheduleCRUD


class RegistrationService:
    """挂号服务"""

    def __init__(self, auth: AuthSchema) -> None:
        self.auth = auth
        self.crud = RegistrationCRUD(Registration, auth=auth)
        self.schedule_crud = ScheduleCRUD(Schedule, auth=auth)

    # ── 工具 ──
    @property
    def _user_id(self) -> Optional[str]:
        user = self.auth.user if self.auth else None
        uid = getattr(user, "id", None) if user else None
        return str(uid) if uid is not None else None

    @property
    def _tenant_id(self) -> Optional[str]:
        return self.auth.tenant_id if self.auth else None

    @property
    def _db(self):
        return self.crud.db

    # ── 排班管理 ──
    _TIME_SLOT_TEXT = {
        "morning": "上午",
        "afternoon": "下午",
        "evening": "晚上",
        "full_day": "全天",
    }

    def _schedule_dict(self, s: Schedule) -> dict:
        """将排班 ORM 转为前端所需的富化字典（含医生/科室名、可用号源、时段中文）"""
        doctor = getattr(s, "doctor", None)
        department = getattr(s, "department", None)
        doctor_name = getattr(doctor, "name", "") if doctor else ""
        department_name = getattr(department, "name", "") if department else ""
        total_quota = s.total_quota or 0
        used_quota = s.used_quota or 0
        return {
            "id": str(s.id),
            "doctor_id": str(s.doctor_id) if s.doctor_id else None,
            "department_id": str(s.department_id) if s.department_id else None,
            "doctor_name": doctor_name,
            "department_name": department_name,
            "schedule_date": s.schedule_date.isoformat() if s.schedule_date else None,
            "time_slot": s.time_slot,
            "time_slot_text": self._TIME_SLOT_TEXT.get(s.time_slot, s.time_slot or ""),
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "end_time": s.end_time.isoformat() if s.end_time else None,
            "total_quota": total_quota,
            "used_quota": used_quota,
            "available_quota": total_quota - used_quota,
            "price": float(s.price) if s.price else 0.0,
            "status": s.status or "active",
        }

    async def _load_schedule(self, schedule_id: str) -> Schedule:
        """重新加载带 doctor/department 关系的排班对象。

        新建/更新/状态变更后直接对 ORM 对象调用 _schedule_dict 会访问未加载的
        doctor/department 关系，在 async 会话中触发 sqlalchemy.exc.MissingGreenlet。
        这里用 preload 重新查询，确保关系已加载。
        """
        return await self.schedule_crud.get_or_404(
            id=schedule_id, preload=["doctor", "department"]
        )

    async def create_schedule(
        self, schedule_data: ScheduleCreateSchema, creator_id: Optional[str] = None
    ) -> dict:
        """创建排班（含全天/时段冲突校验 + 默认挂号费回退）"""
        data = schedule_data.model_dump()
        doctor_id = data.get("doctor_id")
        schedule_date = data.get("schedule_date")
        time_slot = data.get("time_slot")

        if doctor_id and schedule_date:
            existing = await self._query_schedules(
                doctor_id=doctor_id, schedule_date=schedule_date
            )
            if time_slot == "full_day":
                if existing:
                    raise CustomException(
                        msg=f"该医生在{schedule_date}已有其他时间段排班，不能创建全天排班。请先删除其他时间段的排班。",
                        code=400,
                    )
            else:
                if any(s.time_slot == "full_day" for s in existing):
                    raise CustomException(
                        msg=f"该医生在{schedule_date}已有全天排班，不能创建其他时间段的排班。",
                        code=400,
                    )

        # 未设置挂号费时回退到医生默认挂号费
        price = data.get("price")
        if not price or Decimal(str(price)) <= 0:
            if doctor_id:
                try:
                    from app.api.v1.module_doctor.model import Doctor

                    res = await self._db.execute(
                        select(Doctor).where(
                            Doctor.id == doctor_id, Doctor.deleted_at.is_(None)
                        )
                    )
                    doctor = res.scalars().first()
                    if doctor and getattr(doctor, "registration_fee", None):
                        data["price"] = float(doctor.registration_fee)
                        logger.info(f"使用医生默认挂号费: {doctor.name}, 金额: {doctor.registration_fee}")
                except Exception as e:  # pragma: no cover
                    logger.warning(f"获取医生默认挂号费失败: {e!s}", exc_info=True)

        schedule = await self.schedule_crud.create(data)
        uid = creator_id or self._user_id
        if uid and hasattr(schedule, "created_by"):
            setattr(schedule, "created_by", uid)
            await self._db.flush()
        await self._db.commit()
        logger.info(f"创建排班: {schedule.id} by {uid}")
        schedule = await self._load_schedule(schedule.id)
        return self._schedule_dict(schedule)

    async def get_schedule(self, schedule_id: str) -> dict:
        schedule = await self.schedule_crud.get_or_404(
            id=schedule_id, preload=["doctor", "department"]
        )
        return self._schedule_dict(schedule)

    async def list_schedules(
        self,
        doctor_id: Optional[str] = None,
        department_id: Optional[str] = None,
        schedule_date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[dict], int]:
        schedules = await self._query_schedules(
            doctor_id=doctor_id,
            department_id=department_id,
            schedule_date=schedule_date,
            start_date=start_date,
            end_date=end_date,
        )
        total = len(schedules)
        page = schedules[skip : skip + limit]
        return [self._schedule_dict(s) for s in page], total

    async def update_schedule(
        self,
        schedule_id: str,
        schedule_data: ScheduleUpdateSchema,
        updater_id: Optional[str] = None,
    ) -> dict:
        data = schedule_data.model_dump(exclude_unset=True)
        schedule = await self.schedule_crud.get(id=schedule_id)
        if not schedule:
            raise CustomException(msg="排班不存在")

        doctor_id = data.get("doctor_id") or str(schedule.doctor_id)
        schedule_date = data.get("schedule_date") or schedule.schedule_date
        time_slot = data.get("time_slot") or schedule.time_slot

        if doctor_id and schedule_date:
            existing = await self._query_schedules(
                doctor_id=doctor_id, schedule_date=schedule_date
            )
            existing = [s for s in existing if str(s.id) != schedule_id]
            if time_slot == "full_day":
                if existing:
                    raise CustomException(
                        msg=f"该医生在{schedule_date}已有其他时间段排班，不能更新为全天排班。请先删除其他时间段的排班。",
                        code=400,
                    )
            else:
                if any(s.time_slot == "full_day" for s in existing):
                    raise CustomException(
                        msg=f"该医生在{schedule_date}已有全天排班，不能更新为其他时间段的排班。",
                        code=400,
                    )

        schedule = await self.schedule_crud.update(schedule_id, schedule_data)
        uid = updater_id or self._user_id
        if uid and hasattr(schedule, "updated_by"):
            setattr(schedule, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        logger.info(f"更新排班: {schedule_id} by {uid}")
        schedule = await self._load_schedule(schedule.id)
        return self._schedule_dict(schedule)

    async def pause_schedule(self, schedule_id: str) -> dict:
        """暂停挂号（status -> paused）"""
        schedule = await self.schedule_crud.get(id=schedule_id)
        if not schedule:
            raise CustomException(msg="排班不存在")
        schedule.status = "paused"
        await self._db.flush()
        await self._db.commit()
        logger.info(f"暂停排班: {schedule_id}")
        schedule = await self._load_schedule(schedule.id)
        return self._schedule_dict(schedule)

    async def resume_schedule(self, schedule_id: str) -> dict:
        """恢复挂号（status -> active）"""
        schedule = await self.schedule_crud.get(id=schedule_id)
        if not schedule:
            raise CustomException(msg="排班不存在")
        schedule.status = "active"
        await self._db.flush()
        await self._db.commit()
        logger.info(f"恢复排班: {schedule_id}")
        schedule = await self._load_schedule(schedule.id)
        return self._schedule_dict(schedule)

    async def swap_schedule(self, schedule_id: str, new_doctor_id: str) -> dict:
        """换班：更换排班医生，并联动更新科室"""
        schedule = await self.schedule_crud.get(id=schedule_id)
        if not schedule:
            raise CustomException(msg="排班不存在")
        schedule.doctor_id = new_doctor_id
        # 联动更新科室为医生的所属科室
        try:
            from app.api.v1.module_doctor.model import Doctor

            res = await self._db.execute(
                select(Doctor).where(Doctor.id == new_doctor_id, Doctor.deleted_at.is_(None))
            )
            doctor = res.scalars().first()
            if doctor and getattr(doctor, "department_id", None):
                schedule.department_id = doctor.department_id
        except Exception as e:  # pragma: no cover
            logger.warning(f"换班时获取医生科室失败: {e!s}", exc_info=True)
        await self._db.flush()
        await self._db.commit()
        logger.info(f"换班: {schedule_id} -> doctor {new_doctor_id}")
        schedule = await self._load_schedule(schedule.id)
        return self._schedule_dict(schedule)

    @staticmethod
    def _uuid_or_none(value) -> Optional[uuid.UUID]:
        """将合法 UUID 字符串转为 uuid.UUID，非法/空/'undefined'/'null' 等返回 None。

        前端未选择筛选时可能传入 'undefined'/'null'/空串，直接当 UUID 比较会触发
        asyncpg 的 invalid UUID 异常（500）。这里统一过滤，避免脏参数导致接口崩溃。
        """
        if not value or value in ("undefined", "null", "None", "none"):
            return None
        try:
            return uuid.UUID(str(value))
        except (ValueError, TypeError, AttributeError):
            return None

    async def _query_schedules(
        self,
        doctor_id: Optional[str] = None,
        department_id: Optional[str] = None,
        schedule_date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[Schedule]:
        stmt = (
            select(Schedule)
            .options(joinedload(Schedule.doctor), joinedload(Schedule.department))
            .where(Schedule.deleted_at.is_(None))
        )
        if self._tenant_id is not None:
            stmt = stmt.where(Schedule.tenant_id == self._tenant_id)
        doctor_uuid = self._uuid_or_none(doctor_id)
        if doctor_uuid:
            stmt = stmt.where(Schedule.doctor_id == doctor_uuid)
        department_uuid = self._uuid_or_none(department_id)
        if department_uuid:
            stmt = stmt.where(Schedule.department_id == department_uuid)
        if start_date and end_date:
            stmt = stmt.where(Schedule.schedule_date >= start_date, Schedule.schedule_date <= end_date)
        elif schedule_date:
            stmt = stmt.where(Schedule.schedule_date == schedule_date)
        stmt = stmt.order_by(Schedule.schedule_date.asc(), Schedule.start_time)
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    # ── 挂号管理 ──
    async def create(self, data: RegistrationCreateSchema) -> RegistrationSchema:
        """创建挂号（含号源占用 + 自动建账单）"""
        registration_data = data.model_dump(exclude_unset=True)
        registration_data.setdefault("registration_no", f"REG{generate_id()[:8].upper()}")

        doctor_id = registration_data.get("doctor_id")
        registration_date = registration_data.get("registration_date")
        schedule_id = registration_data.get("schedule_id")

        # 未指定排班但给了医生+日期：自动匹配可用排班
        if doctor_id and registration_date and not schedule_id:
            schedules = await self._query_schedules(
                doctor_id=doctor_id, schedule_date=registration_date
            )
            if not schedules:
                raise CustomException(msg="该医生在该日期没有排班，无法挂号。请先创建排班。", code=400)
            available = next(
                (s for s in schedules if s.status == "active" and s.used_quota < s.total_quota),
                None,
            )
            if not available:
                raise CustomException(
                    msg="该医生在该日期没有可用的排班（已暂停或号源已满），无法挂号。", code=400
                )
            registration_data["schedule_id"] = str(available.id)
            registration_data["doctor_id"] = str(available.doctor_id)
            if available.department_id:
                registration_data["department_id"] = str(available.department_id)
            if not registration_data.get("price"):
                registration_data["price"] = float(available.price) if available.price else 0.0

        # 号源校验 + 占用
        if registration_data.get("schedule_id"):
            schedule = await self.schedule_crud.get(id=registration_data["schedule_id"])
            if not schedule:
                raise CustomException(msg="排班不存在", code=400)
            if schedule.status != "active":
                raise CustomException(msg=f"排班状态为{schedule.status}，无法挂号", code=400)
            if schedule.used_quota >= schedule.total_quota:
                raise CustomException(msg="号源已满，无法挂号", code=400)
            schedule.used_quota += 1
            await self._db.flush()

        # 防重复挂号：同一患者同一排班（同一医生、同一时间段）不能重复挂号
        pid = registration_data.get("patient_id")
        sid = registration_data.get("schedule_id")
        if pid and sid:
            dup_stmt = select(Registration).where(
                Registration.tenant_id == self._tenant_id,
                Registration.patient_id == pid,
                Registration.schedule_id == sid,
                Registration.status != "cancelled",
                Registration.deleted_at.is_(None),
            )
            dup_res = await self._db.execute(dup_stmt)
            if dup_res.scalars().first():
                raise CustomException(
                    msg="该患者在同一医生、同一时间段已经挂过号，不能重复挂号。",
                    code=400,
                    status_code=400,
                )

        registration = await self.crud.create(registration_data)
        uid = self._user_id
        if uid and hasattr(registration, "created_by"):
            setattr(registration, "created_by", uid)
            await self._db.flush()

        # 挂号费 > 0 自动建账单
        price = float(registration.price) if registration.price else 0.0
        if price > 0:
            bill = Bill(
                tenant_id=self._tenant_id,
                bill_no=f"BILL{generate_id()[:8].upper()}",
                patient_id=registration.patient_id,
                registration_id=registration.id,
                bill_type="registration",
                total_amount=Decimal(str(price)),
                paid_amount=Decimal("0"),
                discount_amount=Decimal("0"),
                insurance_amount=Decimal("0"),
                status="unpaid",
            )
            self._db.add(bill)
            await self._db.flush()
            logger.info(f"自动创建挂号账单: {bill.id} for registration {registration.id}")

        await self._db.commit()
        logger.info(f"创建挂号: {registration.id} by {uid}")
        # commit 后对象属性过期，且 RegistrationSchema 含 patient/doctor/department/schedule
        # 嵌套字段，直接 model_validate 会触发懒加载导致 MissingGreenlet；用 get() 重新拉取并预加载关联。
        return await self.get(registration.id)

    def _registration_dict(self, reg: Registration) -> dict:
        """将挂号 ORM 转为富化字典（含患者/医生/科室名称，患者姓名）

        RegistrationSchema 未声明 patient/doctor/department 关联字段，因此
        page/get 直接 model_validate 会丢失这些展示用字段。这里在已预加载关联对象的
        基础上手工补齐。
        """
        data = RegistrationSchema.model_validate(reg).model_dump()
        patient = getattr(reg, "patient", None)
        doctor = getattr(reg, "doctor", None)
        department = getattr(reg, "department", None)

        # 患者姓名（明文）；档案号直接取
        patient_name = ""
        patient_no = None
        if patient:
            patient_no = getattr(patient, "patient_no", None)
            patient_name = patient.name or ""

        data["patient_name"] = patient_name
        data["patient_no"] = patient_no
        data["patient_phone"] = getattr(patient, "phone", "") if patient else ""
        data["doctor_name"] = getattr(doctor, "name", "") if doctor else ""
        data["department_name"] = getattr(department, "name", "") if department else ""

        # 预约时间：优先就诊时间，否则挂号日期
        visit = getattr(reg, "visit_time", None)
        if visit:
            appointment_time = visit.isoformat() if hasattr(visit, "isoformat") else str(visit)
        else:
            reg_date = getattr(reg, "registration_date", None)
            appointment_time = reg_date.isoformat() if reg_date and hasattr(reg_date, "isoformat") else None
        data["appointment_time"] = appointment_time
        return data

    async def get(self, id: str) -> dict:
        reg = await self.crud.get_or_404(
            id=id,
            preload=["patient", "doctor", "department", "schedule"],
        )
        return self._registration_dict(reg)

    async def list(
        self,
        page_no: int,
        page_size: int,
        order_by=None,
        search: Optional[dict] = None,
    ) -> PageResultSchema:
        search = dict(search or {})
        extra_conditions = []
        # 关键词：挂号单号模糊匹配 OR 患者档案号模糊匹配 OR 患者姓名精确哈希匹配
        keyword = search.pop("keyword", None)
        if keyword:
            kw = keyword.strip() if isinstance(keyword, str) else str(keyword).strip()
            if kw:
                patient_subq = (
                    select(Patient)
                    .where(
                        Patient.id == Registration.patient_id,
                        Patient.deleted_at.is_(None),
                        or_(
                            Patient.patient_no.like(f"%{kw}%"),
                            Patient.name.like(f"%{kw}%"),
                        ),
                    )
                    .exists()
                )
                extra_conditions.append(
                    or_(Registration.registration_no.like(f"%{kw}%"), patient_subq)
                )
        result = await self.crud.page(
            offset=(page_no - 1) * page_size,
            limit=page_size,
            order_by=order_by or [{"created_at": "desc"}],
            search=search,
            extra_conditions=extra_conditions,
            preload=["patient", "doctor", "department", "schedule"],
        )
        items = [self._registration_dict(obj) for obj in result.items]
        return PageResultSchema(
            page_no=result.page_no,
            page_size=result.page_size,
            total=result.total,
            has_next=result.has_next,
            items=items,
        )

    async def update(self, id: str, data: RegistrationUpdateSchema) -> RegistrationSchema:
        obj = await self.crud.update(id, data)
        uid = self._user_id
        if uid and hasattr(obj, "updated_by"):
            setattr(obj, "updated_by", uid)
            await self._db.flush()
        await self._db.commit()
        return await self.get(obj.id)

    async def delete(self, id: str) -> None:
        await self.crud.delete([id])

    async def cancel_registration(self, registration_id: str, canceller_id: Optional[str] = None) -> RegistrationSchema:
        """取消挂号：退费 + 释放号源"""
        registration = await self.crud.get(id=registration_id)
        if not registration:
            raise CustomException(msg="挂号不存在")
        if registration.status == "cancelled":
            raise CustomException(msg="挂号已取消", code=400)

        registration.status = "cancelled"
        paid_amount = float(registration.paid_amount) if registration.paid_amount else 0.0
        if paid_amount > 0:
            registration.paid_amount = Decimal("0")
            registration.payment_status = "refunded"
            logger.info(f"取消挂号自动退费: {registration_id}, 退费金额: {paid_amount}")

        if registration.schedule_id:
            schedule = await self.schedule_crud.get(id=str(registration.schedule_id))
            if schedule and schedule.used_quota > 0:
                schedule.used_quota -= 1
                await self._db.flush()

        await self._db.commit()
        logger.info(f"取消挂号: {registration_id} by {canceller_id or self._user_id}")
        return await self.get(registration.id)
