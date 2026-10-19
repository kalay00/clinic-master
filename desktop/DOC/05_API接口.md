# API 接口规范

## 5.1 请求封装

项目使用 Axios 进行网络请求封装，核心配置在 `src/utils/request.js`。

### 5.1.1 请求方法

```javascript
import { request, get, post, put, del, upload, download } from '@/utils/request'

// GET 请求
const data = await get('/api/user/list', { page: 1, size: 10 })

// POST 请求
const result = await post('/api/user/create', { username: 'test', email: 'test@example.com' })

// PUT 请求
await put('/api/user/123', { username: 'updated' })

// DELETE 请求
await del('/api/user/123')

// 上传文件
const formData = new FormData()
formData.append('file', fileInput.files[0])
await upload('/api/upload', formData)

// 下载文件
await download('/api/export', { format: 'xlsx' }, 'report.xlsx')
```

### 5.1.2 自定义配置

```javascript
// 带自定义配置
await get('/api/data', {}, {
  headers: { 'X-Custom-Header': 'value' },
  timeout: 10000
})
```

## 5.2 接口模块化

按业务模块划分接口文件：

### 5.2.1 用户接口 (src/api/user.js)

```javascript
import { get, post } from '@/utils/request'

export function login(data) {
  return post('/auth/login', data)
}

export function logout() {
  return post('/auth/logout')
}

export function getUserInfo() {
  return get('/auth/userInfo')
}

export function refreshToken() {
  return post('/auth/refreshToken')
}
```

### 5.2.2 系统接口 (src/api/system.js)

```javascript
import { get, post, put, del } from '@/utils/request'

export function getUserList(params) {
  return get('/system/user/list', params)
}

export function getUserDetail(id) {
  return get(`/system/user/${id}`)
}

export function createUser(data) {
  return post('/system/user', data)
}

export function updateUser(id, data) {
  return put(`/system/user/${id}`, data)
}

export function deleteUser(id) {
  return del(`/system/user/${id}`)
}
```

### 5.2.3 仪表盘接口 (src/api/dashboard.js)

```javascript
import { get } from '@/utils/request'

export function getDashboardData() {
  return get('/dashboard/data')
}

export function getChartData(type) {
  return get('/dashboard/chart', { type })
}
```

## 5.3 接口统一调用

在 `src/api/index.js` 统一导出：

```javascript
import userApi from './user'
import systemApi from './system'
import dashboardApi from './dashboard'

const api = {
  user: userApi,
  system: systemApi,
  dashboard: dashboardApi
}

export default api
export { userApi, systemApi, dashboardApi }
```

## 5.4 请求拦截器

### 5.4.1 请求拦截

- 自动添加 Token 到请求头
- 添加时间戳防止缓存
- 防重复请求（同一请求取消前一个）

```javascript
// 实际使用中无需手动处理，已封装在 request.js 中
```

### 5.4.2 响应拦截

- 统一处理成功/失败状态
- 401 自动跳转登录
- 403 无权限提示
- 500 服务器错误提示

## 5.5 响应格式规范

### 5.5.1 成功响应

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": 1,
    "username": "admin"
  }
}
```

### 5.5.2 失败响应

```json
{
  "code": 400,
  "message": "参数错误",
  "data": null
}
```

## 5.6 错误码规范

| 错误码 | 说明 | 处理方式 |
|--------|------|---------|
| 200 | 成功 | 正常处理 |
| 400 | 请求参数错误 | 提示用户 |
| 401 | 未登录/登录过期 | 跳转登录页 |
| 403 | 无权限 | 提示无权限 |
| 404 | 资源不存在 | 提示不存在 |
| 500 | 服务器错误 | 提示稍后重试 |

## 5.7 接口文档模板

新增接口时，建议在对应的接口文件中添加注释：

```javascript
/**
 * 获取用户列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.size - 每页条数
 * @param {string} [params.username] - 用户名（可选）
 * @returns {Promise<{code: number, data: Array, total: number}>}
 */
export function getUserList(params) {
  return get('/system/user/list', params)
}
```

## 5.8 Mock 接口

开发环境支持 Mock 数据，配置方式：

1. 在 `src/api/` 对应文件中返回模拟数据
2. 或使用 Vite 插件配置 Mock

示例（直接返回模拟数据）：

```javascript
export function getDashboardData() {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        code: 200,
        data: {
          users: 12580,
          visits: 1234,
          orders: 856,
          sales: 128560
        }
      })
    }, 300)
  })
}
```
