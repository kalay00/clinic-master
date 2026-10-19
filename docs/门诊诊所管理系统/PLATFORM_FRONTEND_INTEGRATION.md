# 平台管理员前端集成文档

## 一、实现概述

本文档记录了平台管理员前端页面的创建和集成工作。

### 1.1 实现内容

1. **平台管理员登录页面**
   - 路径：`/platform-login.html`
   - 功能：平台管理员专用登录界面
   - 特点：独立登录流程，不与普通用户混用

2. **平台管理仪表板**
   - 路径：`/views/platform/dashboard.html`
   - 功能：平台管理主页面，显示统计信息
   - 特点：租户统计、最近租户列表、系统信息

3. **租户管理页面**
   - 路径：`/views/platform/tenants.html`
   - 功能：租户的CRUD操作
   - 特点：搜索、筛选、分页、新增/编辑/删除租户

4. **API集成**
   - 创建 `PlatformAPI` 对象
   - 集成所有平台管理相关API调用
   - 统一错误处理和响应格式

## 二、页面功能

### 2.1 平台管理员登录页面

#### 功能特点
- 独立的登录界面，区别于普通用户登录
- 平台管理员标识（Platform Admin Badge）
- 登录后跳转到平台管理仪表板
- 如果已登录，自动跳转到仪表板

#### 使用流程
1. 访问 `/platform-login.html`
2. 输入平台管理员用户名和密码
3. 调用 `/api/v1/platform/login` API
4. 保存Token和用户信息到localStorage
5. 跳转到 `/views/platform/dashboard.html`

#### 测试账号
- 用户名：`platform_admin`
- 密码：`111111`

### 2.2 平台管理仪表板

#### 功能特点
- **统计卡片**：总租户数、活跃租户数、总用户数、总患者数
- **最近租户**：显示最近创建的5个租户
- **系统信息**：平台版本、系统时间、最后登录时间
- **侧边栏导航**：仪表板、租户管理、平台统计、审计日志
- **用户信息**：显示当前登录的平台管理员信息

#### 数据加载
- 页面加载时自动调用 `PlatformAPI.getTenants()` 获取租户列表
- 计算统计数据并显示
- 按创建时间排序显示最近租户

### 2.3 租户管理页面

#### 功能特点
- **租户列表**：表格展示所有租户信息
- **搜索功能**：按租户名称或代码搜索
- **状态筛选**：按状态（启用/禁用）筛选
- **分页显示**：支持分页浏览
- **新增租户**：模态框创建新租户
- **编辑租户**：模态框编辑租户信息
- **删除租户**：软删除租户（需确认）

#### 租户字段
- 租户名称（必填）
- 租户代码（必填，唯一）
- 机构类型（门诊/医院）
- 租户域名（可选）
- 联系人信息（姓名、电话、邮箱）
- 地址
- 状态（启用/禁用）
- 订阅计划（标准版/高级版）

## 三、API集成

### 3.1 PlatformAPI 对象

```javascript
const PlatformAPI = {
    // 平台管理员登录
    async login(username, password),
    
    // 获取所有租户列表
    async getTenants(params),
    
    // 获取租户详情
    async getTenantDetail(id),
    
    // 创建租户
    async createTenant(data),
    
    // 更新租户
    async updateTenant(id, data),
    
    // 删除租户
    async deleteTenant(id),
    
    // 获取平台统计信息
    async getStatistics()
};
```

### 3.2 API调用示例

#### 登录
```javascript
const response = await PlatformAPI.login('platform_admin', '111111');
if (response.code === 200) {
    // 保存Token
    localStorage.setItem('his_token', response.data.access_token);
    // 跳转到仪表板
    window.location.href = '/views/platform/dashboard.html';
}
```

#### 获取租户列表
```javascript
const response = await PlatformAPI.getTenants({
    page: 1,
    page_size: 10,
    search: '测试',
    status: 'active'
});
```

#### 创建租户
```javascript
const response = await PlatformAPI.createTenant({
    name: '测试门诊三',
    code: 'TEST003',
    type: 'clinic',
    domain: 'test003.his.example.com',
    status: 'active'
});
```

## 四、路由配置

### 4.1 更新路由配置

在 `app.js` 中添加平台管理相关路由：

```javascript
const APP_CONFIG = {
    ROUTES: {
        platformLogin: '/platform-login.html',
        platformDashboard: '/views/platform/dashboard.html',
        platformTenants: '/views/platform/tenants.html',
        // ... 其他路由
    }
};
```

### 4.2 页面访问控制

所有平台管理页面都需要检查登录状态：

```javascript
// 检查登录状态
const token = localStorage.getItem('his_token');
const user = JSON.parse(localStorage.getItem('his_user') || '{}');

if (!token || user.role !== 'platform_admin') {
    window.location.href = '/platform-login.html';
}
```

## 五、UI设计

### 5.1 登录页面

- **渐变背景**：紫色渐变背景
- **卡片式设计**：白色卡片，圆角阴影
- **图标标识**：盾牌锁图标，Platform Admin标签
- **响应式设计**：适配不同屏幕尺寸

### 5.2 仪表板

- **侧边栏导航**：固定左侧，包含主要功能入口
- **统计卡片**：彩色边框，图标+数字展示
- **数据表格**：Bootstrap表格样式
- **实时时间**：显示当前系统时间

### 5.3 租户管理

- **搜索筛选区**：顶部搜索和筛选控件
- **数据表格**：响应式表格，支持操作按钮
- **模态框**：新增/编辑租户使用模态框
- **分页控件**：底部分页导航

## 六、安全考虑

### 6.1 登录验证

- 所有平台管理页面都需要验证登录状态
- 检查用户角色是否为 `platform_admin`
- 未登录或非平台管理员自动跳转到登录页

### 6.2 Token管理

- Token存储在localStorage
- API请求自动携带Token
- Token过期需要重新登录

### 6.3 权限控制

- 前端仅做UI控制
- 后端API需要验证平台管理员权限
- 所有敏感操作需要确认

## 七、测试

### 7.1 测试场景

1. **登录测试**
   - 使用平台管理员账号登录
   - 验证跳转到仪表板
   - 验证Token保存

2. **租户管理测试**
   - 创建新租户
   - 编辑租户信息
   - 删除租户（软删除）
   - 搜索和筛选租户

3. **权限测试**
   - 未登录访问平台管理页面
   - 普通用户访问平台管理页面
   - 验证跳转到登录页

### 7.2 测试数据

- 平台管理员：`platform_admin` / `111111`
- 测试租户：TEST001, TEST002

## 八、后续优化

1. **平台统计页面**
   - 详细的数据统计图表
   - 租户使用情况分析
   - 收入统计

2. **审计日志页面**
   - 平台管理员操作日志
   - 租户操作审计
   - 日志搜索和筛选

3. **租户管理增强**
   - 租户用户管理
   - 租户配置管理
   - 租户数据导出

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  

