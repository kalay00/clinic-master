#!/bin/bash
# 启动开发环境脚本

set -e

echo "=========================================="
echo "启动门诊诊所管理系统开发环境"
echo "=========================================="

# 检查 Podman 是否安装
if ! command -v podman &> /dev/null; then
    echo "错误: Podman 未安装，请先安装 Podman"
    exit 1
fi

# 检查是否存在 .env 文件
if [ ! -f .env ]; then
    echo "警告: .env 文件不存在，从 env.example 创建..."
    cp env.example .env
    echo "请编辑 .env 文件配置数据库密码等敏感信息"
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 检查是否有 podman-compose
if command -v podman-compose &> /dev/null; then
    echo "使用 podman-compose 启动服务..."
    podman-compose up -d
elif command -v docker-compose &> /dev/null; then
    echo "使用 docker-compose 启动服务..."
    docker-compose up -d
else
    echo "使用 Podman 直接启动服务..."
    
    # 创建网络
    podman network create his_network 2>/dev/null || true
    
    # 启动 PostgreSQL
    echo "启动 PostgreSQL..."
    podman run -d \
        --name his_postgres \
        --network his_network \
        -e POSTGRES_USER=${POSTGRES_USER:-his_user} \
        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-his_password} \
        -e POSTGRES_DB=${POSTGRES_DB:-his_db} \
        -e PGDATA=/var/lib/postgresql/data/pgdata \
        -p ${POSTGRES_PORT:-5432}:5432 \
        -v his_postgres_data:/var/lib/postgresql/data \
        -v $(pwd)/docker/postgres/init:/docker-entrypoint-initdb.d:Z \
        --restart unless-stopped \
        docker.io/postgres:15-alpine
    
    # 启动 Redis
    echo "启动 Redis..."
    podman run -d \
        --name his_redis \
        --network his_network \
        -p ${REDIS_PORT:-6379}:6379 \
        -v his_redis_data:/data \
        --restart unless-stopped \
        docker.io/redis:7-alpine redis-server --requirepass ${REDIS_PASSWORD:-redis_password} --appendonly yes
    
    # 启动 RabbitMQ
    echo "启动 RabbitMQ..."
    podman run -d \
        --name his_rabbitmq \
        --network his_network \
        -e RABBITMQ_DEFAULT_USER=${RABBITMQ_USER:-his_mq_user} \
        -e RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD:-his_mq_password} \
        -e RABBITMQ_DEFAULT_VHOST=${RABBITMQ_VHOST:-/} \
        -p ${RABBITMQ_PORT:-5672}:5672 \
        -p ${RABBITMQ_MANAGEMENT_PORT:-15672}:15672 \
        -v his_rabbitmq_data:/var/lib/rabbitmq \
        --restart unless-stopped \
        docker.io/rabbitmq:3-management-alpine
    
    echo "服务启动完成！"
fi

echo ""
echo "等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "=========================================="
echo "服务状态检查"
echo "=========================================="
podman ps --filter "name=his_"

echo ""
echo "=========================================="
echo "服务连接信息"
echo "=========================================="
echo "PostgreSQL:"
echo "  主机: localhost"
echo "  端口: ${POSTGRES_PORT:-5432}"
echo "  数据库: ${POSTGRES_DB:-his_db}"
echo "  用户: ${POSTGRES_USER:-his_user}"
echo ""
echo "Redis:"
echo "  主机: localhost"
echo "  端口: ${REDIS_PORT:-6379}"
echo "  密码: ${REDIS_PASSWORD:-redis_password}"
echo ""
echo "RabbitMQ:"
echo "  AMQP端口: ${RABBITMQ_PORT:-5672}"
echo "  管理界面: http://localhost:${RABBITMQ_MANAGEMENT_PORT:-15672}"
echo "  用户名: ${RABBITMQ_USER:-his_mq_user}"
echo "  密码: ${RABBITMQ_PASSWORD:-his_mq_password}"
echo ""
echo "使用以下命令查看日志:"
echo "  podman logs -f his_postgres"
echo "  podman logs -f his_redis"
echo "  podman logs -f his_rabbitmq"
echo "=========================================="

