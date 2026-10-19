"""
统一 CRUD 基类（对齐 FastapiAdmin: app.core.base_crud，Python 3.12+ / PEP 695）
- 软删除基于 deleted_at（而非 is_deleted/deleted_time）
- 租户隔离基于 tenant_id（UUID），有认证时自动追加 tenant_id 过滤
- 审计字段 created_by / updated_by（UUID）
- 支持有认证（Controller）与无认证（后台任务）两种场景
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from sqlalchemy import Select, asc, desc, false, func, select, update
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement

from app.core.base_model import MappedBase
from app.core.base_schema import AuthSchema, PageResultSchema
from app.core.exceptions import CustomException
from app.core.permission import Permission

try:
    from sqlalchemy.engine import Result
except ImportError:  # pragma: no cover
    Result = Any


class CRUDBase[ModelType: MappedBase, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel]:
    """统一数据层基类"""

    def __init__(
        self,
        model: type,
        auth: Optional[AuthSchema] = None,
        session: Optional[AsyncSession] = None,
    ) -> None:
        self.model = model
        self.auth = auth
        self.db = session if session is not None else (auth.db if auth else None)
        if self.db is None:
            raise RuntimeError("CRUDBase 未初始化数据库会话，请传入 auth 或 session 参数")

    # ── 内部工具 ──
    def _get_pk_col(self) -> ColumnElement:
        mapper = sa_inspect(self.model)
        pk_cols = list(getattr(mapper, "primary_key", []))
        if not pk_cols:
            raise CustomException(msg="模型缺少主键")
        if len(pk_cols) > 1:
            raise CustomException(msg="暂不支持复合主键操作")
        return pk_cols[0]

    @property
    def _supports_soft_delete(self) -> bool:
        return hasattr(self.model, "deleted_at")

    def _soft_delete_values(self) -> dict:
        data: dict = {"deleted_at": datetime.utcnow()}
        if self.auth and self.auth.user:
            user_id = getattr(self.auth.user, "id", None)
            if user_id is not None and hasattr(self.model, "updated_by"):
                data["updated_by"] = user_id
        return data

    async def _get_one(self, preload=None, **kwargs):
        conditions = await self.__build_conditions(**kwargs)
        sql = select(self.model).where(*conditions)
        for opt in self.__loader_options(preload):
            sql = sql.options(opt)
        sql = await self.__filter_permissions(sql)
        result = await self.db.execute(sql)
        return result.scalars().first()

    async def get(self, preload=None, **kwargs):
        try:
            return await self._get_one(preload=preload, **kwargs)
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(msg=f"查询失败: {e!s}")

    async def get_by_id(self, model_id: Any):
        return await self.get(id=model_id)

    async def get_or_404(self, id=None, msg="该数据不存在", preload=None, out_schema=None, **kwargs):
        if id is not None:
            kwargs["id"] = id
        obj = await self.get(preload=preload, **kwargs)
        if not obj:
            raise CustomException(msg=msg)
        return out_schema.model_validate(obj) if out_schema else obj

    async def exists(self, **kwargs) -> bool:
        return await self.get(**kwargs) is not None

    async def count(self, **kwargs) -> int:
        try:
            conditions = await self.__build_conditions(**kwargs)
            count_sql = select(func.count()).select_from(self.model).where(*conditions)
            count_sql = await self.__filter_permissions(count_sql)
            result = await self.db.execute(count_sql)
            return result.scalar() or 0
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(msg=f"统计失败: {e!s}")

    async def get_list(self, search=None, order_by=None, preload=None):
        try:
            conditions = await self.__build_conditions(**(search or {}))
            order = order_by or [{"created_at": "desc"}]
            sql = select(self.model).where(*conditions).order_by(*self._parse_order(order))
            for opt in self.__loader_options(preload):
                sql = sql.options(opt)
            sql = await self.__filter_permissions(sql)
            result = await self.db.execute(sql)
            return result.scalars().all()
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(msg=f"列表查询失败: {e!s}")

    async def page(self, offset, limit, order_by, search, out_schema=None, preload=None, extra_conditions=None) -> PageResultSchema:
        try:
            conditions = await self.__build_conditions(**(search or {}))
            if extra_conditions:
                conditions.extend(extra_conditions)
            order = order_by or [{"created_at": "desc"}]

            mapper = sa_inspect(self.model)
            pk_cols = list(getattr(mapper, "primary_key", []))
            pk = pk_cols[0] if pk_cols else func.count()

            data_sql = select(self.model).where(*conditions)
            for opt in self.__loader_options(preload):
                data_sql = data_sql.options(opt)
            data_sql = await self.__filter_permissions(data_sql)

            count_sql = select(func.count(pk)).select_from(self.model)
            where_clause = data_sql.whereclause
            if where_clause is not None:
                count_sql = count_sql.where(where_clause)

            total_result = await self.db.execute(count_sql)
            total = total_result.scalar() or 0

            result = await self.db.execute(
                data_sql.order_by(*self._parse_order(order)).offset(offset).limit(limit)
            )
            objs = result.scalars().all()
            items = (
                [out_schema.model_validate(obj).model_dump() for obj in objs]
                if out_schema
                else list(objs)
            )
            return PageResultSchema(
                page_no=offset // limit + 1 if limit else 1,
                page_size=limit or 10,
                total=total,
                has_next=offset + limit < total,
                items=items,
            )
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(msg=f"分页查询失败: {e!s}")

    async def create(self, data):
        try:
            obj_dict = data if isinstance(data, dict) else data.model_dump()
            obj = self.model(**obj_dict)
            if self.auth and self.auth.user:
                user_id = getattr(self.auth.user, "id", None)
                if hasattr(obj, "tenant_id") and getattr(obj, "tenant_id", None) is None:
                    if self.auth.tenant_id is not None:
                        setattr(obj, "tenant_id", self.auth.tenant_id)
                if hasattr(obj, "created_by") and user_id is not None:
                    setattr(obj, "created_by", user_id)
                if hasattr(obj, "updated_by") and user_id is not None:
                    setattr(obj, "updated_by", user_id)
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
            await self.db.commit()
            return obj
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(msg=f"创建失败: {e!s}")

    async def update(self, id: Any, data):
        try:
            obj_dict = data if isinstance(data, dict) else data.model_dump(exclude_unset=True, exclude={"id"})
            obj = await self._get_one(id=id)
            if not obj:
                raise CustomException(msg="更新对象不存在")
            if self.auth and self.auth.user:
                user_id = getattr(self.auth.user, "id", None)
                if hasattr(obj, "updated_by") and user_id is not None:
                    setattr(obj, "updated_by", user_id)
            for key, value in obj_dict.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            await self.db.flush()
            await self.db.refresh(obj)
            await self.db.commit()
            return obj
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(msg=f"更新失败: {e!s}")

    async def delete(self, ids: list) -> None:
        try:
            pk = self._get_pk_col()
            if self._supports_soft_delete:
                sql = update(self.model).where(pk.in_(ids)).values(**self._soft_delete_values())
            else:
                sql = update(self.model).where(pk.in_(ids))
            await self.db.execute(sql)
            await self.db.flush()
            await self.db.commit()
        except CustomException:
            raise
        except Exception as e:
            raise CustomException(msg=f"删除失败: {e!s}")

    async def __filter_permissions(self, sql: Select) -> Select:
        if not self.auth:
            return sql
        filter_obj = Permission(model=self.model, auth=self.auth)
        return await filter_obj.filter_query(sql)

    async def __build_conditions(self, **kwargs) -> list:
        conditions: list = []
        if hasattr(self.model, "deleted_at"):
            conditions.append(getattr(self.model, "deleted_at").is_(None))
        if self.auth and hasattr(self.model, "tenant_id") and self.auth.tenant_id is not None:
            conditions.append(getattr(self.model, "tenant_id") == self.auth.tenant_id)

        for key, value in kwargs.items():
            if value is None or value == "":
                continue
            attr = getattr(self.model, key)
            if isinstance(value, tuple):
                seq, val = value
                if seq == "None":
                    conditions.append(attr.is_(None))
                elif seq == "not None":
                    conditions.append(attr.isnot(None))
                elif seq == "like" and val:
                    conditions.append(attr.like(f"%{val}%"))
                elif seq == "in":
                    if isinstance(val, (list, tuple, set)) and len(val) == 0:
                        conditions.append(false())
                    else:
                        conditions.append(attr.in_(val))
                elif seq == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                    conditions.append(attr.between(val[0], val[1]))
                elif seq in ("!=", "ne") and val is not None:
                    conditions.append(attr != val)
                elif seq in (">", "gt") and val is not None:
                    conditions.append(attr > val)
                elif seq in (">=", "ge") and val is not None:
                    conditions.append(attr >= val)
                elif seq in ("<", "lt") and val is not None:
                    conditions.append(attr < val)
                elif seq in ("<=", "le") and val is not None:
                    conditions.append(attr <= val)
                elif seq in ("eq", "==") and val is not None:
                    conditions.append(attr == val)
            else:
                conditions.append(attr == value)
        return conditions

    def _parse_order(self, order: list) -> list:
        columns: list = []
        for item in order:
            for field, direction in item.items():
                column = getattr(self.model, field)
                columns.append(desc(column) if direction.lower() == "desc" else asc(column))
        return columns

    def __loader_options(self, preload=None) -> list:
        options: list = []
        if preload:
            for opt in preload:
                if isinstance(opt, str) and hasattr(self.model, opt):
                    options.append(selectinload(getattr(self.model, opt)))
                elif not isinstance(opt, str):
                    options.append(opt)
        return options
