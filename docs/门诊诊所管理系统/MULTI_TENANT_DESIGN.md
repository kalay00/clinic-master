# 多租户架构设计文档

## 一、多租户概述

### 1.1 设计目标

- 支持多个机构（租户）独立使用系统
- 数据完全隔离，互不可见
- 灵活的租户选择机制
- 平台管理员统一管理所有租户

### 1.2 租户标识方式

系统支持以下三种租户选择方式：

1. **域名方式**（推荐）
   - 每个租户分配独立子域名：`{tenant_code}.his.example.com`
   - 自动根据域名识别租户

2. **租户代码方式**
   - 登录时输入租户代码（如：TEST001）
   - 系统根据租户代码查找租户

3. **租户选择界面**
   - 用户登录后，如果属于多个租户，显示租户选择界面
   - 用户选择要使用的租户

## 二、租户选择机制

### 2.1 域名方式（推荐）

#### 实现原理

1. **域名配置**
   - 主域名：`his.example.com`（平台管理）
   - 租户子域名：`{tenant_code}.his.example.com`
   - 例如：`test001.his.example.com`、`test002.his.example.com`

2. **域名解析**
   - 前端：从 `window.location.hostname` 提取子域名
   - 后端：从 `Host` Header 提取租户代码

3. **租户查找**
   - 根据租户代码（code字段）查找租户
   - 如果找不到，返回错误

#### 优势

- 用户体验好，无需输入租户代码
- SEO友好，每个租户独立域名
- 安全性高，域名隔离

#### 配置示例

```nginx
# Nginx配置示例
server {
    listen 80;
    server_name *.his.example.com;
    
    # 提取子域名作为租户代码
    set $tenant_code $host;
    if ($host ~ ^([^.]+)\.his\.example\.com$) {
        set $tenant_code $1;
    }
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Tenant-Code $tenant_code;
    }
}
```

### 2.2 租户代码方式

#### 实现原理

1. **登录界面**
   - 用户输入：用户名、密码、租户代码
   - 系统根据租户代码查找租户

2. **租户验证**
   - 验证租户是否存在且状态为active
   - 验证用户是否属于该租户

#### 适用场景

- 开发测试环境
- 无法配置子域名的环境
- 临时访问需求

### 2.3 租户选择界面

#### 实现原理

1. **用户登录**
   - 用户输入用户名和密码（不指定租户）
   - 系统查找用户所属的所有租户

2. **租户列表**
   - 如果用户只属于一个租户，直接进入
   - 如果用户属于多个租户，显示选择界面

3. **租户切换**
   - 用户可以在系统中切换租户（需要重新生成Token）

## 三、平台管理员

### 3.1 角色定义

**平台管理员（Platform Admin）**：
- 跨租户管理角色
- 不属于任何具体租户（tenant_id为NULL）
- 可以管理所有租户
- 可以查看所有租户的数据（用于审计）

### 3.2 平台管理员权限

- 创建、编辑、删除租户
- 查看所有租户的统计数据
- 管理租户的订阅和配置
- 审计所有租户的操作日志
- 重置租户管理员密码

### 3.3 平台管理员登录

- 使用主域名登录：`his.example.com`
- 不需要指定租户代码
- Token中 `tenant_id` 为 `null` 或特殊值（如 `platform`）

## 四、数据模型设计

### 4.1 租户表扩展

```sql
ALTER TABLE tenants ADD COLUMN domain VARCHAR(100);  -- 租户域名
ALTER TABLE tenants ADD COLUMN platform_admin_id UUID;  -- 平台管理员ID（如果租户有平台管理员）
```

### 4.2 用户表扩展

```sql
-- 用户可能属于多个租户（多对多关系）
CREATE TABLE user_tenants (
    user_id UUID NOT NULL REFERENCES users(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    is_primary BOOLEAN DEFAULT FALSE,  -- 是否为主要租户
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, tenant_id)
);
```

### 4.3 平台管理员表

```sql
CREATE TABLE platform_admins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

## 五、API设计

### 5.1 租户相关API

#### 5.1.1 根据域名获取租户

```
GET /api/v1/tenant/by-domain?domain={domain}
```

#### 5.1.2 根据代码获取租户

```
GET /api/v1/tenant/by-code?code={code}
```

#### 5.1.3 获取用户所属租户列表

```
GET /api/v1/auth/tenants
```

#### 5.1.4 切换租户

```
POST /api/v1/auth/switch-tenant
{
    "tenant_id": "uuid"
}
```

### 5.2 平台管理员API

#### 5.2.1 平台管理员登录

```
POST /api/v1/platform/login
{
    "username": "platform_admin",
    "password": "password"
}
```

#### 5.2.2 租户管理

```
GET /api/v1/platform/tenants          # 获取所有租户列表
POST /api/v1/platform/tenants         # 创建租户
PUT /api/v1/platform/tenants/{id}     # 更新租户
DELETE /api/v1/platform/tenants/{id}  # 删除租户
```

## 六、前端实现

### 6.1 登录页面

- 检测当前域名
- 如果是子域名，自动提取租户代码
- 如果是主域名，显示租户代码输入框
- 如果是平台管理域名，显示平台管理员登录

### 6.2 租户选择界面

- 如果用户属于多个租户，显示租户选择卡片
- 每个卡片显示：租户名称、租户代码、最后访问时间
- 用户点击选择租户

### 6.3 租户切换

- 在用户菜单中显示"切换租户"
- 显示用户所属的所有租户
- 选择租户后重新生成Token

## 七、安全考虑

### 7.1 租户隔离

- 所有查询自动添加 `tenant_id` 过滤
- 平台管理员可以跨租户查询（需要特殊标记）
- 防止租户ID伪造（验证Token中的tenant_id）

### 7.2 域名验证

- 验证域名与租户代码的对应关系
- 防止域名劫持（HTTPS证书验证）
- 验证租户状态（active/inactive）

### 7.3 平台管理员安全

- 平台管理员需要额外的权限验证
- 所有平台管理员操作记录审计日志
- 限制平台管理员的操作范围

## 八、部署建议

### 8.1 域名配置

```
主域名：his.example.com          -> 平台管理
租户1：test001.his.example.com   -> 租户TEST001
租户2：test002.his.example.com   -> 租户TEST002
```

### 8.2 DNS配置

```
*.his.example.com  A 记录指向服务器IP
```

### 8.3 SSL证书

- 使用通配符证书：`*.his.example.com`
- 或使用Let's Encrypt自动申请证书

## 九、实施步骤

### 阶段1：基础实现（当前）

1. ✅ 租户表设计
2. ✅ 多租户中间件
3. ✅ 数据隔离实现

### 阶段2：租户选择机制

1. ⏳ 域名提取逻辑
2. ⏳ 租户代码查找
3. ⏳ 登录界面优化

### 阶段3：平台管理员

1. ⏳ 平台管理员表设计
2. ⏳ 平台管理员API
3. ⏳ 平台管理界面

### 阶段4：高级功能

1. ⏳ 用户多租户支持
2. ⏳ 租户切换功能
3. ⏳ 租户选择界面

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  

