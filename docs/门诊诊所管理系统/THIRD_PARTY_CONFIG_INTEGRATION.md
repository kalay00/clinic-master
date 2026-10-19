# 第三方服务配置前后端集成文档

## 一、概述

本文档描述第三方服务配置功能的前后端集成实现，支持租户管理员在管理后台配置阿里云短信、支付宝、微信支付、银联支付等第三方服务参数。

## 二、后端API

### 2.1 API端点

#### 获取所有配置
```
GET /api/v1/third-party/configs
```

**响应示例**:
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [
            {
                "id": "uuid",
                "tenant_id": "uuid",
                "service_type": "aliyun_sms",
                "service_name": "阿里云短信",
                "is_enabled": true,
                "config_data": {
                    "sign_name": "诊所名称",
                    "template_code": "SMS_123456"
                },
                "created_at": "2024-12-19T10:00:00Z",
                "updated_at": "2024-12-19T10:00:00Z"
            }
        ]
    }
}
```

#### 获取指定服务配置
```
GET /api/v1/third-party/configs/{service_type}
```

#### 保存配置
```
POST /api/v1/third-party/configs
Content-Type: application/json

{
    "service_type": "aliyun_sms",
    "config_data": {
        "access_key_id": "LTAI5t...",
        "access_key_secret": "xxx...",
        "sign_name": "诊所名称",
        "template_code": "SMS_123456",
        "region": "cn-hangzhou"
    },
    "is_enabled": true
}
```

#### 更新配置
```
PUT /api/v1/third-party/configs/{service_type}
```

#### 删除配置
```
DELETE /api/v1/third-party/configs/{service_type}
```

#### 测试配置
```
POST /api/v1/third-party/configs/{service_type}/test
Content-Type: application/json

{
    "test_params": {
        "phone": "13800138000",
        "message": "这是一条测试短信"
    }
}
```

### 2.2 服务类型

- `aliyun_sms`: 阿里云短信
- `alipay`: 支付宝
- `wechat_pay`: 微信支付
- `unionpay`: 银联支付

## 三、前端实现

### 3.1 API封装

位置: `frontend/js/api.js`

```javascript
const ThirdPartyConfigAPI = {
    async getList() {
        return await api.get('/third-party/configs');
    },
    
    async getConfig(serviceType) {
        return await api.get(`/third-party/configs/${serviceType}`);
    },
    
    async saveConfig(data) {
        return await api.post('/third-party/configs', data);
    },
    
    async updateConfig(serviceType, data) {
        return await api.put(`/third-party/configs/${serviceType}`, data);
    },
    
    async deleteConfig(serviceType) {
        return await api.delete(`/third-party/configs/${serviceType}`);
    },
    
    async testConfig(serviceType, testParams = {}) {
        return await api.post(`/third-party/configs/${serviceType}/test`, {
            test_params: testParams
        });
    }
};
```

### 3.2 前端页面

位置: `frontend/views/system/third-party-configs.html`

**功能**:
- 显示所有服务配置列表（卡片式布局）
- 支持添加/编辑配置
- 支持删除配置
- 支持测试配置
- 配置表单根据服务类型动态生成

**主要函数**:
- `loadConfigList()`: 加载配置列表
- `showConfigModal(serviceType)`: 显示配置表单
- `saveConfig()`: 保存配置
- `deleteConfig(serviceType)`: 删除配置
- `testConfig()`: 测试配置

### 3.3 配置表单字段定义

```javascript
const SERVICE_TYPES = {
    aliyun_sms: {
        name: '阿里云短信',
        fields: [
            { key: 'access_key_id', label: 'AccessKey ID', type: 'text', required: true, encrypted: true },
            { key: 'access_key_secret', label: 'AccessKey Secret', type: 'password', required: true, encrypted: true },
            { key: 'sign_name', label: '签名名称', type: 'text', required: true },
            { key: 'template_code', label: '模板代码', type: 'text', required: true },
            { key: 'region', label: '区域', type: 'text', required: false, value: 'cn-hangzhou' }
        ],
        testParams: {
            phone: { label: '测试手机号', type: 'text', required: true },
            message: { label: '测试消息', type: 'text', required: true }
        }
    },
    // ... 其他服务类型
};
```

## 四、集成流程

### 4.1 配置流程

1. **租户管理员登录系统**
2. **进入系统管理 -> 第三方服务配置**
3. **选择要配置的服务**（如：阿里云短信）
4. **填写配置参数**：
   - AccessKey ID（加密存储）
   - AccessKey Secret（加密存储）
   - 签名名称
   - 模板代码
   - 区域（可选）
5. **点击"测试配置"验证配置是否正确**
6. **保存配置**

### 4.2 使用流程

1. **系统自动读取租户配置**
2. **根据配置调用第三方服务**
3. **如果配置不存在或未启用，使用备用方案**（消息队列）

## 五、安全特性

### 5.1 数据加密

- 敏感字段（如AccessKey Secret、API密钥）使用AES-256-GCM加密存储
- 加密密钥从环境变量读取

### 5.2 权限控制

- 只有租户管理员可以配置
- 配置数据隔离（每个租户独立配置）

### 5.3 配置验证

- 保存前验证必填字段
- 提供测试接口验证配置有效性

## 六、错误处理

### 6.1 前端错误处理

- 使用统一的错误处理组件（ErrorHandler）
- 显示友好的错误提示
- 自动重试机制

### 6.2 后端错误处理

- 配置验证失败返回400错误
- 配置不存在返回404错误
- 服务调用失败记录日志并返回错误信息

## 七、测试

### 7.1 配置测试

1. 在配置表单中填写测试参数
2. 点击"测试配置"按钮
3. 系统调用第三方服务进行测试
4. 显示测试结果

### 7.2 集成测试

1. 配置完成后，在实际业务流程中使用
2. 验证短信发送、支付功能是否正常
3. 检查日志确认配置生效

## 八、注意事项

1. **敏感信息保护**: 配置中的敏感字段会被加密存储，修改时需要重新输入
2. **配置更新**: 更新配置后，需要重启相关服务或等待配置生效
3. **测试功能**: 建议在正式使用前先进行测试，确保配置正确
4. **备份配置**: 重要配置建议备份，避免丢失

## 九、后续扩展

1. **配置历史**: 记录配置变更历史
2. **配置模板**: 提供常用配置模板
3. **批量配置**: 支持批量配置多个服务
4. **配置验证规则**: 更详细的配置验证规则

