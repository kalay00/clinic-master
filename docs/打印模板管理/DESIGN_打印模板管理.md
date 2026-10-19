# 打印模板管理功能 - 设计文档

## 一、整体架构

### 1.1 系统分层设计

```
┌─────────────────────────────────────────────────────────┐
│                     前端层 (Frontend)                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 模板管理页面  │  │  模板编辑器   │  │  打印界面集成  │  │
│  │ (列表/CRUD)  │  │ (拖拽/预览)  │  │ (模板选择)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP API
┌─────────────────────────────────────────────────────────┐
│                      API层 (FastAPI)                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │  /api/v1/print-templates                         │   │
│  │  - GET    /print-templates (列表)                │   │
│  │  - GET    /print-templates/{id} (详情)           │   │
│  │  - POST   /print-templates (创建)                   │   │
│  │  - PUT    /print-templates/{id} (更新)            │   │
│  │  - DELETE /print-templates/{id} (删除)           │   │
│  │  - GET    /print-templates/{id}/preview (预览)   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                     Service层 (Business Logic)            │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │  PrintTemplateService                           │   │
│  │  - create_template()                            │   │
│  │  - update_template()                            │   │
│  │  - delete_template()                            │   │
│  │  - get_template()                               │   │
│  │  - list_templates()                             │   │
│  │  - render_template() (渲染模板)                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                  Repository层 (Data Access)                │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │  PrintTemplateRepository                         │   │
│  │  - create()                                      │   │
│  │  - update()                                      │   │
│  │  - delete()                                      │   │
│  │  - get_by_id()                                   │   │
│  │  - list_by_type()                                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                   │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │  print_templates 表                                │   │
│  │  - id (UUID)                                       │   │
│  │  - name (VARCHAR)                                  │   │
│  │  - type (VARCHAR)                                  │   │
│  │  - template_config (JSONB)                        │   │
│  │  - is_default (BOOLEAN)                           │   │
│  │  - tenant_id (UUID)                               │   │
│  │  - created_at, updated_at, deleted_at             │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

1. **PrintTemplate 模型**：数据模型定义
2. **PrintTemplateRepository**：数据访问层
3. **PrintTemplateService**：业务逻辑层
4. **PrintTemplateAPI**：API接口层
5. **前端模板管理页面**：CRUD界面
6. **模板编辑器组件**：拖拽编辑界面
7. **模板预览组件**：实时预览功能
8. **打印集成组件**：在打印页面选择模板

## 二、数据模型设计

### 2.1 PrintTemplate 模型

```python
class PrintTemplate(BaseModel):
    """打印模板模型"""
    __tablename__ = "print_templates"
    
    name = Column(String(100), nullable=False, comment="模板名称")
    type = Column(String(50), nullable=False, comment="模板类型：bill/prescription/medical_record")
    template_config = Column(JSON, nullable=False, comment="模板配置（JSON）")
    is_default = Column(Boolean, default=False, comment="是否默认模板")
    
    # 关系
    # 无外键关系
```

### 2.2 template_config JSON结构

```json
{
  "version": "1.0",
  "page": {
    "width": 210,
    "height": 297,
    "unit": "mm",
    "margin": {
      "top": 10,
      "right": 10,
      "bottom": 10,
      "left": 10
    }
  },
  "sections": [
    {
      "id": "header",
      "name": "页眉",
      "fields": [
        {
          "id": "field_1",
          "type": "text",
          "name": "title",
          "label": "标题",
          "value": "门诊收费单",
          "position": {"x": 0, "y": 0},
          "style": {
            "fontSize": 18,
            "fontWeight": "bold",
            "textAlign": "center"
          }
        },
        {
          "id": "field_2",
          "type": "data",
          "name": "bill_no",
          "label": "账单号",
          "position": {"x": 0, "y": 30},
          "style": {
            "fontSize": 12
          }
        }
      ]
    },
    {
      "id": "body",
      "name": "正文",
      "fields": [
        {
          "id": "field_3",
          "type": "table",
          "name": "items",
          "label": "明细",
          "columns": [
            {"name": "item_name", "label": "项目名称", "width": "40%"},
            {"name": "quantity", "label": "数量", "width": "20%"},
            {"name": "unit_price", "label": "单价", "width": "20%"},
            {"name": "total_price", "label": "金额", "width": "20%"}
          ],
          "position": {"x": 0, "y": 100},
          "style": {}
        }
      ]
    },
    {
      "id": "footer",
      "name": "页脚",
      "fields": [
        {
          "id": "field_4",
          "type": "data",
          "name": "total_amount",
          "label": "总金额",
          "position": {"x": 0, "y": 200},
          "style": {
            "fontSize": 14,
            "fontWeight": "bold"
          }
        }
      ]
    }
  ]
}
```

### 2.3 字段类型定义

| 类型 | 说明 | 示例 |
|------|------|------|
| `text` | 静态文本 | "门诊收费单" |
| `data` | 动态数据字段 | `bill_no`, `patient_name` |
| `table` | 表格数据 | 账单明细、处方药品 |
| `image` | 图片 | Logo |
| `line` | 分隔线 | 用于布局分隔 |

## 三、接口设计

### 3.1 API端点

#### 3.1.1 获取模板列表
```
GET /api/v1/print-templates
Query Parameters:
  - type: 模板类型（可选：bill/prescription/medical_record）
  - skip: 跳过的记录数
  - limit: 每页记录数

Response:
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "账单打印模板A",
        "type": "bill",
        "is_default": true,
        "created_at": "2024-01-01T00:00:00"
      }
    ],
    "pagination": {
      "total": 10,
      "page": 1,
      "page_size": 10,
      "pages": 1
    }
  }
}
```

#### 3.1.2 获取模板详情
```
GET /api/v1/print-templates/{id}

Response:
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "uuid",
    "name": "账单打印模板A",
    "type": "bill",
    "template_config": {...},
    "is_default": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

#### 3.1.3 创建模板
```
POST /api/v1/print-templates

Request Body:
{
  "name": "账单打印模板A",
  "type": "bill",
  "template_config": {...},
  "is_default": false
}

Response:
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": "uuid",
    "name": "账单打印模板A",
    ...
  }
}
```

#### 3.1.4 更新模板
```
PUT /api/v1/print-templates/{id}

Request Body:
{
  "name": "账单打印模板A（更新）",
  "template_config": {...},
  "is_default": true
}

Response:
{
  "code": 200,
  "message": "更新成功",
  "data": {...}
}
```

#### 3.1.5 删除模板
```
DELETE /api/v1/print-templates/{id}

Response:
{
  "code": 200,
  "message": "删除成功"
}
```

#### 3.1.6 预览模板
```
GET /api/v1/print-templates/{id}/preview?data_type=bill&data_id={id}

Response:
{
  "code": 200,
  "message": "预览成功",
  "data": {
    "html": "<html>...</html>"
  }
}
```

## 四、前端设计

### 4.1 模板管理页面结构

```
/system/print-templates
├── 列表区域
│   ├── 搜索栏（按类型筛选）
│   ├── 模板列表表格
│   └── 操作按钮（新增、编辑、删除、设为默认）
├── 编辑弹窗
│   ├── 基本信息（名称、类型）
│   ├── 模板编辑器
│   │   ├── 字段列表（可拖拽）
│   │   ├── 画布区域（拖拽放置）
│   │   └── 属性面板（编辑字段属性）
│   └── 预览区域（实时预览）
└── 打印集成
    └── 在打印页面添加模板选择下拉框
```

### 4.2 模板编辑器组件

使用 SortableJS 实现拖拽功能：

```javascript
// 字段列表（可拖拽源）
<div id="field-list">
  <div class="field-item" data-type="text">文本</div>
  <div class="field-item" data-type="data">数据字段</div>
  <div class="field-item" data-type="table">表格</div>
  <div class="field-item" data-type="image">图片</div>
  <div class="field-item" data-type="line">分隔线</div>
</div>

// 画布区域（拖拽目标）
<div id="canvas">
  <div class="section" data-section="header">页眉</div>
  <div class="section" data-section="body">正文</div>
  <div class="section" data-section="footer">页脚</div>
</div>
```

### 4.3 模板渲染

```javascript
function renderTemplate(templateConfig, data) {
  let html = '<div class="print-template">';
  
  templateConfig.sections.forEach(section => {
    html += `<div class="section section-${section.id}">`;
    
    section.fields.forEach(field => {
      html += renderField(field, data);
    });
    
    html += '</div>';
  });
  
  html += '</div>';
  return html;
}

function renderField(field, data) {
  switch(field.type) {
    case 'text':
      return `<div style="${getStyleString(field.style)}">${field.value}</div>`;
    case 'data':
      return `<div style="${getStyleString(field.style)}">${data[field.name] || ''}</div>`;
    case 'table':
      return renderTable(field, data);
    case 'image':
      return `<img src="${field.value}" style="${getStyleString(field.style)}" />`;
    case 'line':
      return `<hr style="${getStyleString(field.style)}" />`;
  }
}
```

## 五、数据流向

### 5.1 创建模板流程

```
用户操作 → 前端表单 → API请求 → Service验证 → Repository保存 → 数据库
                ↓
            返回结果 → 更新列表
```

### 5.2 使用模板打印流程

```
用户点击打印 → 选择模板 → 获取模板配置 → 获取数据 → 渲染模板 → 打印
```

## 六、异常处理策略

### 6.1 后端异常
- **模板不存在**：返回404错误
- **模板配置无效**：返回400错误，提示配置格式错误
- **权限不足**：返回403错误
- **数据验证失败**：返回422错误，显示详细验证信息

### 6.2 前端异常
- **API请求失败**：显示错误提示，记录日志
- **模板渲染失败**：显示默认模板或错误提示
- **拖拽操作失败**：回滚到上一个状态

## 七、安全考虑

### 7.1 数据安全
- 模板数据按租户隔离
- 只有管理员可以管理模板
- 模板配置JSON需要验证格式

### 7.2 输入验证
- 模板名称长度限制（1-100字符）
- 模板类型枚举验证
- JSON配置格式验证

## 八、性能优化

### 8.1 数据库优化
- 模板列表查询添加索引（tenant_id, type）
- 使用JSONB类型存储配置（PostgreSQL）

### 8.2 前端优化
- 模板预览使用防抖（避免频繁渲染）
- 大量字段时使用虚拟滚动

