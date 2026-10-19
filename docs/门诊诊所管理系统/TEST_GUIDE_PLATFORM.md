# 平台管理员功能测试指南

## 一、测试前准备

### 1.1 启动后端服务

```bash
cd /home/laknl/his/backend

# 激活虚拟环境（如果有）
source venv/bin/activate

# 安装依赖（如果未安装）
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 1.2 检查数据库

确保数据库已初始化，包含平台管理员账号：

```bash
cd /home/laknl/his/backend

# 初始化测试数据（如果未初始化）
python3 -m app.core.init_test_data
```

测试账号：
- 用户名: `platform_admin`
- 密码: `111111`

### 1.3 启动前端服务（可选）

如果使用静态文件服务器：

```bash
cd /home/laknl/his/frontend

# 使用Python简单服务器
python3 -m http.server 8080

# 或使用Nginx等Web服务器
```

## 二、自动化测试

### 2.1 运行快速测试脚本

```bash
cd /home/laknl/his

# 运行快速测试
bash tests/quick_test_platform.sh
```

该脚本会：
1. 检查后端服务状态
2. 测试平台管理员登录
3. 测试获取租户列表
4. 检查前端文件
5. 检查API定义

### 2.2 运行Python测试

```bash
cd /home/laknl/his

# 运行Python测试脚本
python3 tests/test_platform_admin.py
```

## 三、手动测试

### 3.1 后端API测试

#### 测试平台管理员登录

```bash
curl -X POST http://localhost:8000/api/v1/platform/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "platform_admin",
    "password": "111111"
  }'
```

预期响应：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "...",
    "refresh_token": "...",
    "token_type": "bearer",
    "user": {
      "id": "...",
      "username": "platform_admin",
      "role": "platform_admin",
      "tenant_id": null
    }
  }
}
```

#### 测试获取租户列表

```bash
# 先获取Token（从登录响应中）
TOKEN="your_access_token"

curl -X GET "http://localhost:8000/api/v1/platform/tenants?skip=0&limit=10" \
  -H "Authorization: Bearer ${TOKEN}"
```

#### 测试创建租户

```bash
curl -X POST http://localhost:8000/api/v1/platform/tenants \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试租户",
    "code": "TEST999",
    "type": "clinic",
    "domain": "test999.his.example.com",
    "status": "active",
    "subscription_plan": "standard"
  }'
```

#### 测试更新租户

```bash
curl -X PUT "http://localhost:8000/api/v1/platform/tenants/{tenant_id}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的名称",
    "status": "active"
  }'
```

#### 测试删除租户

```bash
curl -X DELETE "http://localhost:8000/api/v1/platform/tenants/{tenant_id}" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 3.2 前端页面测试

#### 测试登录页面

1. 访问: `http://localhost:8000/platform-login.html`
2. 输入用户名: `platform_admin`
3. 输入密码: `111111`
4. 点击登录按钮
5. 验证：
   - 登录成功后跳转到仪表板
   - Token保存到localStorage
   - 用户信息保存到localStorage

检查localStorage：
```javascript
// 在浏览器控制台执行
console.log('Token:', localStorage.getItem('his_token'));
console.log('User:', localStorage.getItem('his_user'));
```

#### 测试仪表板页面

1. 登录后自动跳转到: `http://localhost:8000/views/platform/dashboard.html`
2. 验证：
   - 统计卡片显示正确
   - 最近租户列表显示
   - 系统时间实时更新
   - 侧边栏导航正常

#### 测试租户管理页面

1. 访问: `http://localhost:8000/views/platform/tenants.html`
2. 测试功能：
   - 查看租户列表
   - 搜索租户（输入关键词）
   - 筛选租户（选择状态）
   - 新增租户（点击"新增租户"按钮）
   - 编辑租户（点击"编辑"按钮）
   - 删除租户（点击"删除"按钮，确认删除）

## 四、测试检查清单

### 4.1 后端API测试

- [ ] 平台管理员登录成功
- [ ] 登录返回正确的Token和用户信息
- [ ] 获取租户列表成功
- [ ] 租户列表包含正确的分页信息
- [ ] 获取租户详情成功
- [ ] 创建租户成功
- [ ] 创建租户时验证必填字段
- [ ] 创建租户时验证唯一性（代码、域名）
- [ ] 更新租户成功
- [ ] 删除租户成功（软删除）
- [ ] 未登录访问API返回401
- [ ] 普通用户访问API返回403

### 4.2 前端页面测试

- [ ] 登录页面正常加载
- [ ] 登录表单验证正常
- [ ] 登录成功跳转正常
- [ ] 登录失败显示错误信息
- [ ] 仪表板页面正常加载
- [ ] 统计数据正确显示
- [ ] 最近租户列表正确显示
- [ ] 租户管理页面正常加载
- [ ] 租户列表正确显示
- [ ] 搜索功能正常
- [ ] 筛选功能正常
- [ ] 分页功能正常
- [ ] 新增租户功能正常
- [ ] 编辑租户功能正常
- [ ] 删除租户功能正常
- [ ] 未登录访问自动跳转
- [ ] 普通用户访问自动跳转

### 4.3 权限控制测试

- [ ] 未登录用户无法访问平台管理页面
- [ ] 普通用户无法访问平台管理页面
- [ ] 平台管理员可以正常访问
- [ ] Token过期后需要重新登录

## 五、常见问题

### 5.1 后端服务无法启动

**问题**: `ModuleNotFoundError: No module named 'pydantic_settings'`

**解决**:
```bash
cd backend
pip install pydantic-settings
```

### 5.2 登录失败

**问题**: 登录返回401错误

**解决**:
1. 检查数据库是否已初始化测试数据
2. 确认平台管理员账号存在
3. 检查密码是否正确（应为111111）

### 5.3 前端页面无法访问

**问题**: 404错误或页面无法加载

**解决**:
1. 检查文件路径是否正确
2. 确认Web服务器配置正确
3. 检查静态文件服务是否正常

### 5.4 API调用失败

**问题**: CORS错误或401错误

**解决**:
1. 检查后端CORS配置
2. 确认Token是否正确传递
3. 检查Authorization头格式

## 六、测试报告模板

测试完成后，记录测试结果：

```markdown
## 测试结果

**测试日期**: 2024-12-19
**测试人员**: [姓名]
**测试环境**: [环境描述]

### 后端API测试
- [x] 平台管理员登录 - 通过
- [x] 获取租户列表 - 通过
- [x] 创建租户 - 通过
- [ ] 更新租户 - 待测试
- [ ] 删除租户 - 待测试

### 前端页面测试
- [x] 登录页面 - 通过
- [x] 仪表板页面 - 通过
- [x] 租户管理页面 - 通过

### 发现的问题
1. [问题描述]
2. [问题描述]

### 建议
1. [建议内容]
2. [建议内容]
```

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  

