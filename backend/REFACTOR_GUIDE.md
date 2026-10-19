# 后端重构：对齐 FastapiAdmin 的 module_* 架构（已完成）

将 `outpatient-management-system` 后端从「扁平 api/services/repositories」重构为
**FastapiAdmin 风格的 `module_*/` 六文件结构**，并**完全对齐为 async + Python 3.12+**。

## 目标状态

- 运行环境：**Python 3.12+**（PEP 695 泛型 `class X[T]`、SQLAlchemy 2.0 风格）。
  > 注：本机验证使用的是 `/opt/homebrew/bin/python3.13`（与 3.12 语法完全兼容）。
- 数据库：**双会话**
  - 异步 `get_async_db()` / `AsyncSession`（新 `module_*` 模块使用，依赖注入传递 `AuthSchema`）
  - 同步 `get_db()` / `Session`（历史消费者 v2 API / 后台任务 / 脚本 / 测试 仍使用，避免一次性改造引发的雪崩）
- 统一响应：`app.common.response.SuccessResponse` / `ErrorResponse` / `ResponseSchema[T]`
- 统一异常：`app.core.exceptions.CustomException(msg, code, status_code)`
- 统一基类：`CRUDBase[Model, CreateSchema, UpdateSchema]`（自动租户隔离、软删除、审计、分页）
- 认证：`get_current_user` 依赖 → `AuthSchema`；路由级权限 `AuthPermission(permission=[...])`

## 目录结构（每个领域模块）

```
app/api/v1/module_<domain>/
├── controller.py   # HTTP 处理，FastAPI 路由 + AuthPermission + SuccessResponse
├── service.py      # 业务逻辑，依赖 AuthSchema，调用 CRUDBase
├── crud.py         # 数据层，CRUDBase 子类（每个 ORM 模型一个）
├── model.py        # 再导出 app.models.<x> 的 ORM 模型（单一数据源，避免重复建表）
├── schema.py       # Pydantic：<Model>Schema / <Model>CreateSchema / <Model>UpdateSchema
├── param.py        # <Domain>QueryParam（分页 + 公共过滤）
└── __init__.py     # 暴露 router
```

## 已迁移模块（20 个）

registration / treatment / payment / pharmacy / inventory / notification /
third_party_config / tenant / role / department / doctor / tcm / log /
print_template / platform / user / report / integration / upload
（以上由 `scripts/migrate_modules.py` 生成），外加手写参考模块 `module_patient`（含加密/解密逻辑）。

`auth` 仍沿用旧版（`/auth` 前缀，登录/令牌/刷新），未纳入 module 结构（核心认证基础设施，后续单独处理）。

原扁平文件 `app/api/v1/*.py`（registrations.py / treatments.py / … / users.py / patients.py）
已删除；其路由由对应 `module_*` 接管。

## 重新生成模块

```bash
python scripts/migrate_modules.py
```
该脚本通过 AST 解析 `app/models/<file>.py` 自动生成 schema/param，无需运行时依赖。

## 业务逻辑迁移状态（已完成）

所有 20 个 `module_*` 的 `service.py` 均已迁入业务领域逻辑（对齐旧 `app/services/*.py`，
改造为 async + `CRUDBase`，Python 3.12+）。其中 `module_patient` 为手写加密版本。

### 含核心领域逻辑的模块（已完整移植）
- **registration**：排班冲突、号源占用/释放、挂号自动建账单、取消退费。
- **payment**：账单金额重算、支付联动 registration 状态。
- **pharmacy**：库存扣减、近效期预警、发药联动 treatment 处方状态（药师审核开关读 `Tenant` 配置）。
- **inventory**：采购单/入库/盘点/退货单（退货扣库存并生成系统患者账单）。
- **treatment**：病历/处方（自动完成关联挂号、处方号生成）。
- **tcm**：中医诊断/四诊/治疗/处方/方剂/代煎全量异步化。
- **user**：用户名同租户唯一、角色分配/撤销、用户权限查询。
- **tenant**：配置默认/合并/校验、药师审核开关、按 code/domain 查询。
- **role**：角色权限分配/撤销/查询。
- **third_party_config**：敏感字段 AES 加密存储、按服务类型校验、配置解密。
- **platform**：跨租户管理（创建租户并自动建 admin 账号 + 分配 admin 角色）、平台统计、密码修改。
- **notification**：通知记录 CRUD + 短信/微信发送（优先租户配置，回退消息队列）。
- **report**：收入/就诊量/药品销售/每日/工作台/患者统计（无独立模型，直接用 `auth.db`）。
- **integration**：微信/支付宝/银联/医保支付对接、微信授权（无独立模型，直接用 `auth.db`）。

### 纯 CRUD 模块（生成骨架即等价旧逻辑，无需额外移植）
- **department / doctor / upload / log / print_template**：旧逻辑仅为 `system_repository` /
  `user_repository` 的 CRUD，已由 `CRUDBase` 覆盖，控制器端点已可用。

### 端点补充
`report`、`integration` 原为骨架控制器，已补齐业务端点；`tenant`/`user`/`role`/`platform`/
`notification` 在标准 CRUD 之外补充了配置、角色权限、跨租户管理、发送等业务端点。

### 注意
- 旧 `app/services/`、`app/repositories/`、`app/models/` 保留，供 v2 API / 后台任务继续使用（同步会话）。
- `route` 顺序：具体路径（如 `/tenant/pharmacist-review-enabled`）须注册在 `/{id}` 之前，
  否则会被路径参数抢匹配；`tenant` 控制器已按此顺序调整。
- 运行前需安装依赖（`fastapi`/`sqlalchemy`/`pydantic`/`bcrypt`/`pyjwt`/`cryptography` 等），
  本环境未预装，已通过 `py_compile` + 结构审查验证，尚未做运行时 import/OpenAPI 校验。

## 运行所需依赖（3.12+）

`requirements.txt` 已满足；额外确认 `cryptography`（加密模块依赖）与异步驱动
`asyncpg`（Postgres）/ `aiosqlite`（Sqlite）已安装。`pyproject.toml` 的
`requires-python` 已改为 `>=3.12`。
