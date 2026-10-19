# 版本升级策略文档

## 一、版本开发策略

### 1.1 开发目录选择

#### 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **方案A：同一目录开发（推荐）** | ✅ 代码复用率高<br>✅ 版本管理简单<br>✅ 数据迁移方便<br>✅ 维护成本低 | ⚠️ 需要版本分支管理<br>⚠️ 需要谨慎处理破坏性变更 | ⭐⭐⭐⭐⭐ |
| **方案B：单独目录开发** | ✅ 版本隔离清晰<br>✅ 可以并行开发 | ❌ 代码重复<br>❌ 数据迁移复杂<br>❌ 维护成本高<br>❌ 难以复用代码 | ⭐⭐ |

#### 推荐方案：**同一目录 + Git分支管理**

**理由**：
1. ✅ 现有系统已有完善的Alembic迁移机制
2. ✅ Git分支可以很好地管理版本
3. ✅ 代码复用率高，避免重复开发
4. ✅ 数据迁移通过Alembic统一管理
5. ✅ 维护成本低，只需维护一套代码

### 1.2 Git分支策略

#### 1.2.1 分支结构

```
main (生产环境)
├── v1.0 (v1.0稳定版本)
│   └── v1.0.1 (v1.0补丁版本)
│
├── develop (开发主分支)
│   ├── feature/v2.0-xxx (v2.0功能分支)
│   ├── feature/regulatory-compliance (监管合规功能)
│   └── feature/user-experience (用户体验优化)
│
└── release/v2.0 (v2.0发布分支)
    ├── v2.0-alpha (内测版本)
    ├── v2.0-beta (公测版本)
    └── v2.0-rc (候选版本)
```

#### 1.2.2 分支命名规范

- **主分支**: `main` (生产环境)
- **稳定版本**: `v1.0`, `v2.0` (稳定版本标签)
- **开发分支**: `develop` (开发主分支)
- **功能分支**: `feature/v2.0-xxx` (v2.0功能开发)
- **发布分支**: `release/v2.0` (v2.0发布准备)
- **热修复**: `hotfix/v1.0-xxx` (v1.0紧急修复)

### 1.3 版本号管理

#### 1.3.1 版本号规范

采用 [语义化版本](https://semver.org/lang/zh-CN/) 规范：`主版本号.次版本号.修订号`

- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

**示例**:
- `v1.0.0` - v1.0正式版
- `v1.0.1` - v1.0补丁版本
- `v2.0.0-alpha.1` - v2.0内测版本1
- `v2.0.0-beta.1` - v2.0公测版本1
- `v2.0.0-rc.1` - v2.0候选版本1
- `v2.0.0` - v2.0正式版

#### 1.3.2 版本号配置位置

**后端版本号**: `backend/app/core/config.py`
```python
VERSION: str = "2.0.0"  # 更新版本号
```

**前端版本号**: 可在 `frontend/index.html` 或配置文件中管理

## 二、数据迁移策略

### 2.1 数据库迁移工具：Alembic

#### 2.1.1 现有迁移机制

✅ **已具备**:
- Alembic迁移工具已配置
- 已有10个迁移脚本
- 支持版本控制和回滚

**迁移脚本位置**: `backend/alembic/versions/`

#### 2.1.2 v2.0迁移策略

**原则**: 
- ✅ 所有数据库变更通过Alembic迁移脚本管理
- ✅ 迁移脚本可回滚（downgrade函数）
- ✅ 迁移前必须备份数据库
- ✅ 迁移脚本必须经过测试

### 2.2 数据迁移方案

#### 2.2.1 新增表迁移

**场景**: v2.0新增监管相关表

**步骤**:
1. 创建数据模型（`backend/app/models/`）
2. 生成迁移脚本：
   ```bash
   cd backend
   alembic revision --autogenerate -m "add_regulatory_tables"
   ```
3. 检查并修改迁移脚本
4. 测试迁移：
   ```bash
   alembic upgrade head  # 升级
   alembic downgrade -1  # 回滚测试
   ```

**示例迁移脚本**:
```python
"""add regulatory compliance tables

Revision ID: 002_regulatory
Revises: 001_initial
Create Date: 2025-01-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002_regulatory'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 创建医保违规记录表
    op.create_table(
        'violation_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('violation_type', sa.String(50), nullable=False),
        sa.Column('violation_desc', sa.Text),
        sa.Column('bill_id', postgresql.UUID(as_uuid=True)),
        sa.Column('prescription_id', postgresql.UUID(as_uuid=True)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['bill_id'], ['bills.id']),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id']),
    )
    
    # 创建索引
    op.create_index('ix_violation_records_tenant_id', 'violation_records', ['tenant_id'])
    op.create_index('ix_violation_records_type', 'violation_records', ['violation_type'])

def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_violation_records_type', 'violation_records')
    op.drop_index('ix_violation_records_tenant_id', 'violation_records')
    # 删除表
    op.drop_table('violation_records')
```

#### 2.2.2 表结构扩展迁移

**场景**: 在现有表上增加字段

**步骤**:
1. 修改数据模型，增加字段
2. 生成迁移脚本：
   ```bash
   alembic revision --autogenerate -m "add_regulatory_fields_to_bills"
   ```
3. 检查迁移脚本，确保：
   - 新字段有默认值或允许NULL
   - 有数据迁移逻辑（如需要）
4. 测试迁移

**示例**: 在`bills`表中增加医保相关字段
```python
def upgrade() -> None:
    # 检查字段是否已存在
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('bills')]
    
    if 'medical_insurance_amount' not in columns:
        op.add_column('bills', 
            sa.Column('medical_insurance_amount', sa.Numeric(10, 2), nullable=True, comment='医保报销金额')
        )
    
    if 'medical_insurance_ratio' not in columns:
        op.add_column('bills',
            sa.Column('medical_insurance_ratio', sa.Numeric(5, 2), nullable=True, comment='医保报销比例')
        )
    
    # 如果有现有数据，设置默认值
    op.execute("UPDATE bills SET medical_insurance_amount = 0 WHERE medical_insurance_amount IS NULL")
    op.execute("UPDATE bills SET medical_insurance_ratio = 0 WHERE medical_insurance_ratio IS NULL")

def downgrade() -> None:
    op.drop_column('bills', 'medical_insurance_ratio')
    op.drop_column('bills', 'medical_insurance_amount')
```

#### 2.2.3 数据迁移（数据转换）

**场景**: 需要转换现有数据

**步骤**:
1. 在迁移脚本的`upgrade()`函数中添加数据迁移逻辑
2. 确保数据迁移可回滚（在`downgrade()`中实现）

**示例**: 为现有药品添加追溯码（生成临时追溯码）
```python
def upgrade() -> None:
    # 先添加字段
    op.add_column('drugs', 
        sa.Column('trace_code', sa.String(100), nullable=True, comment='药品追溯码')
    )
    
    # 为现有药品生成临时追溯码（格式：DRUG-{drug_id}）
    op.execute("""
        UPDATE drugs 
        SET trace_code = 'DRUG-' || id::text 
        WHERE trace_code IS NULL
    """)

def downgrade() -> None:
    op.drop_column('drugs', 'trace_code')
```

### 2.3 数据备份策略

#### 2.3.1 备份时机

**必须备份的时机**:
1. ✅ 执行数据库迁移前
2. ✅ 版本升级前
3. ✅ 重大数据变更前
4. ✅ 定期备份（每日/每周）

#### 2.3.2 备份方法

**方法1: PostgreSQL原生备份（推荐）**

```bash
# 完整备份
pg_dump -h localhost -U his_user -d his_db -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# 仅备份数据（不含结构）
pg_dump -h localhost -U his_user -d his_db -F c -a -f backup_data_$(date +%Y%m%d_%H%M%S).dump

# 仅备份结构（不含数据）
pg_dump -h localhost -U his_user -d his_db -F c -s -f backup_schema_$(date +%Y%m%d_%H%M%S).dump
```

**方法2: Docker容器备份**

```bash
# 备份PostgreSQL数据卷
docker exec his_postgres pg_dump -U his_user -d his_db -F c > backup_$(date +%Y%m%d_%H%M%S).dump

# 或备份整个数据卷
docker run --rm -v his_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

**方法3: 自动化备份脚本**

创建 `scripts/backup_database.sh`:
```bash
#!/bin/bash
# 数据库备份脚本

BACKUP_DIR="/backups/his"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/his_backup_${DATE}.dump"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 执行备份
docker exec his_postgres pg_dump -U his_user -d his_db -F c > ${BACKUP_FILE}

# 压缩备份文件
gzip ${BACKUP_FILE}

# 删除7天前的备份
find ${BACKUP_DIR} -name "*.dump.gz" -mtime +7 -delete

echo "备份完成: ${BACKUP_FILE}.gz"
```

#### 2.3.3 备份恢复

```bash
# 恢复备份
pg_restore -h localhost -U his_user -d his_db -c backup_20250109_120000.dump

# Docker容器恢复
docker exec -i his_postgres pg_restore -U his_user -d his_db -c < backup_20250109_120000.dump
```

### 2.4 数据迁移检查清单

#### 2.4.1 迁移前检查

- [ ] 数据库已备份
- [ ] 迁移脚本已测试（测试环境）
- [ ] 迁移脚本可回滚（downgrade函数已实现）
- [ ] 数据迁移逻辑已测试
- [ ] 应用程序已停止（生产环境）
- [ ] 迁移计划已制定
- [ ] 回滚计划已制定

#### 2.4.2 迁移后检查

- [ ] 数据库结构正确
- [ ] 数据完整性验证
- [ ] 索引创建正确
- [ ] 外键约束正确
- [ ] 应用程序启动正常
- [ ] 功能测试通过
- [ ] 性能测试通过

## 三、版本升级流程

### 3.1 开发环境升级流程

#### 3.1.1 准备工作

```bash
# 1. 切换到v2.0开发分支
git checkout develop
git pull origin develop

# 2. 创建v2.0功能分支
git checkout -b feature/v2.0-regulatory-compliance

# 3. 备份开发数据库
./scripts/backup_database.sh
```

#### 3.1.2 执行迁移

```bash
# 1. 进入后端目录
cd backend

# 2. 检查当前迁移版本
alembic current

# 3. 查看待执行的迁移
alembic heads

# 4. 执行迁移
alembic upgrade head

# 5. 验证迁移结果
alembic current
```

#### 3.1.3 测试验证

```bash
# 1. 启动应用
cd backend
uvicorn app.main:app --reload

# 2. 运行测试
pytest tests/

# 3. 手动测试新功能
# 访问 http://localhost:8000
```

### 3.2 测试环境升级流程

#### 3.2.1 升级前准备

```bash
# 1. 通知相关人员
# 2. 停止应用服务
docker-compose down

# 3. 备份数据库
./scripts/backup_database.sh

# 4. 备份应用代码
git tag v1.0-backup-$(date +%Y%m%d)
```

#### 3.2.2 执行升级

```bash
# 1. 切换到v2.0分支
git checkout release/v2.0-beta
git pull origin release/v2.0-beta

# 2. 更新依赖
cd backend
pip install -r requirements.txt

# 3. 执行数据库迁移
alembic upgrade head

# 4. 启动应用
docker-compose up -d

# 5. 检查服务状态
docker-compose ps
docker-compose logs backend
```

#### 3.2.3 验证测试

```bash
# 1. 健康检查
curl http://localhost:8000/api

# 2. 功能测试
# 执行测试用例

# 3. 性能测试
# 检查响应时间、资源使用等
```

### 3.3 生产环境升级流程

#### 3.3.1 升级前准备（提前1周）

**1. 制定升级计划**
- [ ] 确定升级时间窗口（建议业务低峰期）
- [ ] 通知用户升级时间
- [ ] 准备回滚方案
- [ ] 准备应急联系人

**2. 备份准备**
```bash
# 完整备份
./scripts/backup_database.sh

# 备份应用代码
git tag v1.0-production-backup-$(date +%Y%m%d)

# 备份配置文件
cp backend/app/core/config.py config.py.backup
```

**3. 测试环境验证**
- [ ] 在测试环境完整测试升级流程
- [ ] 验证所有功能正常
- [ ] 验证性能指标正常
- [ ] 验证数据完整性

#### 3.3.2 执行升级（升级窗口）

**1. 停止服务**
```bash
# 停止应用服务
docker-compose down

# 或停止systemd服务
systemctl stop his-backend
```

**2. 执行升级**
```bash
# 1. 切换到v2.0版本
git checkout v2.0.0
git pull origin v2.0.0

# 2. 更新依赖
cd backend
pip install -r requirements.txt

# 3. 执行数据库迁移（关键步骤）
alembic upgrade head

# 4. 验证迁移结果
alembic current
psql -U his_user -d his_db -c "\dt"  # 检查表结构

# 5. 启动服务
docker-compose up -d
# 或
systemctl start his-backend
```

**3. 验证服务**
```bash
# 1. 检查服务状态
docker-compose ps
# 或
systemctl status his-backend

# 2. 检查日志
docker-compose logs backend
# 或
journalctl -u his-backend -f

# 3. 健康检查
curl http://localhost:8000/api
```

#### 3.3.3 升级后验证

**1. 功能验证**
- [ ] 登录功能正常
- [ ] 核心业务流程正常
- [ ] 新功能正常
- [ ] 数据查询正常

**2. 性能验证**
- [ ] 响应时间正常
- [ ] 数据库查询正常
- [ ] 资源使用正常

**3. 数据验证**
- [ ] 数据完整性检查
- [ ] 数据一致性检查
- [ ] 关键数据抽样验证

#### 3.3.4 回滚方案（如需要）

**回滚条件**:
- 升级后出现严重bug
- 数据丢失或损坏
- 性能严重下降
- 无法快速修复

**回滚步骤**:
```bash
# 1. 停止服务
docker-compose down

# 2. 恢复数据库备份
pg_restore -h localhost -U his_user -d his_db -c backup_20250109_120000.dump

# 3. 回滚数据库迁移
cd backend
alembic downgrade <previous_revision>

# 4. 切换回v1.0代码
git checkout v1.0.0

# 5. 启动服务
docker-compose up -d
```

## 四、数据安全保障措施

### 4.1 数据备份策略

#### 4.1.1 备份频率

| 备份类型 | 频率 | 保留时间 | 位置 |
|---------|------|---------|------|
| 完整备份 | 每日 | 7天 | 本地+远程 |
| 增量备份 | 每小时 | 24小时 | 本地 |
| 迁移前备份 | 每次迁移前 | 30天 | 本地+远程 |
| 版本升级备份 | 每次升级前 | 90天 | 本地+远程 |

#### 4.1.2 备份存储

**本地备份**:
- 位置: `/backups/his/`
- 格式: `his_backup_YYYYMMDD_HHMMSS.dump.gz`

**远程备份**:
- 云存储（如阿里云OSS、AWS S3）
- 异地服务器
- 定期同步

#### 4.1.3 备份验证

```bash
# 验证备份文件完整性
pg_restore --list backup_20250109_120000.dump | head -20

# 测试恢复（到临时数据库）
createdb his_db_test
pg_restore -d his_db_test backup_20250109_120000.dump
```

### 4.2 数据迁移安全保障

#### 4.2.1 迁移脚本安全措施

**1. 幂等性保证**
- 迁移脚本可以重复执行而不出错
- 使用`IF NOT EXISTS`检查

**2. 可回滚性**
- 每个迁移脚本必须实现`downgrade()`函数
- 回滚脚本必须经过测试

**3. 数据完整性**
- 迁移过程中使用事务
- 迁移失败自动回滚

**4. 性能考虑**
- 大数据量迁移分批处理
- 避免长时间锁表

#### 4.2.2 迁移前数据验证

```sql
-- 检查数据完整性
SELECT COUNT(*) FROM patients;
SELECT COUNT(*) FROM bills;
SELECT COUNT(*) FROM prescriptions;

-- 检查外键完整性
SELECT * FROM bills WHERE patient_id NOT IN (SELECT id FROM patients);

-- 检查数据一致性
SELECT COUNT(*) FROM bills WHERE total_amount != (
    SELECT SUM(total_price) FROM bill_items WHERE bill_id = bills.id
);
```

### 4.3 版本兼容性保障

#### 4.3.1 API兼容性

**原则**: v2.0 API应该向后兼容v1.0

**措施**:
- ✅ 不删除现有API端点
- ✅ 不修改现有API响应格式
- ✅ 新功能通过新API端点提供
- ✅ 废弃的API标记为`deprecated`，保留一段时间

**示例**:
```python
# v1.0 API（保留）
@router.get("/bills", deprecated=True)
async def list_bills_v1(...):
    """v1.0 API，已废弃，请使用v2版本"""
    ...

# v2.0 API（新）
@router.get("/bills/v2")
async def list_bills_v2(...):
    """v2.0 API，支持监管数据"""
    ...
```

#### 4.3.2 数据模型兼容性

**原则**: 数据库变更向后兼容

**措施**:
- ✅ 新增字段允许NULL或设置默认值
- ✅ 不删除现有字段（标记为废弃）
- ✅ 不修改现有字段类型（如需要，创建新字段）

### 4.4 监控和告警

#### 4.4.1 升级过程监控

**监控指标**:
- 数据库连接数
- 数据库查询时间
- 应用响应时间
- 错误日志
- 资源使用率

**告警设置**:
- 数据库连接失败
- 迁移脚本执行失败
- 应用启动失败
- 错误率超过阈值

#### 4.4.2 升级后监控

**监控周期**: 升级后24-48小时重点监控

**监控内容**:
- 系统稳定性
- 功能正常性
- 性能指标
- 错误日志
- 用户反馈

## 五、版本升级检查清单

### 5.1 升级前检查清单

#### 5.1.1 代码准备
- [ ] v2.0代码已合并到发布分支
- [ ] 代码已通过代码审查
- [ ] 所有测试通过
- [ ] 文档已更新

#### 5.1.2 数据库准备
- [ ] 迁移脚本已准备
- [ ] 迁移脚本已测试
- [ ] 迁移脚本可回滚
- [ ] 数据库备份已创建

#### 5.1.3 环境准备
- [ ] 测试环境已升级并验证
- [ ] 生产环境配置已准备
- [ ] 依赖包已更新
- [ ] 配置文件已更新

#### 5.1.4 人员准备
- [ ] 升级计划已制定
- [ ] 相关人员已通知
- [ ] 应急联系人已准备
- [ ] 回滚方案已准备

### 5.2 升级中检查清单

- [ ] 服务已停止
- [ ] 数据库备份已完成
- [ ] 代码已更新
- [ ] 依赖已安装
- [ ] 数据库迁移已执行
- [ ] 迁移结果已验证
- [ ] 服务已启动
- [ ] 服务状态正常

### 5.3 升级后检查清单

#### 5.3.1 功能检查
- [ ] 登录功能正常
- [ ] 核心业务流程正常
- [ ] 新功能正常
- [ ] 数据查询正常
- [ ] 报表功能正常

#### 5.3.2 性能检查
- [ ] 响应时间正常
- [ ] 数据库查询正常
- [ ] 资源使用正常
- [ ] 无内存泄漏

#### 5.3.3 数据检查
- [ ] 数据完整性
- [ ] 数据一致性
- [ ] 关键数据验证
- [ ] 历史数据可访问

## 六、最佳实践建议

### 6.1 开发阶段

1. **使用Git分支管理版本**
   - 主分支保持稳定
   - 功能开发使用功能分支
   - 定期合并到开发分支

2. **数据库变更使用Alembic**
   - 所有数据库变更通过迁移脚本
   - 迁移脚本必须可回滚
   - 迁移脚本必须测试

3. **保持API兼容性**
   - 新功能通过新API提供
   - 废弃API标记deprecated
   - 保留废弃API一段时间

### 6.2 测试阶段

1. **充分测试**
   - 单元测试
   - 集成测试
   - 端到端测试
   - 性能测试

2. **测试环境验证**
   - 在测试环境完整测试升级流程
   - 验证所有功能
   - 验证数据迁移

### 6.3 生产部署

1. **制定详细计划**
   - 确定升级时间窗口
   - 准备回滚方案
   - 通知相关人员

2. **充分备份**
   - 数据库完整备份
   - 代码版本备份
   - 配置文件备份

3. **逐步验证**
   - 升级后立即验证
   - 持续监控24-48小时
   - 收集用户反馈

## 七、常见问题处理

### 7.1 迁移失败处理

**问题**: 数据库迁移执行失败

**处理步骤**:
1. 检查错误日志
2. 分析失败原因
3. 修复迁移脚本
4. 回滚到迁移前状态
5. 重新执行迁移

**预防措施**:
- 迁移脚本必须测试
- 迁移前备份数据库
- 迁移脚本使用事务

### 7.2 数据丢失处理

**问题**: 升级后数据丢失

**处理步骤**:
1. 立即停止服务
2. 恢复数据库备份
3. 回滚代码版本
4. 分析丢失原因
5. 修复问题后重新升级

**预防措施**:
- 升级前完整备份
- 迁移脚本充分测试
- 升级后数据验证

### 7.3 性能下降处理

**问题**: 升级后性能下降

**处理步骤**:
1. 分析性能瓶颈
2. 检查数据库索引
3. 优化查询语句
4. 必要时回滚

**预防措施**:
- 升级前性能测试
- 检查数据库索引
- 监控性能指标

## 八、总结

### 8.1 推荐方案

✅ **同一目录 + Git分支管理 + Alembic迁移**

**优势**:
- 代码复用率高
- 版本管理清晰
- 数据迁移安全
- 维护成本低

### 8.2 关键要点

1. **数据安全第一**
   - 升级前必须备份
   - 迁移脚本必须可回滚
   - 升级后必须验证

2. **充分测试**
   - 测试环境完整测试
   - 迁移脚本充分测试
   - 功能充分测试

3. **制定计划**
   - 详细的升级计划
   - 明确的回滚方案
   - 充分的应急准备

### 8.3 升级流程总结

```
1. 开发阶段
   ├── Git分支管理
   ├── Alembic迁移脚本
   └── 功能测试

2. 测试阶段
   ├── 测试环境升级
   ├── 功能验证
   └── 性能验证

3. 生产部署
   ├── 备份数据库
   ├── 执行迁移
   ├── 启动服务
   └── 验证功能

4. 监控维护
   ├── 持续监控
   ├── 收集反馈
   └── 及时处理问题
```

---

**文档版本**: v1.0  
**创建时间**: 2025-01-09  
**最后更新**: 2025-01-09

