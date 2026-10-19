# 前后端集成文档

## 一、API接口对接

### 1. API基础配置

**前端配置** (`frontend/js/app.js`):
```javascript
const APP_CONFIG = {
    API_BASE_URL: '/api/v1',
    TOKEN_KEY: 'his_token',
    USER_KEY: 'his_user',
    ...
};
```

**后端配置** (`backend/app/core/config.py`):
```python
API_V1_PREFIX: str = "/api/v1"
```

### 2. 认证流程

#### 登录流程
1. 前端发送登录请求：
```javascript
POST /api/v1/auth/login
{
    "username": "admin",
    "password": "password",
    "tenant_id": "default"
}
```

2. 后端返回：
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "access_token": "eyJ...",
        "refresh_token": "eyJ...",
        "user": {
            "id": "uuid",
            "username": "admin",
            "name": "管理员",
            "tenant_id": "default"
        }
    }
}
```

3. 前端保存token：
```javascript
localStorage.setItem('his_token', data.data.access_token);
localStorage.setItem('his_user', JSON.stringify(data.data.user));
```

#### Token刷新机制
- 前端API客户端会自动检测401错误
- 自动尝试刷新token
- 刷新失败则跳转到登录页

### 3. API路径映射

| 前端API调用 | 后端路由 | 说明 |
|------------|---------|------|
| `/auth/login` | `/api/v1/auth/login` | 用户登录 |
| `/auth/logout` | `/api/v1/auth/logout` | 用户登出 |
| `/auth/refresh` | `/api/v1/auth/refresh` | 刷新Token |
| `/patients` | `/api/v1/patients` | 患者列表 |
| `/registrations` | `/api/v1/registrations` | 挂号列表 |
| `/registrations/schedules` | `/api/v1/registrations/schedules` | 排班列表 |
| `/treatments/medical-records` | `/api/v1/treatments/medical-records` | 病历列表 |
| `/treatments/prescriptions` | `/api/v1/treatments/prescriptions` | 处方列表 |
| `/payments/bills` | `/api/v1/payments/bills` | 账单列表 |
| `/payments/payments` | `/api/v1/payments/payments` | 支付记录 |
| `/pharmacy/drugs` | `/api/v1/pharmacy/drugs` | 药品列表 |
| `/pharmacy/inventory/{id}` | `/api/v1/pharmacy/inventory/{id}` | 库存信息 |
| `/reports/revenue` | `/api/v1/reports/revenue` | 收入报表 |
| `/reports/visits` | `/api/v1/reports/visits` | 就诊量报表 |
| `/reports/daily` | `/api/v1/reports/daily` | 每日统计 |

## 二、响应格式统一

### 成功响应格式
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        // 具体数据
    }
}
```

### 分页响应格式
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "page_size": 20
    }
}
```

### 错误响应格式
```json
{
    "code": 400,
    "message": "错误信息",
    "details": {}
}
```

## 三、前端API封装

### API客户端 (`frontend/js/app.js`)
```javascript
class ApiClient {
    async request(url, options = {}) {
        // 自动添加Authorization头
        // 自动处理401错误和token刷新
        // 统一错误处理
    }
}
```

### 业务API封装 (`frontend/js/api.js`)
- `AuthAPI` - 认证相关API
- `PatientAPI` - 患者管理API
- `RegistrationAPI` - 挂号管理API
- `TreatmentAPI` - 诊疗管理API
- `PaymentAPI` - 收费管理API
- `PharmacyAPI` - 药房管理API
- `ReportAPI` - 报表API
- `NotificationAPI` - 通知API
- `IntegrationAPI` - 对接服务API

## 四、静态文件服务

后端配置了静态文件服务，前端资源可以通过以下路径访问：
- `http://localhost:8000/` - 前端首页
- `http://localhost:8000/login.html` - 登录页
- `http://localhost:8000/index.html` - 主页面
- `http://localhost:8000/css/` - CSS文件
- `http://localhost:8000/js/` - JavaScript文件
- `http://localhost:8000/images/` - 图片文件

## 五、CORS配置

后端已配置CORS，允许跨域请求：
```python
CORS_ORIGINS: List[str] = ["*"]
```

## 六、错误处理

### 前端错误处理
1. 网络错误：显示"网络错误，请稍后重试"
2. 401错误：自动刷新token，失败则跳转登录页
3. 业务错误：显示后端返回的错误信息

### 后端错误处理
1. 统一异常处理：`BaseAppException`
2. 业务异常：返回具体的错误信息
3. 系统异常：返回"服务器内部错误"

## 七、数据格式

### 日期格式
- 前端发送：ISO 8601格式字符串（如：`2024-12-19`）
- 后端返回：ISO 8601格式字符串

### 金额格式
- 前端显示：`¥123.45`
- 后端存储：`Decimal`类型，返回`float`

### UUID格式
- 所有ID使用UUID格式（36字符）

## 八、待完善项

1. **登录tenant_id**：
   - 当前使用硬编码的`"default"`
   - 需要实现租户选择功能或从配置读取

2. **Token刷新机制**：
   - 已实现自动刷新，但需要测试refresh_token的正确性

3. **API文档**：
   - Swagger UI已配置：`http://localhost:8000/api/docs`
   - 需要补充完整的API文档说明

4. **错误提示优化**：
   - 前端错误提示需要更友好的UI展示
   - 需要统一的错误提示组件

5. **请求拦截器**：
   - 可以添加请求日志
   - 可以添加请求耗时统计
   - 可以添加请求重试机制

## 九、测试建议

1. **登录测试**：
   - 测试正确用户名密码登录
   - 测试错误用户名密码
   - 测试token过期后的刷新

2. **API调用测试**：
   - 测试各个业务模块的API调用
   - 测试分页查询
   - 测试错误处理

3. **跨域测试**：
   - 测试不同域名的访问
   - 测试CORS配置是否正确

4. **静态文件测试**：
   - 测试前端资源是否能正常加载
   - 测试路由是否正确

## 十、部署建议

### 开发环境
- 后端：`http://localhost:8000`
- 前端：通过后端静态文件服务访问

### 生产环境
- 建议使用Nginx作为反向代理
- 前端静态文件可以通过CDN加速
- API接口通过Nginx转发到后端服务

