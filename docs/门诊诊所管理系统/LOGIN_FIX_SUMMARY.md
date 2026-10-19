# 登录问题修复总结

## 问题描述

使用账号 `admin1`，密码 `111111` 登录时，提示"用户名或密码错误"。

## 根本原因

1. **数据库中没有测试用户**：测试数据（包括admin1用户）尚未初始化
2. **数据库表结构不完整**：部分表缺少 `created_by` 和 `updated_by` 字段
3. **关联表设计问题**：`role_permissions` 表继承了 `BaseModel`，但关联表不应该有这些字段

## 解决方案

### 1. 修复数据库表结构

需要添加缺失的字段到以下表：
- `roles` 表：添加 `created_by` 和 `updated_by` 字段

**执行命令**：
```sql
ALTER TABLE roles ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
ALTER TABLE roles ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id);
```

### 2. 初始化测试数据

运行初始化脚本创建测试用户：

```bash
cd backend
python3 -m app.core.init_test_data
```

**注意**：初始化脚本已经修复，支持：
- 检查租户是否已存在，避免重复创建
- 检查用户是否已存在，避免重复创建
- 检查角色是否已存在，避免重复创建

### 3. 登录方式

根据文档，`admin1` 用户属于租户 `TEST001`，登录时需要：

**方式1：使用租户代码**
- 用户名：`admin1`
- 密码：`111111`
- 租户代码：`TEST001`（在登录页面的租户代码输入框中填写）

**方式2：通过域名访问**
- 访问：`test001.his.example.com`（如果配置了域名）
- 用户名：`admin1`
- 密码：`111111`
- 系统会自动从域名识别租户代码

## 当前状态

- ✅ 已修复 `auth.py` 中 `User` 模型导入问题
- ✅ 已修复数据库表结构（添加 `roles.created_by` 和 `roles.updated_by`）
- ✅ 已修复初始化脚本，支持幂等性（可重复运行）
- ⚠️ 需要运行初始化脚本创建测试用户

## 下一步操作

1. **修复 `role_permissions` 表结构问题**（如果需要）
2. **运行初始化脚本**创建测试用户
3. **验证登录功能**

## 测试账号

根据文档，测试账号如下：

**租户1 (TEST001)**：
- `admin1` / `111111` - 系统管理员

**租户2 (TEST002)**：
- `admin2` / `111111` - 系统管理员

**平台管理员**：
- `platform_admin` / `111111` - 平台管理员

