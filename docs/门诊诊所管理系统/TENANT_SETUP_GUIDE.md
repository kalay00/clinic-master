# 多租户设置指南

## 一、多租户设置方式

### 1.1 创建租户

租户可以通过以下方式创建：

#### 方式1：通过数据库初始化脚本（测试环境）

```bash
cd /home/laknl/his/backend
python3 -m app.core.init_test_data
```

#### 方式2：通过API创建（需要平台管理员）

```bash
POST /api/v1/platform/tenants
{
    "name": "测试门诊三",
    "code": "TEST003",
    "type": "clinic",
    "domain": "test003.his.example.com",
    "contact_name": "王五",
    "contact_phone": "13800138003",
    "contact_email": "test3@example.com",
    "address": "广州市天河区测试路3号"
}
```

#### 方式3：直接操作数据库

```sql
INSERT INTO tenants (name, code, type, domain, status, created_at, updated_at)
VALUES ('测试门诊三', 'TEST003', 'clinic', 'test003.his.example.com', 'active', NOW(), NOW());
```

### 1.2 租户字段说明

| 字段 | 说明 | 必填 | 示例 |
|------|------|------|------|
| name | 机构名称 | 是 | 测试门诊一 |
| code | 机构编码（唯一） | 是 | TEST001 |
| type | 机构类型 | 是 | clinic/hospital |
| domain | 租户域名 | 否 | test001.his.example.com |
| status | 状态 | 是 | active/inactive |
| subscription_plan | 订阅计划 | 否 | premium/standard |

## 二、用户如何选择租户

### 2.1 方式一：域名识别（推荐）

**适用场景**：生产环境，已配置DNS和子域名

**实现方式**：
1. 为每个租户配置子域名，如：`test001.his.example.com`
2. 用户在浏览器中访问该域名
3. 系统自动从域名提取租户代码，识别租户

**配置步骤**：

1. **DNS配置**
   ```
   *.his.example.com  A  记录指向服务器IP
   ```

2. **Nginx配置**（示例）
   ```nginx
   server {
       listen 80;
       server_name *.his.example.com;
       
       # 提取子域名
       set $tenant_code $host;
       if ($host ~ ^([^.]+)\.his\.example\.com$) {
           set $tenant_code $1;
       }
       
       location / {
           proxy_pass http://backend:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Tenant-Code $tenant_code;
       }
   }
   ```

3. **用户访问**
   - 访问：`http://test001.his.example.com`
   - 系统自动识别租户代码：`TEST001`

### 2.2 方式二：租户代码输入

**适用场景**：开发测试环境，无法配置子域名

**实现方式**：
1. 登录界面显示"租户代码"输入框
2. 用户输入租户代码（如：TEST001）
3. 系统根据代码查找租户

**登录示例**：
```json
POST /api/v1/auth/login
{
    "username": "admin1",
    "password": "111111",
    "tenant_code": "TEST001"
}
```

### 2.3 方式三：租户选择界面

**适用场景**：用户属于多个租户

**实现方式**：
1. 用户登录时只输入用户名和密码
2. 系统查找用户所属的所有租户
3. 如果用户只属于一个租户，直接进入
4. 如果用户属于多个租户，显示租户选择界面

**API调用**：
```json
POST /api/v1/auth/login
{
    "username": "admin",
    "password": "111111"
}

# 响应
{
    "code": 200,
    "data": {
        "tenants": [
            {"id": "uuid1", "name": "测试门诊一", "code": "TEST001"},
            {"id": "uuid2", "name": "测试门诊二", "code": "TEST002"}
        ]
    }
}

# 然后选择租户
POST /api/v1/auth/switch-tenant
{
    "tenant_id": "uuid1"
}
```

## 三、域名配置

### 3.1 域名格式

- **主域名**：`his.example.com`（平台管理）
- **租户子域名**：`{code}.his.example.com`
  - 例如：`test001.his.example.com`
  - 例如：`test002.his.example.com`

### 3.2 配置步骤

1. **DNS配置**
   - 添加通配符A记录：`*.his.example.com` -> 服务器IP
   - 或为每个租户单独配置：`test001.his.example.com` -> 服务器IP

2. **SSL证书**
   - 使用通配符证书：`*.his.example.com`
   - 或使用Let's Encrypt自动申请

3. **Web服务器配置**
   - Nginx/Apache配置子域名代理
   - 提取子域名并传递给后端

### 3.3 开发环境配置

开发环境可以使用hosts文件模拟：

**Windows (C:\Windows\System32\drivers\etc\hosts)**:
```
127.0.0.1 test001.his.local
127.0.0.1 test002.his.local
127.0.0.1 his.local
```

**Linux/Mac (/etc/hosts)**:
```
127.0.0.1 test001.his.local
127.0.0.1 test002.his.local
127.0.0.1 his.local
```

然后访问：`http://test001.his.local:8000`

## 四、平台管理员

### 4.1 是否需要平台管理员？

**建议：需要**

平台管理员的作用：
- 统一管理所有租户
- 创建、编辑、删除租户
- 查看所有租户的统计数据
- 审计和监控
- 处理租户问题

### 4.2 平台管理员特点

- **不属于任何租户**：`tenant_id` 为 `NULL` 或特殊值（如 `platform`）
- **跨租户权限**：可以访问所有租户的数据
- **独立登录**：使用主域名登录 `his.example.com`
- **独立角色**：平台管理员角色，与租户内角色分离

### 4.3 平台管理员登录

```json
POST /api/v1/platform/login
{
    "username": "platform_admin",
    "password": "password"
}

# 响应
{
    "code": 200,
    "data": {
        "access_token": "...",
        "user": {
            "id": "uuid",
            "username": "platform_admin",
            "role": "platform_admin",
            "tenant_id": null  // 平台管理员没有tenant_id
        }
    }
}
```

### 4.4 创建平台管理员

```sql
-- 创建平台管理员表（如果不存在）
CREATE TABLE IF NOT EXISTS platform_admins (
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

-- 插入平台管理员（密码：111111）
INSERT INTO platform_admins (username, password_hash, real_name, email, status)
VALUES (
    'platform_admin',
    '$2b$12$...',  -- bcrypt哈希后的密码
    '平台管理员',
    'admin@his.example.com',
    'active'
);
```

## 五、最佳实践

### 5.1 租户选择优先级

1. **生产环境**：优先使用域名识别
2. **开发环境**：使用租户代码输入
3. **多租户用户**：使用租户选择界面

### 5.2 安全建议

1. **域名验证**：验证域名与租户的对应关系
2. **HTTPS**：使用SSL证书保护域名
3. **租户隔离**：所有查询自动添加tenant_id过滤
4. **平台管理员**：限制平台管理员的操作范围

### 5.3 性能优化

1. **缓存租户信息**：Redis缓存租户代码和域名的映射
2. **索引优化**：为tenant_id和code字段建立索引
3. **查询优化**：避免跨租户查询

## 六、常见问题

### Q1: 用户如何知道应该访问哪个域名？

**A**: 
- 系统管理员在创建租户时，告知用户租户域名
- 或在登录页面提供"根据租户代码查找域名"的功能

### Q2: 如果用户不知道租户代码怎么办？

**A**:
- 提供"忘记租户代码"功能，通过邮箱或手机号查找
- 或联系系统管理员

### Q3: 一个用户可以在多个租户中使用吗？

**A**: 
- 可以，但需要分别在每个租户中创建用户账号
- 或使用用户多租户关联表（需要额外开发）

### Q4: 平台管理员可以访问所有租户的数据吗？

**A**: 
- 可以，但需要特殊标记和权限验证
- 建议所有平台管理员操作记录审计日志

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  

