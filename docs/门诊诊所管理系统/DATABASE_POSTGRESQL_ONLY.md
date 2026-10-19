# PostgreSQL数据库专用配置说明

## 一、项目要求

根据项目说明文档，**项目仅支持PostgreSQL数据库，不支持SQLite**。

### 1.1 数据库选择
- **主数据库**: PostgreSQL 15+
- **缓存**: Redis 7+
- **消息队列**: RabbitMQ

### 1.2 为什么使用PostgreSQL
1. **多租户支持**: PostgreSQL的JSONB类型和行级安全特性更适合多租户架构
2. **数据类型支持**: 
   - JSONB类型：支持索引和查询优化
   - ARRAY类型：原生数组支持
   - UUID类型：原生UUID支持
3. **性能**: 适合生产环境的高并发场景
4. **功能完整性**: 支持复杂查询、事务、外键约束等

## 二、代码修改

### 2.1 已移除的SQLite支持

#### ✅ backend/app/core/database.py
- **移除**: SQLite连接池参数的条件判断
- **移除**: SQLite的`check_same_thread`参数
- **添加**: PostgreSQL数据库URL验证

#### ✅ backend/app/core/db_types.py
- **移除**: SQLite适配器逻辑
- **更新**: JSONBType和ArrayType仅支持PostgreSQL
- **添加**: 非PostgreSQL数据库时抛出错误

#### ✅ backend/app/core/config.py
- **添加**: DATABASE_URL验证，确保使用PostgreSQL

#### ✅ tests/conftest.py
- **移除**: SQLite内存数据库配置
- **更新**: 使用PostgreSQL测试数据库

#### ✅ run_tests.sh
- **移除**: SQLite数据库URL设置
- **更新**: 使用PostgreSQL测试数据库

### 2.2 数据库配置验证

所有数据库配置都会验证：
- DATABASE_URL必须以`postgresql://`开头
- 如果配置了非PostgreSQL数据库，会抛出`ValueError`异常

## 三、测试数据库配置

### 3.1 测试环境要求

测试也需要PostgreSQL数据库，不能使用SQLite内存数据库。

### 3.2 测试数据库配置

```bash
# 方式1：使用环境变量
export TEST_DATABASE_URL="postgresql://his_user:his_password@localhost:5432/his_test_db"

# 方式2：使用默认配置
# 默认使用: postgresql://his_user:his_password@localhost:5432/his_test_db
```

### 3.3 创建测试数据库

```bash
# 连接到PostgreSQL
psql -U his_user -d postgres

# 创建测试数据库
CREATE DATABASE his_test_db;
\q
```

## 四、环境变量配置

### 4.1 生产环境

```bash
# .env文件
DATABASE_URL=postgresql://his_user:his_password@postgres:5432/his_db
```

### 4.2 开发环境

```bash
# .env文件
DATABASE_URL=postgresql://his_user:his_password@localhost:5432/his_db
```

### 4.3 测试环境

```bash
# 测试环境变量
TEST_DATABASE_URL=postgresql://his_user:his_password@localhost:5432/his_test_db
```

## 五、错误处理

### 5.1 数据库类型错误

如果配置了非PostgreSQL数据库，系统会在启动时抛出错误：

```
ValueError: 不支持的数据库类型。项目要求使用PostgreSQL数据库，当前配置: sqlite:///:memory:...
```

### 5.2 解决方案

1. 检查`.env`文件中的`DATABASE_URL`配置
2. 确保使用`postgresql://`协议
3. 确保PostgreSQL服务正在运行

## 六、迁移指南

### 6.1 从SQLite迁移到PostgreSQL

如果之前使用SQLite，需要：

1. **安装PostgreSQL**
   ```bash
   # 使用Docker
   docker-compose up -d postgres
   ```

2. **创建数据库**
   ```bash
   createdb -U his_user his_db
   ```

3. **迁移数据**（如果有）
   - 使用pgloader或其他工具迁移数据
   - 或重新初始化数据库

4. **更新配置**
   - 修改`.env`文件中的`DATABASE_URL`
   - 确保使用PostgreSQL连接字符串

## 七、验证检查

### 7.1 代码检查

运行以下命令检查是否还有SQLite引用：

```bash
# 检查Python代码
grep -r "sqlite" backend/ --include="*.py"

# 检查配置文件
grep -r "sqlite" backend/ --include="*.ini" --include="*.conf"
```

### 7.2 配置验证

```python
from app.core.config import settings
from app.core.database import engine

# 验证数据库URL
assert settings.DATABASE_URL.startswith("postgresql"), "必须使用PostgreSQL"

# 测试连接
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("SELECT version()"))
    print(f"PostgreSQL版本: {result.fetchone()[0]}")
```

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  
**状态**: ✅ 已完成SQLite移除，强制使用PostgreSQL

