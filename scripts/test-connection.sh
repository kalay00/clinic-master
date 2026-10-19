#!/bin/bash
# 测试数据库和Redis连接脚本

set -e

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "=========================================="
echo "测试数据库连接"
echo "=========================================="

# 测试 PostgreSQL
echo "测试 PostgreSQL 连接..."
if podman exec his_postgres psql -U ${POSTGRES_USER:-his_user} -d ${POSTGRES_DB:-his_db} -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ PostgreSQL 连接成功"
    podman exec his_postgres psql -U ${POSTGRES_USER:-his_user} -d ${POSTGRES_DB:-his_db} -c "SELECT version();"
else
    echo "❌ PostgreSQL 连接失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "测试 Redis 连接"
echo "=========================================="

# 测试 Redis
echo "测试 Redis 连接..."
if podman exec his_redis redis-cli -a ${REDIS_PASSWORD:-redis_password} ping > /dev/null 2>&1; then
    echo "✅ Redis 连接成功"
    podman exec his_redis redis-cli -a ${REDIS_PASSWORD:-redis_password} ping
else
    echo "❌ Redis 连接失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "测试 RabbitMQ 连接"
echo "=========================================="

# 测试 RabbitMQ
echo "测试 RabbitMQ 连接..."
if podman exec his_rabbitmq rabbitmq-diagnostics ping > /dev/null 2>&1; then
    echo "✅ RabbitMQ 连接成功"
    podman exec his_rabbitmq rabbitmq-diagnostics ping
else
    echo "❌ RabbitMQ 连接失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "所有服务连接正常！"
echo "=========================================="

