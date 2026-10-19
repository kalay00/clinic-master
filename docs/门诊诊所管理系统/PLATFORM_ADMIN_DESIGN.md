# 平台管理员设计文档

## 一、平台管理员概述

### 1.1 定义

**平台管理员（Platform Admin）**是跨租户的管理角色，用于：
- 统一管理所有租户
- 创建、编辑、删除租户
- 查看所有租户的统计数据
- 审计和监控
- 处理租户问题

### 1.2 特点

- **不属于任何租户**：`tenant_id` 为 `NULL` 或特殊值（如 `platform`）
- **跨租户权限**：可以访问所有租户的数据
- **独立登录**：使用主域名登录 `his.example.com`
- **独立角色体系**：平台管理员角色与租户内角色分离

## 二、数据模型设计

### 2.1 平台管理员表

```sql
CREATE TABLE platform_admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',  -- active/inactive/locked
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_platform_admins_username ON platform_admins(username);
CREATE INDEX idx_platform_admins_status ON platform_admins(status);
```

### 2.2 平台管理员角色和权限

```sql
CREATE TABLE platform_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE platform_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    code VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE platform_admin_roles (
    admin_id UUID NOT NULL REFERENCES platform_admins(id),
    role_id UUID NOT NULL REFERENCES platform_roles(id),
    PRIMARY KEY (admin_id, role_id)
);

CREATE TABLE platform_role_permissions (
    role_id UUID NOT NULL REFERENCES platform_roles(id),
    permission_id UUID NOT NULL REFERENCES platform_permissions(id),
    PRIMARY KEY (role_id, permission_id)
);
```

## 三、API设计

### 3.1 平台管理员认证

#### 登录

```
POST /api/v1/platform/login
{
    "username": "platform_admin",
    "password": "password"
}

响应：
{
    "code": 200,
    "data": {
        "access_token": "...",
        "refresh_token": "...",
        "token_type": "bearer",
        "user": {
            "id": "uuid",
            "username": "platform_admin",
            "real_name": "平台管理员",
            "role": "platform_admin",
            "tenant_id": null  // 平台管理员没有tenant_id
        }
    }
}
```

#### 登出

```
POST /api/v1/platform/logout
```

### 3.2 租户管理

#### 获取所有租户列表

```
GET /api/v1/platform/tenants?skip=0&limit=100&search=&status=

响应：
{
    "code": 200,
    "data": {
        "items": [
            {
                "id": "uuid",
                "code": "TEST001",
                "name": "测试门诊一",
                "domain": "test001.his.example.com",
                "status": "active",
                "subscription_plan": "premium",
                "created_at": "2024-12-19T10:00:00Z",
                "user_count": 6,
                "patient_count": 5
            }
        ],
        "total": 2,
        "page": 1,
        "page_size": 100
    }
}
```

#### 创建租户

```
POST /api/v1/platform/tenants
{
    "name": "测试门诊三",
    "code": "TEST003",
    "type": "clinic",
    "domain": "test003.his.example.com",
    "contact_name": "王五",
    "contact_phone": "13800138003",
    "contact_email": "test3@example.com",
    "address": "广州市天河区测试路3号",
    "subscription_plan": "standard"
}
```

#### 更新租户

```
PUT /api/v1/platform/tenants/{id}
{
    "name": "测试门诊三（更新）",
    "status": "active",
    "subscription_plan": "premium"
}
```

#### 删除租户（软删除）

```
DELETE /api/v1/platform/tenants/{id}
```

#### 获取租户详情

```
GET /api/v1/platform/tenants/{id}
```

### 3.3 租户统计

#### 获取租户统计信息

```
GET /api/v1/platform/tenants/{id}/statistics

响应：
{
    "code": 200,
    "data": {
        "user_count": 6,
        "patient_count": 50,
        "registration_count": 200,
        "bill_count": 180,
        "total_revenue": 50000.00,
        "active_days": 30
    }
}
```

#### 获取所有租户统计

```
GET /api/v1/platform/statistics

响应：
{
    "code": 200,
    "data": {
        "total_tenants": 10,
        "active_tenants": 8,
        "total_users": 60,
        "total_patients": 500,
        "total_revenue": 500000.00
    }
}
```

## 四、权限控制

### 4.1 平台管理员权限

- **tenant:view** - 查看租户列表
- **tenant:create** - 创建租户
- **tenant:edit** - 编辑租户
- **tenant:delete** - 删除租户
- **tenant:view_data** - 查看租户数据（跨租户查询）
- **tenant:manage_users** - 管理租户用户
- **platform:statistics** - 查看平台统计
- **platform:audit** - 审计日志

### 4.2 跨租户查询

平台管理员查询时，需要特殊标记：

```python
# 平台管理员查询所有租户的患者
def get_all_patients(platform_admin_id: str):
    if is_platform_admin(platform_admin_id):
        # 不添加tenant_id过滤
        return db.query(Patient).filter(Patient.deleted_at.is_(None)).all()
    else:
        # 普通用户只能查询自己租户的数据
        return db.query(Patient).filter(
            Patient.tenant_id == tenant_id,
            Patient.deleted_at.is_(None)
        ).all()
```

## 五、前端实现

### 5.1 平台管理登录页面

- URL: `/platform/login.html`
- 主域名访问：`his.example.com`
- 只显示用户名和密码输入框
- 不需要租户代码

### 5.2 平台管理界面

- 租户列表
- 租户详情
- 租户统计
- 平台统计
- 审计日志

## 六、安全考虑

### 6.1 平台管理员安全

- 独立的认证体系
- 强密码策略
- 操作审计日志
- IP白名单（可选）
- 双因素认证（可选）

### 6.2 数据访问控制

- 平台管理员查询时明确标记
- 所有跨租户查询记录日志
- 限制平台管理员的操作范围
- 敏感操作需要二次确认

### 6.3 Token设计

平台管理员的Token中：
- `tenant_id`: `null` 或 `"platform"`
- `role`: `"platform_admin"`
- `permissions`: 平台管理员权限列表

## 七、实施建议

### 7.1 是否需要平台管理员？

**建议：需要**

原因：
1. 统一管理多个租户
2. 租户创建和配置
3. 平台级统计和监控
4. 问题处理和审计

### 7.2 实施优先级

1. **阶段1**：基础平台管理员（当前）
   - 平台管理员表
   - 平台管理员登录
   - 租户管理API

2. **阶段2**：平台管理界面
   - 租户列表界面
   - 租户详情界面
   - 平台统计界面

3. **阶段3**：高级功能
   - 审计日志
   - 租户监控
   - 自动化管理

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  

