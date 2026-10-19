# 测试执行指南

## 一、测试准备

### 1.1 环境准备

确保以下环境已准备好：

```bash
# 1. Python环境（Python 3.9+）
python --version

# 2. 安装测试依赖
pip install pytest pytest-asyncio httpx pytest-cov pytest-html sqlalchemy aiosqlite

# 3. 确保数据库服务运行（可选，单元测试使用内存数据库）
# PostgreSQL和Redis服务（用于集成测试）
```

### 1.2 测试配置

测试配置文件：
- `pytest.ini`: pytest主配置文件
- `tests/conftest.py`: 测试共享配置和fixtures

## 二、测试执行方式

### 2.1 快速执行（推荐）

```bash
# 进入项目根目录
cd /home/laknl/his

# 执行完整测试套件
python tests/run_all_tests.py
```

### 2.2 分类执行

#### 单元测试

```bash
cd backend
pytest tests/unit -v
```

#### 集成测试

```bash
cd backend
pytest tests/integration -v
```

#### 端到端测试

```bash
cd backend
pytest tests/integration/test_e2e_*.py -v
```

### 2.3 特定模块测试

```bash
# 用户服务测试
pytest tests/unit/test_user_service.py -v

# 患者服务测试
pytest tests/unit/test_patient_service.py -v

# 认证API测试
pytest tests/integration/test_api_auth.py -v

# 患者管理API测试
pytest tests/integration/test_api_patients.py -v
```

## 三、测试覆盖率

### 3.1 生成覆盖率报告

```bash
cd backend

# 生成HTML覆盖率报告
pytest tests --cov=app --cov-report=html --cov-report=term

# 查看覆盖率报告
# 打开 test_reports/coverage_html/index.html
```

### 3.2 覆盖率目标

- **单元测试覆盖率**: > 80%
- **集成测试覆盖率**: > 70%
- **总体覆盖率**: > 75%

## 四、测试报告

### 4.1 测试报告位置

测试执行后，报告生成在以下位置：

```
test_reports/
├── unit_test_report.html              # 单元测试报告
├── integration_api_test_report.html   # API集成测试报告
├── e2e_test_report.html               # 端到端测试报告
├── coverage_html/                     # 覆盖率HTML报告
│   └── index.html
├── coverage.xml                        # 覆盖率XML报告
└── test_summary.md                    # 测试总结报告
```

### 4.2 查看测试报告

```bash
# HTML报告可以直接用浏览器打开
# 在项目根目录执行
open test_reports/unit_test_report.html  # macOS
xdg-open test_reports/unit_test_report.html  # Linux
```

## 五、测试标记

### 5.1 使用标记运行特定测试

```bash
# 只运行单元测试
pytest -m unit -v

# 只运行集成测试
pytest -m integration -v

# 只运行端到端测试
pytest -m e2e -v

# 只运行API测试
pytest -m api -v

# 只运行认证测试
pytest -m auth -v

# 排除慢速测试
pytest -m "not slow" -v
```

## 六、测试调试

### 6.1 详细输出

```bash
# 显示详细输出
pytest tests/unit/test_user_service.py -v -s

# 显示最详细输出
pytest tests/unit/test_user_service.py -vv
```

### 6.2 调试模式

```bash
# 失败时进入调试器
pytest tests/unit/test_user_service.py --pdb

# 显示日志
pytest tests/unit/test_user_service.py --log-cli-level=DEBUG
```

### 6.3 运行特定测试

```bash
# 运行特定测试类
pytest tests/unit/test_user_service.py::TestUserService -v

# 运行特定测试方法
pytest tests/unit/test_user_service.py::TestUserService::test_create_user -v
```

## 七、测试执行步骤

### 步骤1: 执行单元测试

```bash
cd backend
pytest tests/unit -v --html=test_reports/unit_test_report.html --self-contained-html
```

### 步骤2: 执行集成测试

```bash
pytest tests/integration/test_api_integration.py -v
pytest tests/integration/test_api_auth.py -v
pytest tests/integration/test_api_patients.py -v
```

### 步骤3: 执行端到端测试

```bash
pytest tests/integration/test_e2e_workflow.py -v
pytest tests/integration/test_e2e_complete_workflow.py -v
```

### 步骤4: 生成覆盖率报告

```bash
pytest tests --cov=app --cov-report=html:test_reports/coverage_html --cov-report=term
```

### 步骤5: 查看测试报告

查看生成的测试报告和覆盖率报告。

## 八、常见问题

### 8.1 数据库连接错误

**问题**: 测试时数据库连接失败

**解决方案**:
- 单元测试使用内存数据库（SQLite），无需配置
- 集成测试需要PostgreSQL，确保数据库服务运行

### 8.2 认证失败

**问题**: 测试中认证失败

**解决方案**:
- 确保测试fixtures正确创建测试用户
- 检查Token生成逻辑

### 8.3 异步测试问题

**问题**: 异步测试执行失败

**解决方案**:
- 确保使用 `@pytest.mark.asyncio` 标记
- 检查 `pytest-asyncio` 已安装
- 检查 `pytest.ini` 中的异步配置

## 九、测试最佳实践

### 9.1 测试前准备

1. 确保所有依赖已安装
2. 检查测试配置文件
3. 确保数据库服务运行（集成测试）

### 9.2 测试执行

1. 先运行单元测试
2. 再运行集成测试
3. 最后运行端到端测试
4. 生成覆盖率报告

### 9.3 测试后

1. 查看测试报告
2. 分析失败用例
3. 修复问题和补充测试
4. 更新测试文档

## 十、持续集成

### 10.1 CI/CD配置

在CI/CD流程中自动执行测试：

```yaml
# 示例：GitHub Actions
- name: Run tests
  run: |
    cd backend
    pip install -r requirements.txt
    pip install pytest pytest-asyncio httpx pytest-cov
    pytest tests --cov=app --cov-report=xml
```

### 10.2 测试报告上传

将测试报告上传到CI/CD平台或测试报告服务。

---

**创建时间**: 2024-12-19  
**最后更新**: 2024-12-19  
