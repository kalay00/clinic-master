# 第三方服务集成设计文档

## 一、概述

本文档描述第三方服务集成架构设计，支持租户管理员在管理后台自行配置各平台的接口参数。

## 二、设计目标

1. **租户可配置**: 每个租户可以独立配置自己的第三方服务参数
2. **多平台支持**: 支持阿里云短信、支付宝、微信、银联支付
3. **安全存储**: 敏感配置信息加密存储
4. **灵活扩展**: 易于添加新的第三方服务

## 三、架构设计

### 3.1 配置管理模型

#### 第三方服务配置表 (third_party_configs)

```sql
CREATE TABLE third_party_configs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    service_type VARCHAR(50) NOT NULL,  -- aliyun_sms, alipay, wechat_pay, unionpay
    service_name VARCHAR(100) NOT NULL,  -- 服务名称（如：阿里云短信）
    is_enabled BOOLEAN DEFAULT true,     -- 是否启用
    config_data JSONB NOT NULL,         -- 配置数据（加密存储）
    encrypted_fields TEXT[],             -- 需要加密的字段名列表
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    UNIQUE(tenant_id, service_type)
);
```

#### 配置数据示例

**阿里云短信配置**:
```json
{
    "access_key_id": "encrypted_value",
    "access_key_secret": "encrypted_value",
    "sign_name": "诊所名称",
    "template_code": "SMS_123456",
    "region": "cn-hangzhou"
}
```

**支付宝配置**:
```json
{
    "app_id": "2021001234567890",
    "app_private_key": "encrypted_value",
    "alipay_public_key": "encrypted_value",
    "sign_type": "RSA2",
    "gateway_url": "https://openapi.alipay.com/gateway.do"
}
```

**微信支付配置**:
```json
{
    "app_id": "wx1234567890",
    "mch_id": "1234567890",
    "api_key": "encrypted_value",
    "app_secret": "encrypted_value",
    "cert_path": "/path/to/cert.pem",
    "key_path": "/path/to/key.pem"
}
```

**银联支付配置**:
```json
{
    "mer_id": "1234567890",
    "mer_key": "encrypted_value",
    "gateway_url": "https://gateway.95516.com/gateway/api/order.do",
    "version": "5.1.0"
}
```

### 3.2 服务层设计

#### 配置管理服务 (ThirdPartyConfigService)

```python
class ThirdPartyConfigService:
    def get_config(tenant_id, service_type)
    def save_config(tenant_id, service_type, config_data)
    def encrypt_config(config_data, encrypted_fields)
    def decrypt_config(config_data, encrypted_fields)
    def validate_config(service_type, config_data)
```

#### 第三方服务适配器

```python
# 阿里云短信适配器
class AliyunSMSAdapter:
    def send_sms(phone, message, config)

# 支付宝适配器
class AlipayAdapter:
    def create_payment(order_info, config)
    def verify_callback(callback_data, config)

# 微信支付适配器
class WeChatPayAdapter:
    def create_payment(order_info, config)
    def verify_callback(callback_data, config)

# 银联支付适配器
class UnionPayAdapter:
    def create_payment(order_info, config)
    def verify_callback(callback_data, config)
```

### 3.3 API设计

#### 配置管理API

```
GET    /api/v1/third-party/configs              # 获取租户所有配置
GET    /api/v1/third-party/configs/{type}       # 获取指定服务配置
POST   /api/v1/third-party/configs              # 创建/更新配置
PUT    /api/v1/third-party/configs/{type}      # 更新配置
DELETE /api/v1/third-party/configs/{type}       # 删除配置
POST   /api/v1/third-party/configs/{type}/test  # 测试配置
```

## 四、实现方案

### 4.1 数据模型

创建 `app/models/third_party_config.py`

### 4.2 服务实现

1. 配置管理服务 (`app/services/third_party_config_service.py`)
2. 第三方服务适配器 (`app/services/third_party/`)
   - `aliyun_sms.py` - 阿里云短信
   - `alipay.py` - 支付宝
   - `wechat_pay.py` - 微信支付
   - `unionpay.py` - 银联支付

### 4.3 API实现

创建 `app/api/v1/third_party_configs.py`

### 4.4 前端界面

创建配置管理页面：
- `/views/system/third-party-configs.html` - 配置列表
- `/views/system/third-party-configs/form.html` - 配置表单

## 五、安全考虑

1. **敏感信息加密**: 使用AES-256-GCM加密存储敏感配置
2. **权限控制**: 只有租户管理员可以配置
3. **配置验证**: 保存前验证配置格式和必填项
4. **测试功能**: 提供测试接口验证配置是否正确

## 六、扩展性

1. **适配器模式**: 使用适配器模式，易于添加新服务
2. **配置模板**: 为每种服务类型提供配置模板
3. **验证规则**: 为每种服务类型定义验证规则

