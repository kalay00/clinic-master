#!/usr/bin/env python3.13
"""
模块迁移生成器（对齐 FastapiAdmin 的 module_*/ 六文件结构，Python 3.12+）

说明：
- 解析 app/models/<file>.py 中的 ORM 模型（Column / mapped_column 风格），
  据此生成 schema.py / param.py，避免运行时依赖（本项目未安装依赖，仅做 AST 解析）。
- 为每一个领域生成 module_<domain>/ 包：
    model.py    —— 从 app.models 再导出 ORM 模型（单一数据源，避免重复建表）
    schema.py   —— <Model>Schema / <Model>CreateSchema / <Model>UpdateSchema
    param.py    —— <Domain>QueryParam（分页 + 公共过滤）
    crud.py     —— 每个模型一个 CRUDBase 子类
    service.py  —— 标准 CRUD 服务（async + AuthSchema）
    controller.py —— 标准 CRUD 路由（SuccessResponse + AuthPermission）
    __init__.py —— 暴露 router
- 无独立 ORM 模型的模块（report / integration / upload）生成骨架包，业务逻辑待手写。

运行：python3.13 scripts/migrate_modules.py
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
MODELS_DIR = BACKEND / "app" / "models"
API_V1 = BACKEND / "app" / "api" / "v1"

SKIP_BASE = {"id", "tenant_id", "created_at", "updated_at", "deleted_at", "created_by", "updated_by"}

# sqlalchemy 列类型 -> (python 类型, 需要的 import 集合)
TYPE_MAP: dict[str, tuple[str, set[str]]] = {
    "UUID": ("str", set()),
    "String": ("str", set()),
    "Text": ("str", set()),
    "CHAR": ("str", set()),
    "Character": ("str", set()),
    "Integer": ("int", set()),
    "BigInteger": ("int", set()),
    "SmallInteger": ("int", set()),
    "Numeric": ("float", set()),
    "Float": ("float", set()),
    "DECIMAL": ("float", set()),
    "Decimal": ("float", set()),
    "Boolean": ("bool", set()),
    "DateTime": ("DateTimeStr", {"from app.core.validator import DateTimeStr"}),
    "Date": ("date", {"from datetime import date"}),
    "Time": ("time", {"from datetime import time"}),
    "JSON": ("Any", {"from typing import Any"}),
    "ARRAY": ("list", {"from typing import Any"}),
    "Enum": ("str", set()),
}

FILTER_COLS = ("name", "code", "status", "type")


def py_type(type_name: str) -> tuple[str, set[str]]:
    return TYPE_MAP.get(type_name, ("Any", {"from typing import Any"}))


def parse_model_file(path: Path) -> dict[str, list[dict]]:
    """返回 {class_name: [field, ...]}。field: name, pytype, nullable, has_default, pk, unique, comment"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: dict[str, list[dict]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        fields: list[dict] = []
        for stmt in node.body:
            targets = []
            value = None
            if isinstance(stmt, ast.Assign):
                targets = [t for t in stmt.targets if isinstance(t, ast.Name)]
                value = stmt.value
            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                targets = [stmt.target]
                value = stmt.value
            if not targets or value is None or not isinstance(value, ast.Call):
                continue
            func = value.func
            if isinstance(func, ast.Name) and func.id in ("Column", "mapped_column"):
                col_name = targets[0].id
                type_name = "Any"
                if value.args:
                    first = value.args[0]
                    if isinstance(first, ast.Call) and isinstance(first.func, ast.Name):
                        type_name = first.func.id
                    elif isinstance(first, ast.Name):
                        type_name = first.id
                nullable = True
                has_default = False
                pk = False
                unique = False
                comment = ""
                for kw in value.keywords:
                    if kw.arg == "nullable":
                        nullable = _const_bool(kw.value, True)
                    elif kw.arg == "default":
                        has_default = True
                    elif kw.arg == "primary_key":
                        pk = _const_bool(kw.value, False)
                    elif kw.arg == "unique":
                        unique = _const_bool(kw.value, False)
                    elif kw.arg == "comment" and isinstance(kw.value, ast.Constant):
                        comment = str(kw.value.value)
                pytype, _ = py_type(type_name)
                fields.append({
                    "name": col_name,
                    "pytype": pytype,
                    "nullable": nullable,
                    "has_default": has_default,
                    "pk": pk,
                    "unique": unique,
                    "comment": comment,
                })
        if fields:
            result[node.name] = fields
    return result


def _const_bool(node: ast.AST, default: bool) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return default


PYTYPE_IMPORT: dict[str, set[str]] = {
    "DateTimeStr": {"from app.core.validator import DateTimeStr"},
    "date": {"from datetime import date"},
    "time": {"from datetime import time"},
    "Any": {"from typing import Any"},
}


def gather_imports(classes: dict[str, list[dict]]) -> set[str]:
    imports: set[str] = set()
    for fields in classes.values():
        for f in fields:
            imports |= PYTYPE_IMPORT.get(f["pytype"], set())
    return imports


# ------------------------- 生成各文件 -------------------------

def gen_model(model_file: str | None, classes: list[str]) -> str:
    if not model_file:
        return '# 该模块无独立 ORM 模型，业务逻辑见 service.py / controller.py\n'
    cls_line = ", ".join(classes)
    return (
        f'"""\n模块 ORM 模型再导出（单一数据源：app.models.{model_file}）\n"""\n'
        f"from app.models.{model_file} import {cls_line}\n\n"
        f"__all__ = [{', '.join(repr(c) for c in classes)}]\n"
    )


def gen_schema(classes: dict[str, list[dict]]) -> str:
    imports = gather_imports(classes)
    import_lines = sorted(imports)
    head = (
        '"""\nPydantic 模型（对齐 FastapiAdmin: schema.py，Python 3.12+）\n"""\n'
        "from typing import Optional\n\n"
        "from pydantic import BaseModel, ConfigDict, Field\n\n"
    )
    if import_lines:
        head += "\n".join(import_lines) + "\n\n"
    out = [head]
    for cls, fields in classes.items():
        out.append(_gen_one_schema(cls, fields, "Schema", response=True))
        out.append(_gen_one_schema(cls, fields, "CreateSchema", response=False))
        out.append(_gen_one_schema(cls, fields, "UpdateSchema", response=False))
    return "\n".join(out)


def _gen_one_schema(cls: str, fields: list[dict], suffix: str, response: bool) -> str:
    name = f"{cls}{suffix}"
    lines = [f"class {name}(BaseModel):", f'    """{cls} {suffix}"""', ""]
    lines.append("    model_config = ConfigDict(from_attributes=True)")
    lines.append("")
    body = []
    for f in fields:
        required = (not f["nullable"]) and (not f["has_default"]) and (not f["pk"])
        if suffix == "CreateSchema" and f["name"] in SKIP_BASE:
            continue
        if suffix == "UpdateSchema" and f["name"] in SKIP_BASE:
            continue
        annotation = f["pytype"]
        comment_kw = f', comment="{f["comment"]}"' if f["comment"] else ""
        if response:
            if f["nullable"]:
                ann = f"Optional[{annotation}]"
                body.append(f"    {f['name']}: {ann} = Field(default=None{comment_kw})")
            else:
                body.append(f"    {f['name']}: {annotation} = Field(...{comment_kw})")
        else:
            if required:
                body.append(f"    {f['name']}: {annotation} = Field(...{comment_kw})")
            else:
                ann = f"Optional[{annotation}]"
                body.append(f"    {f['name']}: {ann} = Field(default=None{comment_kw})")
    if not body:
        body.append("    pass")
    lines.extend(body)
    return "\n".join(lines) + "\n\n"


def gen_param(domain: str, classes: dict[str, list[dict]]) -> str:
    # 用第一个类的字段决定是否生成常用过滤列
    Domain = domain[0].upper() + domain[1:]
    first = next(iter(classes.values()), [])
    available = {f["name"] for f in first}
    filters = [c for c in FILTER_COLS if c in available]
    lines = [
        '"""\n查询参数（对齐 FastapiAdmin: param.py，Python 3.12+）\n"""',
        "from dataclasses import dataclass",
        "from typing import Optional",
        "",
        "from fastapi import Query",
        "",
        "from app.core.base_params import PaginationQueryParam, BaseQueryParam",
        "",
        "",
        f"@dataclass",
        f"class {Domain}QueryParam(PaginationQueryParam, BaseQueryParam):",
        f'    """{Domain} 查询参数"""',
    ]
    if not filters:
        lines.append("    pass")
    else:
        for c in filters:
            cn = "名称" if c == "name" else ("编码" if c == "code" else ("状态" if c == "status" else "类型"))
            lines.append(f'    {c}: Optional[str] = Query(None, description="{cn}")')
    return "\n".join(lines) + "\n"


def gen_crud(domain: str, classes: dict[str, list[dict]]) -> str:
    cls_list = list(classes.keys())
    import_cls = ", ".join(cls_list)
    import_schema = ", ".join(f"{c}Schema, {c}CreateSchema, {c}UpdateSchema" for c in cls_list)
    head = (
        '"""\n数据层（对齐 FastapiAdmin: crud.py，Python 3.12+）\n"""\n'
        "from app.core.base_crud import CRUDBase\n"
        f"from .model import {import_cls}\n"
        f"from .schema import {import_schema}\n\n\n"
    )
    out = [head]
    for c in cls_list:
        out.append(
            f"class {c}CRUD(CRUDBase[{c}, {c}CreateSchema, {c}UpdateSchema]):\n"
            f'    """{c} 数据层"""\n\n'
            f"    pass\n\n"
        )
    return "\n".join(out)


def gen_service(domain: str, primary: str) -> str:
    Domain = domain[0].upper() + domain[1:]
    return (
        f'"""\n服务层（对齐 FastapiAdmin: service.py，Python 3.12+）\n"""\n'
        "from app.core.base_schema import AuthSchema\n"
        f"from .model import {primary}\n"
        f"from .schema import {primary}Schema, {primary}CreateSchema, {primary}UpdateSchema\n"
        f"from .crud import {primary}CRUD\n\n\n"
        f"class {Domain}Service:\n"
        f'    """{Domain} 服务"""\n\n'
        "    def __init__(self, auth: AuthSchema) -> None:\n"
        "        self.auth = auth\n"
        f"        self.crud = {primary}CRUD({primary}, auth=auth)\n\n"
        f"    async def get(self, id: str) -> {primary}Schema:\n"
        f"        return await self.crud.get_or_404(id=id, out_schema={primary}Schema)\n\n"
        "    async def list(self, page_no: int, page_size: int, order_by, search: dict | None):\n"
        "        return await self.crud.page(\n"
        "            offset=(page_no - 1) * page_size,\n"
        "            limit=page_size,\n"
        "            order_by=order_by or [{'created_at': 'desc'}],\n"
        "            search=search or {},\n"
        f"            out_schema={primary}Schema,\n"
        "        )\n\n"
        f"    async def create(self, data: {primary}CreateSchema) -> {primary}Schema:\n"
        "        obj = await self.crud.create(data)\n"
        f"        return {primary}Schema.model_validate(obj)\n\n"
        f"    async def update(self, id: str, data: {primary}UpdateSchema) -> {primary}Schema:\n"
        "        obj = await self.crud.update(id, data)\n"
        f"        return {primary}Schema.model_validate(obj)\n\n"
        "    async def delete(self, id: str) -> None:\n"
        "        await self.crud.delete([id])\n"
    )


def gen_controller(domain: str, primary: str, prefix: str, tag: str, perm: str) -> str:
    Domain = domain[0].upper() + domain[1:]
    return (
        f'"""\n控制器（对齐 FastapiAdmin: controller.py，Python 3.12+）\n"""\n'
        "from typing import Optional\n\n"
        "from fastapi import APIRouter, Depends, Query\n\n"
        "from app.common.response import SuccessResponse\n"
        "from app.core.base_schema import AuthSchema\n"
        "from app.core.dependencies import AuthPermission, get_current_user\n"
        "from app.core.exceptions import CustomException\n"
        f"from .model import {primary}\n"
        f"from .schema import {primary}Schema, {primary}CreateSchema, {primary}UpdateSchema\n"
        f"from .param import {Domain}QueryParam\n"
        f"from .service import {Domain}Service\n\n\n"
        "router = APIRouter()\n\n\n"
        f'@router.get("", summary="获取{tag}列表", dependencies=[Depends(AuthPermission(permission=["{perm}:list"]))])\n'
        "async def list_(\n"
        "    auth: AuthSchema = Depends(get_current_user),\n"
        "    page: int = Query(1, ge=1, description=\"页码\"),\n"
        "    page_size: int = Query(20, ge=1, le=100, description=\"每页数量\"),\n"
        "    order_by: Optional[str] = Query(None, description=\"排序\"),\n"
        "):\n"
        f"    params = {Domain}QueryParam(page_no=page, page_size=page_size, order_by=order_by)\n"
        f"    data = await {Domain}Service(auth).list(params.page_no, params.page_size, params.order_by, {{}})\n"
        "    return SuccessResponse(data=data, msg=\"查询成功\")\n\n\n"
        f'@router.post("", summary="创建{tag}", dependencies=[Depends(AuthPermission(permission=["{perm}:create"]))])\n'
        "async def create_(\n"
        f"    data: {primary}CreateSchema,\n"
        "    auth: AuthSchema = Depends(get_current_user),\n"
        "):\n"
        f"    result = await {Domain}Service(auth).create(data)\n"
        "    return SuccessResponse(data=result, msg=\"创建成功\")\n\n\n"
        f'@router.get("/{{id}}", summary="获取{tag}详情", dependencies=[Depends(AuthPermission(permission=["{perm}:get"]))])\n'
        "async def get_(\n"
        "    id: str,\n"
        "    auth: AuthSchema = Depends(get_current_user),\n"
        "):\n"
        f"    result = await {Domain}Service(auth).get(id)\n"
        "    return SuccessResponse(data=result, msg=\"查询成功\")\n\n\n"
        f'@router.put("/{{id}}", summary="更新{tag}", dependencies=[Depends(AuthPermission(permission=["{perm}:update"]))])\n'
        "async def update_(\n"
        "    id: str,\n"
        f"    data: {primary}UpdateSchema,\n"
        "    auth: AuthSchema = Depends(get_current_user),\n"
        "):\n"
        f"    result = await {Domain}Service(auth).update(id, data)\n"
        "    return SuccessResponse(data=result, msg=\"更新成功\")\n\n\n"
        f'@router.delete("/{{id}}", summary="删除{tag}", dependencies=[Depends(AuthPermission(permission=["{perm}:delete"]))])\n'
        "async def delete_(\n"
        "    id: str,\n"
        "    auth: AuthSchema = Depends(get_current_user),\n"
        "):\n"
        f"    await {Domain}Service(auth).delete(id)\n"
        '    return SuccessResponse(msg="删除成功")\n'
    )


def gen_thin_controller(domain: str, tag: str, perm: str) -> str:
    return (
        f'"""\n控制器（{tag}模块骨架，待迁移业务逻辑）\n"""\n'
        "from fastapi import APIRouter\n\n"
        "from app.common.response import SuccessResponse\n\n\n"
        "router = APIRouter()\n\n\n"
        f'@router.get("", summary="获取{tag}列表（骨架）")\n'
        "async def index():\n"
        '    return SuccessResponse(data=None, msg="该模块业务逻辑待手动迁移至 module 结构")\n'
    )


def gen_init() -> str:
    return "from .controller import router\n\n__all__ = ['router']\n"


# ------------------------- 模块配置 -------------------------

MODULES = [
    # dir, model_file, classes, primary, prefix, tag, perm
    ("module_registration", "registration", ["Schedule", "Registration"], "Registration", "/registrations", "挂号", "registration"),
    ("module_treatment", "treatment", ["MedicalRecord", "Prescription"], "MedicalRecord", "/treatments", "诊疗", "treatment"),
    ("module_payment", "payment", ["Bill", "Payment"], "Bill", "/payments", "收费", "payment"),
    ("module_pharmacy", "pharmacy", ["Drug", "Inventory", "Dispense"], "Drug", "/pharmacy", "药房", "pharmacy"),
    ("module_inventory", "inventory", ["Supplier", "PurchaseOrder", "PurchaseOrderItem", "InventoryTransaction", "InventoryCheck", "InventoryCheckItem"], "Supplier", "/inventory", "进销存", "inventory"),
    ("module_notification", "notification", ["Notification"], "Notification", "/notifications", "通知", "notification"),
    ("module_third_party_config", "third_party_config", ["ThirdPartyConfig"], "ThirdPartyConfig", "/third-party/configs", "第三方服务配置", "third_party_config"),
    ("module_tenant", "tenant", ["Tenant"], "Tenant", "/tenant", "租户配置", "tenant"),
    ("module_role", "user", ["Role", "Permission", "UserRole", "RolePermission"], "Role", "/roles", "角色", "role"),
    ("module_department", "system", ["Department", "Doctor"], "Department", "/departments", "科室", "department"),
    ("module_doctor", "system", ["Department", "Doctor"], "Doctor", "/doctors", "医生", "doctor"),
    ("module_tcm", "tcm", ["Diagnosis", "TCMDiagnosis", "TCMFourExaminations", "TCMTreatment", "TCMPrescription", "TCMPrescriptionItem", "TCMFormula", "TCMDecoctionService"], "TCMTreatment", "/tcm", "中医", "tcm"),
    ("module_log", "log", ["OperationLog"], "OperationLog", "/logs", "操作日志", "log"),
    ("module_print_template", "print_template", ["PrintTemplate"], "PrintTemplate", "/print-templates", "打印模板管理", "print_template"),
    ("module_platform", "platform_admin", ["PlatformAdmin"], "PlatformAdmin", "/platform", "平台管理", "platform"),
    ("module_user", "user", ["User", "Role", "Permission", "UserRole", "RolePermission"], "User", "/users", "用户", "user"),
    # 无独立 ORM 模型的模块（骨架）
    ("module_report", None, [], None, "/reports", "报表", "report"),
    ("module_integration", None, [], None, "/integrations", "对接", "integration"),
    ("module_upload", None, [], None, "/upload", "文件上传", "upload"),
]


def main() -> None:
    API_V1.mkdir(parents=True, exist_ok=True)
    for cfg in MODULES:
        dir_name, model_file, classes, primary, prefix, tag, perm = cfg
        mod_dir = API_V1 / dir_name
        mod_dir.mkdir(exist_ok=True)
        # model.py
        (mod_dir / "model.py").write_text(gen_model(model_file, classes), encoding="utf-8")
        if model_file:
            parsed = parse_model_file(MODELS_DIR / f"{model_file}.py")
            # 仅保留配置中声明的类
            parsed = {c: parsed.get(c, []) for c in classes}
            (mod_dir / "schema.py").write_text(gen_schema(parsed), encoding="utf-8")
            (mod_dir / "param.py").write_text(gen_param(dir_name.replace("module_", ""), parsed), encoding="utf-8")
            (mod_dir / "crud.py").write_text(gen_crud(dir_name.replace("module_", ""), parsed), encoding="utf-8")
            (mod_dir / "service.py").write_text(gen_service(dir_name.replace("module_", ""), primary), encoding="utf-8")
            (mod_dir / "controller.py").write_text(
                gen_controller(dir_name.replace("module_", ""), primary, prefix, tag, perm), encoding="utf-8"
            )
        else:
            (mod_dir / "schema.py").write_text('# 该模块无独立 ORM 模型\n')
            (mod_dir / "param.py").write_text('# 该模块无独立 ORM 模型\n')
            (mod_dir / "crud.py").write_text('# 该模块无独立 ORM 模型\n')
            (mod_dir / "service.py").write_text('# 该模块无独立 ORM 模型\n')
            (mod_dir / "controller.py").write_text(gen_thin_controller(dir_name.replace("module_", ""), tag, perm), encoding="utf-8")
        (mod_dir / "__init__.py").write_text(gen_init(), encoding="utf-8")
        print(f"generated: {dir_name}")


if __name__ == "__main__":
    main()
