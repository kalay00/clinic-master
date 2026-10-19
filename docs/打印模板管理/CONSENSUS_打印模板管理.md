# 打印模板管理功能 - 共识文档

## 一、明确的需求描述

### 1.1 核心功能
管理员可以自定义打印模板，在每个打印界面可以选择打印模板。打印模板支持：
- ✅ 自定义命名
- ✅ 实时预览
- ✅ 字段拖拽排序
- ✅ 多场景支持（账单、处方、病历）

### 1.2 功能边界
- ✅ **包含**：模板CRUD、字段拖拽、预览、模板选择
- ❌ **不包含**：模板导入/导出、版本管理、权限控制（后续可扩展）

## 二、技术实现方案

### 2.1 后端架构
- **数据模型**：`PrintTemplate`（继承BaseModel）
- **数据存储**：PostgreSQL，使用JSONB存储模板配置
- **API设计**：RESTful API，6个端点
- **多租户**：基于tenant_id数据隔离

### 2.2 前端架构
- **管理页面**：`/system/print-templates`
- **编辑器**：使用SortableJS实现拖拽
- **预览**：实时渲染模板
- **集成**：在现有打印页面添加模板选择

### 2.3 技术选型
- **拖拽库**：SortableJS
- **模板引擎**：原生JavaScript模板字符串
- **样式**：Bootstrap 5 + 自定义CSS

## 三、数据模型设计

### 3.1 表结构
```sql
print_templates (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  name VARCHAR(100) NOT NULL,
  type VARCHAR(50) NOT NULL,  -- bill/prescription/medical_record
  template_config JSONB NOT NULL,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  deleted_at TIMESTAMP,
  created_by UUID,
  updated_by UUID
)
```

### 3.2 模板配置结构
- **版本控制**：version字段
- **页面设置**：width, height, margin
- **区域划分**：header, body, footer
- **字段类型**：text, data, table, image, line

## 四、接口规范

### 4.1 API端点
- `GET /api/v1/print-templates` - 获取列表
- `GET /api/v1/print-templates/{id}` - 获取详情
- `POST /api/v1/print-templates` - 创建模板
- `PUT /api/v1/print-templates/{id}` - 更新模板
- `DELETE /api/v1/print-templates/{id}` - 删除模板
- `GET /api/v1/print-templates/{id}/preview` - 预览模板

### 4.2 响应格式
统一使用 `{code, message, data}` 格式

## 五、任务拆分

### 5.1 11个原子任务
1. 创建数据模型
2. 创建Repository
3. 创建Service
4. 创建API接口
5. 创建数据库迁移
6. 创建前端API客户端
7. 创建模板管理页面
8. 创建模板编辑器
9. 创建模板预览组件
10. 集成到现有打印界面
11. 测试和优化

### 5.2 任务依赖
- 任务1 → 任务2 → 任务3 → 任务4
- 任务1 → 任务5
- 任务4 → 任务6 → 任务7 → 任务8 → 任务9 → 任务10 → 任务11

## 六、验收标准

### 6.1 功能验收
- ✅ 管理员可以创建、编辑、删除打印模板
- ✅ 模板可以自定义命名
- ✅ 支持字段拖拽排序
- ✅ 支持实时预览
- ✅ 在打印界面可以选择模板
- ✅ 模板数据按租户隔离

### 6.2 质量验收
- ✅ 代码符合项目规范
- ✅ 无语法错误和lint错误
- ✅ 支持多租户数据隔离
- ✅ 错误处理完善

## 七、技术约束和集成方案

### 7.1 代码规范
- 函数级注释（功能描述、参数说明、返回值）
- 遵循现有命名规范
- 使用现有的工具和库

### 7.2 数据库规范
- 使用软删除（deleted_at）
- 多租户支持（tenant_id）
- 审计字段（created_at, updated_at, created_by, updated_by）

### 7.3 API规范
- RESTful API设计
- 统一的响应格式
- 错误处理规范

## 八、确认事项

### 8.1 已确认
- ✅ 使用拖拽方式排列字段
- ✅ 支持实时预览
- ✅ 模板按类型分类
- ✅ 每个类型可以有多个模板
- ✅ 可以设置默认模板

### 8.2 假设（待确认）
- ❓ 模板字段暂不支持条件显示（后续可扩展）
- ❓ 支持基本的样式设置（字体、颜色、对齐方式）
- ❓ 暂不支持嵌套布局，使用简单的线性布局
- ❓ 模板预览使用模拟数据

## 九、下一步行动

### 9.1 等待确认
- 用户审查对齐文档、设计文档、任务拆分文档
- 确认技术方案和实现细节
- 确认任务拆分是否合理

### 9.2 确认后执行
- 开始执行任务1：创建数据模型
- 按任务依赖顺序逐步实现
- 每完成一个任务立即验证

## 十、风险评估

### 10.1 技术风险
- **低风险**：拖拽功能（SortableJS成熟稳定）
- **低风险**：模板渲染（使用标准HTML/CSS）
- **中风险**：模板配置JSON结构复杂（需要充分测试）

### 10.2 业务风险
- **低风险**：功能需求明确
- **低风险**：与现有系统集成简单

## 十一、项目特性规范对齐

### 11.1 与现有系统一致
- ✅ 使用相同的认证机制
- ✅ 使用相同的多租户隔离
- ✅ 使用相同的软删除机制
- ✅ 使用相同的API响应格式

### 11.2 代码质量
- ✅ 遵循现有代码规范
- ✅ 使用现有组件库
- ✅ 保持代码风格一致

