# 科室管理前后端集成文档

## 集成概述
本文档描述了科室管理模块的前后端集成情况，包括API接口、数据格式、错误处理等。

## 后端API接口

### 1. 获取科室列表
- **路径**: `GET /api/v1/departments`
- **参数**:
  - `skip`: 跳过的记录数（默认0）
  - `limit`: 每页记录数（默认100，最大1000）
  - `search`: 搜索关键词（可选）
- **响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "科室名称",
        "code": "科室编码",
        "description": "描述",
        "status": "active",
        "doctor_count": 0,
        "created_at": "2025-11-06T23:00:00"
      }
    ],
    "pagination": {
      "total": 10,
      "page": 1,
      "page_size": 100,
      "pages": 1
    }
  }
}
```

### 2. 获取科室详情
- **路径**: `GET /api/v1/departments/{department_id}`
- **响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "uuid",
    "name": "科室名称",
    "code": "科室编码",
    "description": "描述",
    "status": "active",
    "sort_order": 0
  }
}
```

### 3. 创建科室
- **路径**: `POST /api/v1/departments`
- **请求体**:
```json
{
  "name": "科室名称",
  "code": "科室编码（英文大写）",
  "description": "描述（可选）",
  "status": "active（可选，默认active）",
  "sort_order": 0（可选，默认0）
}
```
- **响应格式**:
```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": "uuid",
    "name": "科室名称",
    "code": "科室编码"
  }
}
```

### 4. 更新科室
- **路径**: `PUT /api/v1/departments/{department_id}`
- **请求体**（所有字段可选）:
```json
{
  "name": "科室名称",
  "description": "描述",
  "status": "active|inactive",
  "sort_order": 0
}
```
- **注意**: 科室编码创建后不可修改

### 5. 删除科室
- **路径**: `DELETE /api/v1/departments/{department_id}`
- **响应格式**:
```json
{
  "code": 200,
  "message": "删除科室成功"
}
```

## 前端API调用

### DepartmentAPI对象
位于 `/frontend/js/api.js`

```javascript
const DepartmentAPI = {
    // 获取科室列表
    async getList(params = {}) {
        const backendParams = {
            skip: ((params.page || 1) - 1) * (params.page_size || 100),
            limit: params.page_size || 100,
            search: params.keyword || params.search || ''
        };
        return await api.get('/departments', backendParams);
    },
    
    // 获取科室详情
    async getDetail(id) {
        return await api.get(`/departments/${id}`);
    },
    
    // 创建科室
    async create(data) {
        return await api.post('/departments', data);
    },
    
    // 更新科室
    async update(id, data) {
        return await api.put(`/departments/${id}`, data);
    },
    
    // 删除科室
    async delete(id) {
        return await api.delete(`/departments/${id}`);
    }
};
```

## 前端页面功能

### 页面位置
`/frontend/views/system/departments.html`

### 主要功能
1. **科室列表展示**
   - 显示科室名称、编码、描述、医生数量、状态、创建时间
   - 支持搜索功能
   - 支持分页

2. **新增科室**
   - 表单字段：名称（必填）、编码（必填）、描述（可选）
   - 编码自动转换为大写
   - 创建后自动刷新列表

3. **编辑科室**
   - 可编辑：名称、描述、状态
   - 编码不可修改（只读）
   - 更新后自动刷新列表

4. **删除科室**
   - 软删除（设置deleted_at）
   - 删除前确认提示
   - 删除后自动刷新列表

### 全局函数
所有函数已挂载到`window`对象：
- `window.loadDepartments()` - 加载科室列表
- `window.searchDepartments()` - 搜索科室
- `window.resetSearch()` - 重置搜索
- `window.showAddDepartmentModal()` - 显示新增弹窗
- `window.editDepartment(id)` - 编辑科室
- `window.deleteDepartment(id)` - 删除科室

## 数据验证

### 后端验证
1. **创建科室时**:
   - 检查科室编码在同一租户内是否唯一
   - 编码自动转换为大写
   - 必填字段验证（name, code）

2. **更新科室时**:
   - 科室编码不可修改
   - 状态值验证（active/inactive）

### 前端验证
1. **表单验证**:
   - 名称和编码为必填项
   - 编码自动转换为大写

2. **错误处理**:
   - API调用失败时显示错误提示
   - 网络错误时显示友好提示

## 错误处理

### 后端错误码
- `400`: 业务错误（如编码重复、参数验证失败）
- `404`: 资源不存在
- `500`: 服务器内部错误

### 前端错误处理
- 使用`utils.showToast()`显示错误提示
- 控制台输出详细错误信息（开发环境）
- 网络错误时显示友好提示

## 多租户支持

所有API接口都支持多租户：
- 通过JWT token自动获取`tenant_id`
- 所有查询都自动过滤租户数据
- 创建时自动关联当前租户

## 集成状态

✅ **已完成**:
- 后端API接口（CRUD）
- 前端API调用封装
- 前端页面功能
- 数据格式匹配
- 错误处理
- 多租户支持
- 科室编码唯一性验证

✅ **测试建议**:
1. 测试新增科室（正常情况）
2. 测试新增科室（编码重复）
3. 测试编辑科室
4. 测试删除科室
5. 测试搜索功能
6. 测试分页功能

## 相关文件

- 后端API: `/backend/app/api/v1/departments.py`
- 后端Repository: `/backend/app/repositories/system_repository.py`
- 前端API: `/frontend/js/api.js`
- 前端页面: `/frontend/views/system/departments.html`
- 数据模型: `/backend/app/models/system.py`

集成完成时间: 2025-11-06 23:40

