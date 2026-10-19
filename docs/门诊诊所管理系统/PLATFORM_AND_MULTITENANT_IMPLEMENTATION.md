# 平台管理员和用户多租户支持实现文档

## 一、实现概述

本文档记录了平台管理员功能和用户多租户支持的完整实现。

### 1.1 实现内容

1. **平台管理员功能**
   - 平台管理员数据模型
   - 平台管理员服务
   - 平台管理员API（登录、租户管理）
   - 平台管理前端页面

2. **用户多租户支持**
   - 用户多租户关联表
   - 用户多租户服务
   - 租户选择API
   - 切换租户API
   - 租户选择前端界面
   - 登录流程支持多租户选择

## 二、数据模型

### 2.1 平台管理员表（platform_admins）

```sql
CREATE TABLE platform_admins (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);
```

### 2.2 用户租户关联表（user_tenants）

```sql
CREATE TABLE user_tenants (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    is_primary BOOLEAN DEFAULT FALSE,
    last_accessed_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id, tenant_id)
);
```

## 三、API接口

### 3.1 平台管理员API

#### 登录
```
POST /api/v1/platform/login
{
    "username": "platform_admin",
    "password": "111111"
}
```

#### 获取租户列表
```
GET /api/v1/platform/tenants?search=&status=&skip=0&limit=100
```

#### 创建租户
```
POST /api/v1/platform/tenants
{
    "name": "测试门诊三",
    "code": "TEST003",
    "type": "clinic",
    "domain": "test003.his.example.com",
    ...
}
```

#### 更新租户
```
PUT /api/v1/platform/tenants/{id}
{
    "name": "更新后的名称",
    ...
}
```

#### 删除租户
```
DELETE /api/v1/platform/tenants/{id}
```

### 3.2 用户多租户API

#### 获取用户所属租户列表
```
GET /api/v1/auth/tenants
```

#### 切换租户
```
POST /api/v1/auth/switch-tenant
{
    "tenant_id": "uuid"
}
```

#### 获取当前用户信息（包含租户列表）
```
GET /api/v1/auth/me
```

## 四、登录流程

### 4.1 单租户登录

1. 用户输入用户名、密码、租户代码（可选）
2. 系统根据租户代码或域名识别租户
3. 验证用户凭据
4. 生成Token，返回用户信息
5. 跳转到主页

### 4.2 多租户登录

1. 用户输入用户名、密码（不指定租户）
2. 系统验证用户名和密码
3. 查找用户所属的所有租户
4. 如果用户只属于一个租户：
   - 直接使用该租户登录
   - 生成Token，返回用户信息
5. 如果用户属于多个租户：
   - 返回租户列表
   - 跳转到租户选择页面
   - 用户选择租户后，调用切换租户API
   - 重新生成Token，跳转到主页

## 五、前端页面

### 5.1 租户选择页面

- 路径：`/views/auth/tenant-select.html`
- 功能：显示用户所属的所有租户，允许用户选择要登录的租户
- 特点：
  - 显示租户名称、代码、域名
  - 标记主要租户
  - 显示最后访问时间

### 5.2 平台管理页面

- 路径：`/views/platform/tenants.html`
- 功能：平台管理员管理所有租户
- 特点：
  - 租户列表展示
  - 搜索和筛选
  - 新增、编辑、删除租户
  - 分页显示

## 六、测试数据

### 6.1 平台管理员

- 用户名：`platform_admin`
- 密码：`111111`
- 邮箱：`platform@his.example.com`

### 6.2 多租户用户

- 用户：`admin1`（租户1的管理员）
- 该用户属于两个租户：
  - 主要租户：TEST001（测试门诊一）
  - 次要租户：TEST002（测试门诊二）

### 6.3 测试场景

1. **平台管理员登录**
   ```
   POST /api/v1/platform/login
   {
       "username": "platform_admin",
       "password": "111111"
   }
   ```

2. **多租户用户登录**
   ```
   POST /api/v1/auth/login
   {
       "username": "admin1",
       "password": "111111"
   }
   ```
   响应：返回租户列表，需要选择租户

3. **切换租户**
   ```
   POST /api/v1/auth/switch-tenant
   {
       "tenant_id": "租户2的ID"
   }
   ```

## 七、注意事项

### 7.1 用户多租户限制

- 用户在不同租户中需要分别有对应的账号和角色
- 用户多租户关联主要用于统一身份认证
- 实际业务数据仍按租户隔离

### 7.2 平台管理员权限

- 平台管理员不属于任何租户（tenant_id为"platform"）
- 可以跨租户查询数据
- 所有操作需要记录审计日志

### 7.3 安全性

- 平台管理员需要强密码策略
- 跨租户操作需要额外验证
- 所有敏感操作记录审计日志

## 八、后续优化

1. **用户多租户**
   - 支持用户在多个租户中共享同一套角色和权限
   - 支持租户间数据同步（可选）

2. **平台管理员**
   - 平台统计和监控
   - 审计日志查看
   - 租户订阅管理

3. **性能优化**
   - 租户信息缓存
   - 跨租户查询优化

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  

