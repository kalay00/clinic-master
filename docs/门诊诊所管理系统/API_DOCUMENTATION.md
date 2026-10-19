# API接口文档

## 一、概述

本文档描述了门诊诊所管理系统所有API接口的详细信息。

### 基础信息

- **API版本**: v1
- **基础URL**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON
- **字符编码**: UTF-8

### 统一响应格式

#### 成功响应
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        // 具体数据
    },
    "timestamp": "2024-12-19T10:00:00"
}
```

#### 错误响应
```json
{
    "code": 400,
    "message": "错误信息",
    "data": {
        "details": {}
    },
    "timestamp": "2024-12-19T10:00:00"
}
```

#### 分页响应
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [...],
        "pagination": {
            "total": 100,
            "page": 1,
            "page_size": 20,
            "pages": 5
        }
    }
}
```

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（需要登录或令牌无效） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 二、认证接口

### 1. 用户登录

**接口**: `POST /api/v1/auth/login`

**描述**: 用户登录，验证用户名和密码，返回访问令牌和用户信息

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
    "username": "admin",
    "password": "password123",
    "tenant_id": "default"
}
```

**响应示例**:
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {
            "id": "uuid",
            "username": "admin",
            "real_name": "管理员",
            "email": "admin@example.com",
            "permissions": ["user:read", "user:write"]
        }
    }
}
```

**错误响应**:
```json
{
    "code": 401,
    "message": "用户名或密码错误"
}
```

### 2. 用户登出

**接口**: `POST /api/v1/auth/logout`

**描述**: 用户登出，清除服务器端的令牌缓存

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
    "code": 200,
    "message": "登出成功"
}
```

### 3. 刷新令牌

**接口**: `POST /api/v1/auth/refresh`

**描述**: 使用刷新令牌获取新的访问令牌

**请求体**:
```json
{
    "refresh_token": "eyJ..."
}
```

**响应示例**:
```json
{
    "code": 200,
    "message": "Token刷新成功",
    "data": {
        "access_token": "eyJ...",
        "refresh_token": "eyJ...",
        "token_type": "bearer"
    }
}
```

## 三、患者管理接口

### 1. 获取患者列表

**接口**: `GET /api/v1/patients`

**描述**: 获取患者列表，支持分页和搜索

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `skip` (int, 可选): 跳过的记录数，默认0
- `limit` (int, 可选): 每页记录数，默认100，最大1000
- `search` (string, 可选): 搜索关键词（姓名、身份证、电话）

**响应示例**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": "uuid",
                "name": "张三",
                "gender": "male",
                "birth_date": "1990-01-01",
                "id_card": "110101199001011234",
                "phone": "13800138000"
            }
        ],
        "pagination": {
            "total": 100,
            "page": 1,
            "page_size": 20,
            "pages": 5
        }
    }
}
```

### 2. 获取患者详情

**接口**: `GET /api/v1/patients/{id}`

**描述**: 根据ID获取患者详细信息

**路径参数**:
- `id` (string, 必需): 患者ID

**响应示例**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": "uuid",
        "name": "张三",
        "gender": "male",
        "birth_date": "1990-01-01",
        "id_card": "110101199001011234",
        "phone": "13800138000",
        "address": "北京市朝阳区",
        "allergies": "无",
        "medical_history": "无"
    }
}
```

### 3. 创建患者

**接口**: `POST /api/v1/patients`

**描述**: 创建新患者记录

**请求体**:
```json
{
    "name": "张三",
    "gender": "male",
    "birth_date": "1990-01-01",
    "id_card": "110101199001011234",
    "phone": "13800138000",
    "address": "北京市朝阳区",
    "allergies": "无",
    "medical_history": "无"
}
```

**响应示例**:
```json
{
    "code": 201,
    "message": "创建成功",
    "data": {
        "id": "uuid",
        "name": "张三"
    }
}
```

### 4. 更新患者

**接口**: `PUT /api/v1/patients/{id}`

**描述**: 更新患者信息

**路径参数**:
- `id` (string, 必需): 患者ID

**请求体**: 同创建患者，所有字段可选

### 5. 删除患者

**接口**: `DELETE /api/v1/patients/{id}`

**描述**: 删除患者记录（软删除）

**路径参数**:
- `id` (string, 必需): 患者ID

## 四、挂号管理接口

### 1. 获取排班列表

**接口**: `GET /api/v1/registrations/schedules`

**描述**: 获取医生排班列表

**查询参数**:
- `doctor_id` (string, 可选): 医生ID
- `department_id` (string, 可选): 科室ID
- `schedule_date` (string, 可选): 排班日期（YYYY-MM-DD）
- `skip` (int, 可选): 跳过的记录数
- `limit` (int, 可选): 每页记录数

### 2. 创建排班

**接口**: `POST /api/v1/registrations/schedules`

**描述**: 创建医生排班

**请求体**:
```json
{
    "doctor_id": "uuid",
    "department_id": "uuid",
    "schedule_date": "2024-12-20",
    "time_slot": "morning",
    "start_time": "09:00:00",
    "end_time": "12:00:00",
    "total_quota": 20,
    "price": 10.0
}
```

### 3. 获取挂号列表

**接口**: `GET /api/v1/registrations`

**描述**: 获取挂号列表

**查询参数**:
- `patient_id` (string, 可选): 患者ID
- `doctor_id` (string, 可选): 医生ID
- `registration_date` (string, 可选): 挂号日期
- `status` (string, 可选): 状态（pending, completed, cancelled）

### 4. 创建挂号

**接口**: `POST /api/v1/registrations`

**描述**: 创建挂号记录

**请求体**:
```json
{
    "patient_id": "uuid",
    "doctor_id": "uuid",
    "schedule_id": "uuid",
    "registration_date": "2024-12-20",
    "registration_type": "onsite",
    "price": 10.0
}
```

### 5. 取消挂号

**接口**: `POST /api/v1/registrations/{id}/cancel`

**描述**: 取消挂号，自动释放号源

## 五、诊疗管理接口

### 1. 获取病历列表

**接口**: `GET /api/v1/treatments/medical-records`

**描述**: 获取病历列表

**查询参数**:
- `patient_id` (string, 可选): 患者ID
- `doctor_id` (string, 可选): 医生ID
- `registration_id` (string, 可选): 挂号ID

### 2. 创建病历

**接口**: `POST /api/v1/treatments/medical-records`

**描述**: 创建病历记录

**请求体**:
```json
{
    "registration_id": "uuid",
    "patient_id": "uuid",
    "doctor_id": "uuid",
    "chief_complaint": "头痛",
    "present_illness": "患者自述头痛3天",
    "diagnosis": "偏头痛",
    "treatment_plan": "药物治疗"
}
```

### 3. 获取处方列表

**接口**: `GET /api/v1/treatments/prescriptions`

**描述**: 获取处方列表

### 4. 创建处方

**接口**: `POST /api/v1/treatments/prescriptions`

**描述**: 创建处方

**请求体**:
```json
{
    "medical_record_id": "uuid",
    "patient_id": "uuid",
    "doctor_id": "uuid",
    "prescription_type": "western",
    "items": [
        {
            "drug_id": "uuid",
            "quantity": 2,
            "dosage": "1片/次，3次/日",
            "price": 10.0
        }
    ],
    "total_amount": 20.0
}
```

## 六、收费管理接口

### 1. 获取账单列表

**接口**: `GET /api/v1/payments/bills`

**描述**: 获取账单列表

**查询参数**:
- `patient_id` (string, 可选): 患者ID
- `status` (string, 可选): 状态（pending, paid, refunded）
- `bill_type` (string, 可选): 账单类型

### 2. 创建账单

**接口**: `POST /api/v1/payments/bills`

**描述**: 创建账单

**请求体**:
```json
{
    "patient_id": "uuid",
    "registration_id": "uuid",
    "prescription_id": "uuid",
    "bill_type": "consultation",
    "items": [
        {
            "name": "挂号费",
            "amount": 10.0
        }
    ],
    "total_amount": 10.0,
    "discount_amount": 0.0,
    "insurance_amount": 0.0
}
```

### 3. 支付账单

**接口**: `POST /api/v1/payments/bills/{id}/pay`

**描述**: 支付账单

**请求体**:
```json
{
    "payment_method": "cash",
    "amount": 10.0,
    "transaction_id": "TXN123456"
}
```

**支付方式**:
- `cash`: 现金
- `wechat`: 微信支付
- `alipay`: 支付宝
- `medical_insurance`: 医保

### 4. 退费

**接口**: `POST /api/v1/payments/bills/{id}/refund`

**描述**: 退费

**请求体**:
```json
{
    "refund_amount": 10.0,
    "reason": "患者取消就诊"
}
```

## 七、药房管理接口

### 1. 获取药品列表

**接口**: `GET /api/v1/pharmacy/drugs`

**描述**: 获取药品列表

**查询参数**:
- `search` (string, 可选): 搜索关键词
- `category` (string, 可选): 药品分类

### 2. 创建药品

**接口**: `POST /api/v1/pharmacy/drugs`

**描述**: 创建药品记录

**请求体**:
```json
{
    "drug_code": "DRUG001",
    "name": "阿莫西林",
    "generic_name": "Amoxicillin",
    "specification": "0.25g*24片",
    "unit": "盒",
    "category": "antibiotic",
    "manufacturer": "XX制药",
    "price": 25.0
}
```

### 3. 获取库存

**接口**: `GET /api/v1/pharmacy/inventory/{drug_id}`

**描述**: 获取药品库存信息

### 4. 更新库存

**接口**: `POST /api/v1/pharmacy/inventory/{drug_id}`

**描述**: 更新库存（入库/出库）

**请求体**:
```json
{
    "quantity_change": 10
}
```

**说明**: `quantity_change`为正数表示入库，负数表示出库

### 5. 发药

**接口**: `POST /api/v1/pharmacy/dispense`

**描述**: 根据处方发药

**请求体**:
```json
{
    "prescription_id": "uuid",
    "items": [
        {
            "drug_id": "uuid",
            "quantity": 2
        }
    ]
}
```

## 八、报表统计接口

### 1. 收入报表

**接口**: `GET /api/v1/reports/revenue`

**描述**: 获取收入报表

**查询参数**:
- `start_date` (string, 可选): 开始日期（YYYY-MM-DD）
- `end_date` (string, 可选): 结束日期（YYYY-MM-DD）

**响应示例**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "total_revenue": 10000.0,
        "paid_revenue": 9500.0,
        "insurance_revenue": 500.0,
        "bill_count": 100
    }
}
```

### 2. 就诊量报表

**接口**: `GET /api/v1/reports/visits`

**描述**: 获取就诊量报表

### 3. 药品销售报表

**接口**: `GET /api/v1/reports/drugs`

**描述**: 获取药品销售报表

### 4. 每日统计

**接口**: `GET /api/v1/reports/daily`

**描述**: 获取每日统计数据

**查询参数**:
- `target_date` (string, 可选): 目标日期（YYYY-MM-DD），默认今天

## 九、错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（需要登录） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 十、注意事项

1. **认证**: 除登录接口外，所有接口都需要在请求头中携带JWT令牌
2. **多租户**: 系统支持多租户，每个请求会自动过滤租户数据
3. **分页**: 列表接口默认支持分页，建议每页不超过100条
4. **日期格式**: 所有日期使用ISO 8601格式（YYYY-MM-DD或YYYY-MM-DD HH:MM:SS）
5. **金额格式**: 金额使用浮点数，保留2位小数

## 十一、在线API文档

系统提供Swagger UI在线API文档：

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

访问在线文档可以查看完整的API定义、请求示例和响应示例，并可以直接测试API接口。

