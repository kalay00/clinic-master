# 前端项目说明

## 项目结构

```
frontend/
├── index.html          # 主入口HTML文件
├── login.html          # 登录页面
├── css/
│   └── main.css        # 主样式文件
├── js/
│   ├── app.js          # 应用主入口
│   └── api.js          # API调用封装
├── images/             # 图片资源
└── views/              # 页面视图
    ├── dashboard.html  # 工作台
    ├── patients/       # 患者管理
    ├── registrations/  # 挂号管理
    ├── treatments/     # 诊疗管理
    ├── payments/       # 收费管理
    ├── pharmacy/       # 药房管理
    ├── reports/        # 报表统计
    └── system/         # 系统管理
```

## 技术栈

- **UI框架**: Bootstrap 5.3+
- **图标库**: Bootstrap Icons
- **JavaScript**: ES6+ 原生JavaScript
- **图表库**: Chart.js (用于报表统计，按需引入)

## 开发说明

### 1. 项目特点

- 使用原生HTML/CSS/JavaScript，无前端框架依赖
- 基于Bootstrap 5，确保界面美观统一
- 响应式设计，支持PC、平板、移动端
- 模块化设计，代码结构清晰

### 2. 核心文件说明

#### `index.html`
- 主入口文件
- 引入Bootstrap和自定义CSS/JS
- 应用容器

#### `login.html`
- 登录页面
- 独立的HTML文件
- 登录成功后跳转到主应用

#### `css/main.css`
- 主样式文件
- 自定义样式和Bootstrap覆盖
- 响应式布局样式

#### `js/app.js`
- 应用主入口
- 路由管理
- 全局状态管理
- 工具函数

#### `js/api.js`
- API调用封装
- 各业务模块的API方法
- 统一的错误处理

### 3. 页面开发规范

#### 页面结构
每个页面视图应包含：
- 页面标题和面包屑导航
- 操作按钮区（新增、查询、导出等）
- 内容区域（表格、表单、卡片等）

#### 页面示例
```html
<!-- 页面标题 -->
<div class="page-header">
    <h1><i class="bi bi-people"></i> 患者管理</h1>
</div>

<!-- 操作按钮 -->
<div class="mb-3">
    <button class="btn btn-primary">新增患者</button>
    <button class="btn btn-secondary">导出</button>
</div>

<!-- 内容区域 -->
<div class="card">
    <div class="card-body">
        <!-- 页面内容 -->
    </div>
</div>
```

#### 页面脚本
每个页面可以定义自己的初始化函数：
```javascript
window.pageInit = function() {
    // 页面初始化逻辑
    loadData();
};
```

### 4. API调用

使用全局 `api` 对象或模块化的API对象：

```javascript
// 方式1: 使用全局api对象
const data = await api.get('/patients');

// 方式2: 使用模块化API
const patients = await PatientAPI.getList();
```

### 5. 工具函数

使用全局 `utils` 对象：

```javascript
// 显示Toast通知
utils.showToast('操作成功', 'success');

// 格式化日期
const date = utils.formatDate(new Date(), 'YYYY-MM-DD');

// 格式化金额
const money = utils.formatMoney(1234.56); // ¥1,234.56
```

### 6. 路由导航

使用 `app.navigate()` 方法：

```javascript
// 导航到患者管理页面
app.navigate('patients');
```

### 7. 响应式设计

- 使用Bootstrap Grid系统
- 移动端侧边栏自动折叠
- 表格使用 `table-responsive` 包装

### 8. 浏览器兼容性

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 开发流程

1. **创建页面视图**
   - 在 `views/` 目录下创建对应的HTML文件
   - 参考 `dashboard.html` 的结构

2. **添加页面路由**
   - 在 `js/app.js` 的 `getPagePath()` 方法中添加路由映射

3. **实现页面功能**
   - 调用API获取数据
   - 渲染页面内容
   - 实现交互逻辑

4. **测试验证**
   - 功能测试
   - 响应式测试
   - 浏览器兼容性测试

## 注意事项

1. **API调用**: 确保后端API已实现，否则会报错
2. **Token管理**: 登录后token存储在localStorage，API请求会自动携带
3. **错误处理**: 统一使用 `utils.showToast()` 显示错误信息
4. **加载状态**: 数据加载时显示加载动画，提升用户体验
5. **表单验证**: 使用HTML5表单验证和自定义JavaScript验证

## 下一步开发

参考 `docs/门诊诊所管理系统/TASK_11_前端界面.md` 中的任务列表，按顺序完成各个页面的开发。

