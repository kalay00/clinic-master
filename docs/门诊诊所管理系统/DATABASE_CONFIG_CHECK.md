# 数据库配置统一性检查报告

## 一、检查结果

### 1.1 当前状态 ⚠️

**问题**：配置存在不一致，可能导致 Docker 环境连接失败

#### 问题1：DATABASE_URL 配置不一致

- **docker-compose.yml**: 使用服务名 `postgres`（容器间通信）
- **env.example**: 使用服务名 `postgres`（适用于 Docker 环境）
- **config.py 默认值**: 使用 `localhost`（适用于本地开发）

**影响**：
- 应用在 Docker 容器内运行时，使用 `localhost` 无法连接到 PostgreSQL
- 应用在宿主机运行时，使用 `postgres` 无法连接

#### 问题2：REDIS_HOST 配置不一致

- **docker-compose.yml**: 服务名 `redis`
- **env.example**: 使用服务名 `redis`
- **config.py 默认值**: 使用 `localhost`

**影响**：同上

#### 问题3：DATABASE_URL 构建方式

- **env.example**: 没有 `DATABASE_URL`，只有单独的参数（`POSTGRES_HOST`, `POSTGRES_USER` 等）
- **config.py**: 直接使用 `DATABASE_URL`，没有从单独参数构建的逻辑

**影响**：如果只配置了单独参数，无法自动构建 `DATABASE_URL`

### 1.2 配置来源优先级

当前配置使用 `pydantic-settings`，优先级：
1. 环境变量（最高优先级）
2. `.env` 文件
3. 类默认值（最低优先级）

## 二、推荐方案

### 2.1 方案A：统一使用环境变量（推荐）

**优点**：
- 灵活，支持多种部署方式
- Docker 和本地开发都可以正常工作

**实现**：
1. 更新 `env.example` 添加 `DATABASE_URL` 和 `REDIS_URL`
2. 更新 `config.py` 支持从单独参数自动构建 URL
3. 更新 `docker-compose.yml` 添加环境变量

### 2.2 方案B：区分 Docker 和本地配置

**优点**：
- 配置清晰，针对性强

**缺点**：
- 需要维护两套配置
- 容易混淆

## 三、当前配置检查

### 3.1 Docker 配置

**docker-compose.yml** ✅
- 定义了 PostgreSQL 服务（`postgres`）
- 定义了 Redis 服务（`redis`）
- 定义了 RabbitMQ 服务（`rabbitmq`）
- 使用统一的网络 `his_network`

### 3.2 环境变量配置

**env.example** ⚠️
- 使用 Docker 容器服务名（`postgres`, `redis`, `rabbitmq`）
- 缺少 `DATABASE_URL` 和 `REDIS_URL`
- 只提供了单独的参数

### 3.3 应用配置

**config.py** ⚠️
- 默认值使用 `localhost`（适用于本地开发）
- 没有从单独参数构建 URL 的逻辑
- 支持从环境变量读取（✅）

## 四、建议修复

### 4.1 更新 env.example

添加 `DATABASE_URL` 和 `REDIS_URL`，并支持两种模式：
- Docker 模式：使用容器服务名
- 本地模式：使用 localhost

### 4.2 更新 config.py

添加自动构建 URL 的逻辑：
- 如果提供了 `DATABASE_URL`，直接使用
- 如果没有，从单独参数构建
- 支持 Docker 和本地两种模式

### 4.3 更新 docker-compose.yml

添加环境变量，确保应用可以正确连接

## 五、配置检查清单

- [ ] `env.example` 包含完整的数据库配置
- [ ] `config.py` 支持从环境变量读取
- [ ] `config.py` 支持从单独参数构建 URL
- [ ] `docker-compose.yml` 配置正确
- [ ] 部署文档说明配置方式
- [ ] 测试 Docker 环境连接
- [ ] 测试本地环境连接

