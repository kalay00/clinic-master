# 进销存模块测试执行说明

## 一、测试准备

### 1.1 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload
```

### 1.2 确保数据库连接
- PostgreSQL服务运行中
- 数据库连接配置正确

## 二、执行测试

### 2.1 自动化测试
```bash
cd backend
python test_inventory_full.py
```

### 2.2 手动测试步骤

#### 步骤1：创建供应商
1. 访问 http://localhost:8000/views/inventory/suppliers.html
2. 点击"新增供应商"
3. 填写供应商信息并保存
4. 验证供应商出现在列表中

#### 步骤2：创建并入库采购单
1. 访问 http://localhost:8000/views/inventory/purchase-orders.html
2. 点击"新增采购单"
3. 选择供应商
4. 添加采购明细（选择药品、输入数量、单价）
5. 保存采购单
6. 点击"审核"按钮
7. 点击"入库"按钮
8. 验证库存是否更新

#### 步骤3：查看库存流水
1. 访问 http://localhost:8000/views/inventory/transactions.html
2. 验证是否有采购入库的流水记录
3. 验证流水记录的数据是否正确

#### 步骤4：创建并完成盘点
1. 访问 http://localhost:8000/views/inventory/checks.html
2. 点击"新增盘点单"
3. 选择药品（自动获取账面数量）
4. 输入实际数量
5. 保存盘点单
6. 点击"完成盘点"按钮
7. 验证库存是否调整

#### 步骤5：验证数据一致性
1. 查看库存流水，验证所有操作都有记录
2. 验证库存数量与流水记录一致
3. 验证流水记录的连续性

## 三、数据一致性验证

### 3.1 库存数量验证
- 初始库存 + 采购数量 = 入库后库存
- 入库后库存 + 盘点差异 = 盘点后库存

### 3.2 流水记录验证
- 每条操作都有对应的流水记录
- 流水记录的before_quantity和after_quantity正确
- 流水记录连续（前一条的after_quantity = 后一条的before_quantity）

### 3.3 状态流转验证
- 采购单：draft → approved → received
- 盘点单：draft → completed

## 四、测试检查清单

### 4.1 采购流程
- [ ] 创建供应商成功
- [ ] 创建采购单成功
- [ ] 审核采购单成功
- [ ] 入库采购单成功
- [ ] 库存数量更新正确
- [ ] 流水记录创建正确

### 4.2 盘点流程
- [ ] 创建盘点单成功
- [ ] 账面数量自动获取正确
- [ ] 完成盘点成功
- [ ] 库存数量调整正确
- [ ] 流水记录创建正确

### 4.3 数据一致性
- [ ] 库存数量计算正确
- [ ] 流水记录完整
- [ ] 流水记录连续
- [ ] 状态流转正确

---

**测试脚本**: `backend/test_inventory_full.py`  
**测试报告**: `docs/门诊诊所管理系统/INVENTORY_FULL_TEST_REPORT.md`

