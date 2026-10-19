# 进销存模块需求对齐文档

## 一、需求理解

### 1.1 模块概述
进销存模块用于管理门诊诊所的药品采购、销售、库存等业务流程，实现完整的进销存管理。

### 1.2 业务场景
- **采购场景**: 诊所需要定期采购药品，需要管理供应商、采购单、入库等
- **销售场景**: 患者取药就是销售，需要记录销售明细
- **库存管理**: 需要实时掌握库存情况，支持盘点、调整等操作
- **报表分析**: 需要查看进销存报表，分析库存周转、销售情况等

### 1.3 核心功能需求

#### 1.3.1 供应商管理
- 供应商基本信息（名称、联系方式、地址等）
- 供应商分类
- 供应商评价
- 供应商启用/禁用

#### 1.3.2 采购管理
- 采购单创建、编辑、删除
- 采购单审核、入库
- 采购明细管理
- 采购退货
- 采购单查询（支持按供应商、日期、状态筛选）

#### 1.3.3 销售管理
- 销售单管理（与处方发药关联）
- 销售明细查询
- 销售退货
- 销售统计

#### 1.3.4 库存管理（扩展现有功能）
- 库存查询（已有）
- 库存盘点
- 库存调整（已有部分）
- 库存预警（已有）
- 库存流水记录

#### 1.3.5 进销存报表
- 进销存汇总报表
- 库存周转率分析
- 销售统计报表
- 采购统计报表

## 二、现有系统分析

### 2.1 已有功能
- ✅ 药品管理（Drug模型）
- ✅ 基础库存管理（Inventory模型）
- ✅ 库存更新接口（入库/出库）
- ✅ 库存预警功能
- ✅ 发药管理（Dispense模型，可作为销售）

### 2.2 缺失功能
- ❌ 供应商管理
- ❌ 采购单管理
- ❌ 采购明细管理
- ❌ 库存流水记录
- ❌ 库存盘点功能
- ❌ 进销存报表

## 三、技术方案

### 3.1 数据模型设计

#### 3.1.1 供应商表（suppliers）
- id, tenant_id
- name: 供应商名称
- code: 供应商编码
- contact_name: 联系人
- contact_phone: 联系电话
- contact_email: 联系邮箱
- address: 地址
- category: 供应商分类
- status: 状态（active/inactive）
- remark: 备注
- created_at, updated_at, deleted_at

#### 3.1.2 采购单表（purchase_orders）
- id, tenant_id
- order_no: 采购单号
- supplier_id: 供应商ID
- order_date: 采购日期
- expected_date: 预计到货日期
- total_amount: 总金额
- status: 状态（draft/approved/received/cancelled）
- remark: 备注
- approved_by: 审核人
- approved_at: 审核时间
- received_by: 入库人
- received_at: 入库时间

#### 3.1.3 采购明细表（purchase_order_items）
- id
- purchase_order_id: 采购单ID
- drug_id: 药品ID
- quantity: 数量
- unit_price: 单价
- total_amount: 总金额
- received_quantity: 已入库数量
- batch_no: 批次号
- expiry_date: 有效期

#### 3.1.4 库存流水表（inventory_transactions）
- id, tenant_id
- drug_id: 药品ID
- transaction_type: 交易类型（purchase/sale/adjust/check）
- reference_id: 关联ID（采购单ID、销售单ID等）
- reference_type: 关联类型
- quantity: 数量（正数入库，负数出库）
- unit_price: 单价
- total_amount: 总金额
- before_quantity: 变动前库存
- after_quantity: 变动后库存
- operator_id: 操作人
- transaction_date: 交易日期
- remark: 备注

#### 3.1.5 库存盘点表（inventory_checks）
- id, tenant_id
- check_no: 盘点单号
- check_date: 盘点日期
- status: 状态（draft/completed）
- operator_id: 操作人
- remark: 备注

#### 3.1.6 盘点明细表（inventory_check_items）
- id
- inventory_check_id: 盘点单ID
- drug_id: 药品ID
- book_quantity: 账面数量
- actual_quantity: 实际数量
- difference: 差异数量
- unit_price: 单价
- difference_amount: 差异金额
- remark: 备注

### 3.2 API接口设计

#### 3.2.1 供应商管理
- GET /api/v1/inventory/suppliers - 获取供应商列表
- GET /api/v1/inventory/suppliers/{id} - 获取供应商详情
- POST /api/v1/inventory/suppliers - 创建供应商
- PUT /api/v1/inventory/suppliers/{id} - 更新供应商
- DELETE /api/v1/inventory/suppliers/{id} - 删除供应商

#### 3.2.2 采购管理
- GET /api/v1/inventory/purchase-orders - 获取采购单列表
- GET /api/v1/inventory/purchase-orders/{id} - 获取采购单详情
- POST /api/v1/inventory/purchase-orders - 创建采购单
- PUT /api/v1/inventory/purchase-orders/{id} - 更新采购单
- POST /api/v1/inventory/purchase-orders/{id}/approve - 审核采购单
- POST /api/v1/inventory/purchase-orders/{id}/receive - 入库
- DELETE /api/v1/inventory/purchase-orders/{id} - 删除采购单

#### 3.2.3 库存流水
- GET /api/v1/inventory/transactions - 获取库存流水列表
- GET /api/v1/inventory/transactions/{id} - 获取流水详情

#### 3.2.4 库存盘点
- GET /api/v1/inventory/checks - 获取盘点单列表
- GET /api/v1/inventory/checks/{id} - 获取盘点单详情
- POST /api/v1/inventory/checks - 创建盘点单
- POST /api/v1/inventory/checks/{id}/complete - 完成盘点
- DELETE /api/v1/inventory/checks/{id} - 删除盘点单

#### 3.2.5 进销存报表
- GET /api/v1/inventory/reports/summary - 进销存汇总
- GET /api/v1/inventory/reports/turnover - 库存周转率
- GET /api/v1/inventory/reports/sales - 销售统计
- GET /api/v1/inventory/reports/purchases - 采购统计

### 3.3 前端页面设计

#### 3.3.1 供应商管理页面
- 供应商列表（支持搜索、筛选）
- 新增/编辑供应商弹窗
- 供应商详情页面

#### 3.3.2 采购管理页面
- 采购单列表（支持按供应商、日期、状态筛选）
- 采购单详情页面
- 创建/编辑采购单页面
- 采购单审核和入库操作

#### 3.3.3 库存流水页面
- 库存流水列表（支持按药品、日期、类型筛选）
- 流水详情查看

#### 3.3.4 库存盘点页面
- 盘点单列表
- 创建盘点单页面
- 盘点明细录入
- 盘点完成和调整

#### 3.3.5 进销存报表页面
- 进销存汇总报表（图表展示）
- 库存周转率分析
- 销售统计报表
- 采购统计报表

## 四、边界确认

### 4.1 包含范围
- ✅ 供应商管理
- ✅ 采购管理（采购单、采购明细、入库）
- ✅ 库存流水记录
- ✅ 库存盘点
- ✅ 进销存报表

### 4.2 不包含范围
- ❌ 销售管理（使用现有的发药功能）
- ❌ 财务核算（属于财务模块）
- ❌ 供应商结算（属于财务模块）

### 4.3 与现有模块的关系
- **药房模块**: 扩展库存管理功能，增加采购、盘点等
- **诊疗模块**: 发药功能产生销售记录，自动记录库存流水
- **报表模块**: 进销存报表作为报表模块的一部分

## 五、疑问澄清

### 5.1 采购流程
**问题**: 采购流程是否需要多级审核？
**假设**: 单级审核即可，采购单创建后需要审核，审核通过后才能入库。

### 5.2 库存流水
**问题**: 是否需要记录所有库存变动？
**假设**: 是，所有库存变动（采购入库、销售出库、盘点调整等）都需要记录。

### 5.3 盘点功能
**问题**: 盘点是否需要审批流程？
**假设**: 不需要，盘点完成后直接调整库存。

### 5.4 销售管理
**问题**: 销售管理是否使用现有的发药功能？
**假设**: 是，发药即销售，通过发药记录自动生成销售数据。

## 六、验收标准

### 6.1 功能验收
- ✅ 供应商管理功能完整
- ✅ 采购单管理功能完整（创建、审核、入库）
- ✅ 库存流水记录完整
- ✅ 库存盘点功能正常
- ✅ 进销存报表数据准确

### 6.2 技术验收
- ✅ 数据模型设计合理
- ✅ API接口规范统一
- ✅ 前后端集成正常
- ✅ 多租户隔离生效
- ✅ 数据安全（加密、审计）

---

**文档创建时间**: 2024-12-19  
**状态**: 待确认

