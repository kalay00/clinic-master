# 数据库配置统一性修复报告

## 一、修复内容

### 1.1 更新 env.example ✅

**修改内容**：
- 添加了 `DATABASE_URL` 和 `REDIS_URL` 配置
- 保留了单独参数配置（向后兼容）
- 添加了注释说明 Docker 和本地环境的区别

**配置示例**：
```env
# Docker环境（容器内）
DATABASE_URL=postgresql://his_user:his_password@postgres:5432/his_db
REDIS_URL=redis://:redis_password@redis:6379/0

# 本地环境（宿主机）
# DATABASE_URL=postgresql://his_user:his_password@localhost:5432/his_db
# REDIS_URL=redis://:redis_password@localhost:6379/0
```

### 1.2 更新 config.py ✅

**修改内容**：
- 添加了单独参数配置（`POSTGRES_HOST`, `POSTGRES_USER` 等）
- 实现了自动构建 `DATABASE_URL` 和 `REDIS_URL` 的逻辑
- 支持两种配置方式：
  1. 直接提供 URL（优先级高）
  2. 提供单独参数（自动构建）

**实现逻辑**：
```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    
    # 如果没有提供DATABASE_URL，从单独参数构建
    if not self.DATABASE_URL:
        self.DATABASE_URL = (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # 如果没有提供REDIS_URL，从单独参数构建
    if not self.REDIS_URL:
        if self.REDIS_PASSWORD:
            self.REDIS_URL = (
                f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )
        else:
            self.REDIS_URL = (
                f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )
```

### 1.3 更新 docker-compose.yml ✅

**修改内容**：
- 添加了应用服务配置示例（注释状态）
- 展示了如何在 Docker 环境中配置环境变量

## 二、配置方式

### 2.1 Docker 环境配置

**方式1：使用 env.example（推荐）**

```bash
# 复制配置文件
cp env.example .env

# 编辑 .env 文件，确保使用容器服务名
POSTGRES_HOST=postgres
REDIS_HOST=redis
```

**方式2：直接设置 DATABASE_URL**

```bash
# .env 文件
DATABASE_URL=postgresql://his_user:his_password@postgres:5432/his_db
REDIS_URL=redis://:redis_password@redis:6379/0
```

### 2.2 本地环境配置

**方式1：使用 env.example**

```bash
# 复制配置文件
cp env.example .env

# 编辑 .env 文件，修改为 localhost
POSTGRES_HOST=localhost
REDIS_HOST=localhost
```

**方式2：直接设置 DATABASE_URL**

```bash
# .env 文件
DATABASE_URL=postgresql://his_user:his_password@localhost:5432/his_db
REDIS_URL=redis://:redis_password@localhost:6379/0
```

## 三、配置优先级

1. **环境变量**（最高优先级）
   - 系统环境变量
   - Docker 容器环境变量

2. **.env 文件**
   - 项目根目录的 `.env` 文件

3. **config.py 默认值**（最低优先级）
   - 类中定义的默认值

## 四、验证配置

### 4.1 检查配置

```python
from app.core.config import settings

# 检查数据库连接字符串
print(f"DATABASE_URL: {settings.DATABASE_URL}")

# 检查Redis连接字符串
print(f"REDIS_URL: {settings.REDIS_URL}")
```

### 4.2 测试连接

```bash
# 测试 PostgreSQL 连接
psql -h localhost -p 5432 -U his_user -d his_db

# 测试 Redis 连接
redis-cli -h localhost -p 6379 -a redis_password ping
```

## 五、部署场景

### 5.1 场景1：应用在 Docker 容器内运行

**配置**：
```env
POSTGRES_HOST=postgres
REDIS_HOST=redis
```

**说明**：使用 Docker 网络中的服务名

### 5.2 场景2：应用在宿主机运行，数据库在 Docker 中

**配置**：
```env
POSTGRES_HOST=localhost
REDIS_HOST=localhost
```

**说明**：通过端口映射访问（localhost:5432, localhost:6379）

### 5.3 场景3：应用和数据库都在宿主机

**配置**：
```env
POSTGRES_HOST=localhost
REDIS_HOST=localhost
```

**说明**：直接连接本地服务

## 六、注意事项

1. **Docker 环境**：
   - 使用容器服务名（`postgres`, `redis`）
   - 确保应用和数据库在同一 Docker 网络中

2. **本地环境**：
   - 使用 `localhost`
   - 确保端口映射正确

3. **生产环境**：
   - 使用环境变量或配置管理服务
   - 不要将敏感信息提交到代码仓库

4. **配置验证**：
   - 启动前检查配置是否正确
   - 使用健康检查接口验证连接

## 七、统一性检查结果

✅ **配置已统一**：
- 支持 Docker 和本地两种环境
- 支持 URL 和单独参数两种配置方式
- 自动构建逻辑完整
- 向后兼容

## 八、总结

项目现在支持统一的数据库配置：
- ✅ PostgreSQL 和 Redis 都使用统一的配置方式
- ✅ 支持 Docker 和本地环境
- ✅ 支持多种配置方式（URL 或单独参数）
- ✅ 自动构建逻辑完整

**建议**：在部署时根据实际环境选择合适的配置方式。

