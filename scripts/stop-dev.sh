#!/bin/bash
# 停止开发环境脚本

set -e

echo "=========================================="
echo "停止门诊诊所管理系统开发环境"
echo "=========================================="

# 检查是否有 podman-compose
if command -v podman-compose &> /dev/null; then
    echo "使用 podman-compose 停止服务..."
    podman-compose down
elif command -v docker-compose &> /dev/null; then
    echo "使用 docker-compose 停止服务..."
    docker-compose down
else
    echo "使用 Podman 直接停止服务..."
    
    # 停止并删除容器
    podman stop his_postgres his_redis his_rabbitmq 2>/dev/null || true
    podman rm his_postgres his_redis his_rabbitmq 2>/dev/null || true
    
    echo "服务已停止"
fi

echo "=========================================="

