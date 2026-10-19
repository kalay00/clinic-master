"""
患者控制器（对齐 FastapiAdmin: module_hospital/patient/controller.py）

路由契约与前端 PatientAPI 对齐（参考 module_treatment 标准 REST 范式）：
- 前缀 /patients（复数）
- GET  /            列表（skip / limit / search）
- GET  /{id}        详情
- POST /            创建
- PUT  /{id}        更新
- DELETE /{id}      删除
- GET  /by-id-card/{id_card}  按身份证号查询
"""
import math
from typing import Annotated, Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from fastapi.responses import JSONResponse

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import AuthPermission, get_current_user
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from .param import PatientQueryParam
from .schema import (
    FamilyMemberCreateSchema,
    FamilyMemberUpdateSchema,
    PatientCreateSchema,
    PatientRechargeSchema,
    PatientSchema,
    PatientUpdateSchema,
)
from .service import FamilyMemberService, PatientService


PatientRouter = APIRouter(
    route_class=OperationLogRoute,
    tags=["门诊管理", "患者管理"],
)


@PatientRouter.get(
    "",
    summary="查询患者列表",
)
async def get_patient_list_controller(
    auth: Annotated[AuthSchema, Depends(AuthPermission(["patient:list"]))],
    skip: Annotated[int, Query(ge=0, description="跳过数量")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="每页数量")] = 20,
    search: Annotated[Optional[str], Query(description="搜索关键词（姓名/身份证/电话/病历号）")] = None,
) -> JSONResponse:
    """查询患者列表（支持分页与关键词搜索）"""
    page_size = limit or 20
    page = (skip // page_size) + 1 if page_size else 1
    query_param = PatientQueryParam(search=search)
    result = await PatientService(auth).list_patients(query_param, page, page_size)

    total = getattr(result, "total", 0)
    page_no = getattr(result, "page_no", page)
    pages = math.ceil(total / page_size) if page_size else 0

    # 与前端 patients/list.html 期望结构对齐：{ items, pagination:{total,page,page_size,pages} }
    data = {
        "items": getattr(result, "items", []),
        "pagination": {
            "total": total,
            "page": page_no,
            "page_size": page_size,
            "pages": pages,
        },
    }
    return SuccessResponse(data=data, msg="查询患者列表成功")


@PatientRouter.get(
    "/{id}",
    summary="获取患者详情",
)
async def get_patient_detail_controller(
    id: Annotated[str, Path(description="患者ID")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["patient:get"]))],
) -> JSONResponse:
    """获取患者详情"""
    result = await PatientService(auth).get_patient(id)
    return SuccessResponse(data=result, msg="获取患者详情成功")


@PatientRouter.get(
    "/{id}/visits",
    summary="获取患者就诊历史",
)
async def get_patient_visits_controller(
    id: Annotated[str, Path(description="患者ID")],
    limit: Annotated[int, Query(ge=1, le=200, description="返回条数")] = 50,
    auth: Annotated[AuthSchema, Depends(AuthPermission(["patient:get"]))] = None,
) -> JSONResponse:
    """获取患者就诊历史（基于诊疗病历，预加载医生与科室）"""
    visits = await PatientService(auth).get_patient_visits(id, limit=limit)
    return SuccessResponse(data={"items": visits, "total": len(visits)}, msg="获取就诊历史成功")


@PatientRouter.post(
    "",
    summary="创建患者",
)
async def create_patient_controller(
    data: PatientCreateSchema,
    auth: Annotated[AuthSchema, Depends(AuthPermission(["patient:create"]))],
) -> JSONResponse:
    """创建患者"""
    result = await PatientService(auth).create_patient(data)
    return SuccessResponse(data=result, msg="创建患者成功")


@PatientRouter.put(
    "/{id}",
    summary="修改患者",
)
async def update_patient_controller(
    data: PatientUpdateSchema,
    id: Annotated[str, Path(description="患者ID")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["patient:update"]))],
) -> JSONResponse:
    """修改患者"""
    result = await PatientService(auth).update_patient(id, data)
    return SuccessResponse(data=result, msg="修改患者成功")


@PatientRouter.delete(
    "/{id}",
    summary="删除患者",
)
async def delete_patient_controller(
    id: Annotated[str, Path(description="患者ID")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["patient:delete"]))],
) -> JSONResponse:
    """删除患者"""
    await PatientService(auth).delete_patient(id)
    return SuccessResponse(msg="删除患者成功")


@PatientRouter.get(
    "/by-id-card/{id_card}",
    summary="根据身份证号查询患者",
)
async def get_patient_by_id_card_controller(
    id_card: Annotated[str, Path(description="身份证号")],
    auth: Annotated[AuthSchema, Depends(AuthPermission(["patient:get"]))],
) -> JSONResponse:
    """根据身份证号查询患者"""
    result = await PatientService(auth).get_patient_by_id_card(id_card)
    if not result:
        raise CustomException(msg="患者不存在", code=404, status_code=404)
    return SuccessResponse(data=result, msg="查询患者成功")


@PatientRouter.post("/{id}/recharge", summary="患者余额充值（含赠送）")
async def recharge_patient_controller(
    id: Annotated[str, Path(description="患者ID")],
    data: PatientRechargeSchema,
    auth: Annotated[AuthSchema, Depends(AuthPermission(["patient:update"]))],
) -> JSONResponse:
    """充值金额进入余额，并按系统设置比例赠送（充值赠送）。"""
    result = await PatientService(auth).recharge(id, data.amount, data.method, data.remark)
    return SuccessResponse(data=result, msg="充值成功")


@PatientRouter.get(
    "/{patient_id}/family-members",
    summary="家庭成员列表",
    dependencies=[Depends(AuthPermission(["patient:list"]))],
)
async def list_family_members_controller(
    patient_id: Annotated[str, Path(description="患者ID")],
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    page_size: Annotated[int, Query(ge=1, le=500, description="每页条数")] = 100,
    auth: AuthSchema = Depends(get_current_user),
) -> JSONResponse:
    """获取患者的家庭成员列表"""
    result = await FamilyMemberService(auth).list(patient_id, page, page_size)
    return SuccessResponse(data=result, msg="查询家庭成员成功")


@PatientRouter.post(
    "/{patient_id}/family-members",
    summary="添加家庭成员",
    dependencies=[Depends(AuthPermission(["patient:create"]))],
)
async def create_family_member_controller(
    patient_id: Annotated[str, Path(description="患者ID")],
    data: FamilyMemberCreateSchema,
    auth: AuthSchema = Depends(get_current_user),
) -> JSONResponse:
    """为患者添加家庭成员"""
    result = await FamilyMemberService(auth).create(patient_id, data)
    return SuccessResponse(data=result, msg="添加家庭成员成功")


@PatientRouter.put(
    "/{patient_id}/family-members/{member_id}",
    summary="更新家庭成员",
    dependencies=[Depends(AuthPermission(["patient:update"]))],
)
async def update_family_member_controller(
    patient_id: Annotated[str, Path(description="患者ID")],
    member_id: Annotated[str, Path(description="家庭成员ID")],
    data: FamilyMemberUpdateSchema,
    auth: AuthSchema = Depends(get_current_user),
) -> JSONResponse:
    """更新家庭成员信息"""
    result = await FamilyMemberService(auth).update(member_id, data)
    return SuccessResponse(data=result, msg="更新家庭成员成功")


@PatientRouter.delete(
    "/{patient_id}/family-members/{member_id}",
    summary="删除家庭成员",
    dependencies=[Depends(AuthPermission(["patient:delete"]))],
)
async def delete_family_member_controller(
    patient_id: Annotated[str, Path(description="患者ID")],
    member_id: Annotated[str, Path(description="家庭成员ID")],
    auth: AuthSchema = Depends(get_current_user),
) -> JSONResponse:
    """删除家庭成员"""
    await FamilyMemberService(auth).delete(member_id)
    return SuccessResponse(msg="删除家庭成员成功")
