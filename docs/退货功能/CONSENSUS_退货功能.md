# 退货功能 - 共识文档

## 一、明确的需求描述和验收标准

### 1.1 核心功能

#### 退货单管理
- **创建退货单**：必须关联一个已入库的采购单（status='received'）
- **退货方式**：
  - 部分退货：选择采购单中的部分药品，指定每个药品的退货数量
  - 全部退货：退货整个采购单的所有药品
- **退货单状态**：draft（草稿）、approved（已审核）、completed（已完成）、cancelled（已取消）
- **退货单号**：自动生成，格式：RO{YYYYMMDD}{序号}，如：RO202501010001

#### 退货明细
- 每个退货单包含多个退货明细项
- 每个明细项对应采购单中的一个明细项
- 退货数量不能超过采购单中该药品的已入库数量（received_quantity）
- 记录退货的批次号和有效期（从采购单明细中获取）

#### 库存同步
- 退货时自动扣减库存数量
- 创建库存流水记录（transaction_type='return'，quantity为负数）
- 更新库存表的quantity字段

#### 财务同步
- 退货时创建财务记录（Bill）
- bill_type为"purchase_return"
- total_amount为退货总金额（负数或退款金额）
- 记录退货单ID到reference_id

#### 打印功能
- 支持打印退货单
- 使用打印模板系统
- 打印模板类型：purchase_return

### 1.2 业务规则

1. **退货限制**：
   - 只能对已入库（status='received'）的采购单进行退货
   - 退货数量不能超过采购单明细的已入库数量（received_quantity）
   - 不能对已取消的采购单进行退货
   - 不能对已全部退货的采购单再次退货

2. **退货流程**：
   - 创建退货单（草稿状态）
   - 审核退货单（approved状态）
   - 执行退货（completed状态，更新库存、创建财务记录）
   - 可以取消退货单（cancelled状态）

3. **数据一致性**：
   - 退货后需要更新采购单明细的已入库数量（received_quantity -= 退货数量）
   - 如果全部退货，采购单状态保持"received"，但所有明细的已入库数量为0
   - 库存变动需要记录流水
   - 财务记录需要正确关联

### 1.3 验收标准

#### 功能验收
- ✅ 可以创建退货单，必须关联采购单号
- ✅ 可以选择部分退货或全部退货
- ✅ 退货数量不能超过已入库数量
- ✅ 退货后库存自动扣减
- ✅ 退货后创建财务记录
- ✅ 可以打印退货单
- ✅ 退货单打印模板可以自定义

#### 数据验收
- ✅ 退货单数据正确保存
- ✅ 库存数据正确更新
- ✅ 财务记录正确创建
- ✅ 采购单明细的已入库数量正确更新
- ✅ 库存流水记录正确创建

#### 业务验收
- ✅ 退货流程符合业务规则
- ✅ 数据一致性保证
- ✅ 异常情况正确处理（如退货数量超限、采购单状态不正确等）

## 二、技术实现方案

### 2.1 数据模型设计

#### 退货单表（return_orders）
```python
class ReturnOrder(BaseModel):
    __tablename__ = "return_orders"
    
    return_no = Column(String(50), nullable=False, unique=True, comment="退货单号")
    purchase_order_id = Column(UUID, ForeignKey("purchase_orders.id"), nullable=False, comment="采购单ID")
    return_date = Column(Date, nullable=False, comment="退货日期")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    status = Column(String(20), default="draft", comment="状态：draft/approved/completed/cancelled")
    remark = Column(Text, comment="备注")
    
    # 审核和执行信息
    approved_by = Column(UUID, comment="审核人ID")
    approved_at = Column(DateTime, comment="审核时间")
    completed_by = Column(UUID, comment="执行人ID")
    completed_at = Column(DateTime, comment="执行时间")
    
    # 关系
    purchase_order = relationship("PurchaseOrder", backref="return_orders")
    items = relationship("ReturnOrderItem", back_populates="return_order", cascade="all, delete-orphan")
```

#### 退货明细表（return_order_items）
```python
class ReturnOrderItem(BaseModel):
    __tablename__ = "return_order_items"
    
    return_order_id = Column(UUID, ForeignKey("return_orders.id"), nullable=False, comment="退货单ID")
    purchase_order_item_id = Column(UUID, ForeignKey("purchase_order_items.id"), nullable=False, comment="采购明细ID")
    drug_id = Column(UUID, ForeignKey("drugs.id"), nullable=False, comment="药品ID")
    quantity = Column(Integer, nullable=False, comment="退货数量")
    unit_price = Column(Numeric(10, 2), default=0, comment="单价")
    total_amount = Column(Numeric(10, 2), default=0, comment="总金额")
    batch_no = Column(String(50), comment="批次号")
    expiry_date = Column(String(20), comment="有效期")
    
    # 关系
    return_order = relationship("ReturnOrder", back_populates="items")
    purchase_order_item = relationship("PurchaseOrderItem", backref="return_items")
```

### 2.2 API接口设计

#### 退货单管理
- `GET /api/v1/inventory/return-orders` - 获取退货单列表
- `GET /api/v1/inventory/return-orders/{id}` - 获取退货单详情
- `POST /api/v1/inventory/return-orders` - 创建退货单
- `PUT /api/v1/inventory/return-orders/{id}` - 更新退货单
- `POST /api/v1/inventory/return-orders/{id}/approve` - 审核退货单
- `POST /api/v1/inventory/return-orders/{id}/complete` - 完成退货单（执行退货）
- `POST /api/v1/inventory/return-orders/{id}/cancel` - 取消退货单
- `DELETE /api/v1/inventory/return-orders/{id}` - 删除退货单

#### 辅助接口
- `GET /api/v1/inventory/purchase-orders/{id}/returnable` - 获取可退货的采购单信息

### 2.3 前端页面设计

#### 退货单列表页面
- 路径：`/views/inventory/return-orders.html`
- 功能：列表展示、搜索、筛选、查看、编辑、删除、审核、完成、打印

#### 创建退货单页面
- 弹窗形式
- 选择采购单
- 显示采购单明细
- 选择退货药品和数量
- 支持全部退货快捷操作

#### 打印页面
- 使用打印模板系统
- 支持选择打印模板
- 实时预览

### 2.4 技术约束

- 使用现有的BaseModel基类
- 遵循现有的代码规范和架构模式
- 使用现有的异常处理机制
- 使用现有的日志系统
- 多租户隔离（tenant_id）

## 三、任务边界限制

### 3.1 包含的功能
- ✅ 退货单的CRUD操作
- ✅ 退货单与采购单的关联
- ✅ 部分退货和全部退货
- ✅ 库存自动扣减
- ✅ 财务记录创建
- ✅ 退货单打印功能
- ✅ 退货单打印模板管理

### 3.2 不包含的功能
- ❌ 退货单的审批流程（简化处理，单级审核）
- ❌ 退货原因分类（后续可扩展）
- ❌ 退货单的批量操作
- ❌ 退货单的导入导出
- ❌ 退货单的统计分析

## 四、集成方案

### 4.1 与采购单模块集成
- 查询已入库的采购单
- 获取采购单明细信息
- 更新采购单明细的已入库数量

### 4.2 与库存模块集成
- 扣减库存数量
- 创建库存流水记录
- 更新库存表

### 4.3 与财务模块集成
- 创建Bill记录
- 记录退货金额
- 关联退货单ID

### 4.4 与打印模板模块集成
- 新增打印模板类型：purchase_return
- 使用现有的打印模板渲染系统

