# 门诊诊所管理系统 (HIS)

## 项目简介

门诊诊所管理系统是一款适用于中小型门诊、诊所的综合性管理软件，采用微服务架构，支持多租户多机构。

## 技术栈

- **后端**: Python (FastAPI)
- **前端**: 原生 HTML/CSS/JavaScript
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **消息队列**: RabbitMQ 3
- **容器化**: Docker/Podman

## 开发环境搭建

### 前置要求

- Podman 5.4+ (或 Docker)
- Python 3.9+

### 快速开始

1. **克隆项目**
```bash
git clone https://gitee.com/ttlaknl/outpatient-management-system.git
cd outpatient-management-system
```

2. **配置环境变量**
```bash
cp env.example .env
# 编辑 .env 文件，修改数据库密码等配置
```

3. **启动开发环境**
```bash
# 使用 Podman Compose (如果已安装)
podman-compose up -d

# 或使用 Podman 直接运行
podman-compose up -d
```

4. **验证服务**
```bash
# 检查容器状态
podman ps

# 检查 PostgreSQL
podman exec -it his_postgres psql -U his_user -d his_db -c "SELECT version();"

# 检查 Redis
podman exec -it his_redis redis-cli -a redis_password ping

# 检查 RabbitMQ
podman exec -it his_rabbitmq rabbitmq-diagnostics ping 

# 数据库表结构在后端服务启动时自动创建（参考 FastapiAdmin：lifespan 中 create_all），
# 模型有变更（新增表/列）重启即自动生效，无需手动执行 alembic 迁移。
# 如需手动初始化（建表 + 写入默认租户/用户/角色数据）：
#   python -m app.core.init_db


# 访问 RabbitMQ 管理界面
# 浏览器打开 http://localhost:15672
# 用户名: his_mq_user
# 密码: his_mq_password
```

## 项目结构

```
his/
├── backend/          # 后端代码
├── frontend/         # 前端代码
├── docs/            # 项目文档
├── tests/           # 测试文件
├── scripts/         # 脚本文件
├── docker/          # Docker相关配置
│   └── postgres/
│       └── init/    # PostgreSQL初始化脚本
├── docker-compose.yml  # Docker Compose配置
├── env.example      # 环境变量示例
└── README.md        # 项目说明
```

## 开发说明

详细开发文档请参考 `docs/` 目录下的文档：
- `ALIGNMENT_门诊诊所管理系统.md` - 需求对齐文档
- `CONSENSUS_门诊诊所管理系统.md` - 共识文档
- `DESIGN_门诊诊所管理系统.md` - 系统设计文档
- `DATABASE_DESIGN.md` - 数据库设计文档

## 许可证

[待定]

