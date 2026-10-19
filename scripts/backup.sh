#!/bin/bash
# 数据备份脚本
# 用于备份PostgreSQL数据库和Redis数据

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
BACKUP_DIR="${BACKUP_DIR:-/opt/his/backups}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo "数据备份脚本"
echo "=========================================="
echo ""

# 检查Docker/Podman
if command -v docker &> /dev/null; then
    DOCKER_CMD="docker"
elif command -v podman &> /dev/null; then
    DOCKER_CMD="podman"
else
    echo "错误: 未找到Docker或Podman"
    exit 1
fi

# 备份PostgreSQL
echo "备份PostgreSQL数据库..."
if $DOCKER_CMD ps --filter "name=his_postgres" --format "{{.Names}}" | grep -q his_postgres; then
    $DOCKER_CMD exec his_postgres pg_dump -U his_user his_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
    echo -e "${GREEN}✓${NC} 数据库备份完成: db_$DATE.sql.gz"
    
    # 获取备份文件大小
    SIZE=$(du -h "$BACKUP_DIR/db_$DATE.sql.gz" | cut -f1)
    echo "  大小: $SIZE"
else
    echo -e "${YELLOW}⚠${NC} PostgreSQL容器未运行，跳过数据库备份"
fi

# 备份Redis（可选）
echo ""
echo "备份Redis数据..."
if $DOCKER_CMD ps --filter "name=his_redis" --format "{{.Names}}" | grep -q his_redis; then
    $DOCKER_CMD exec his_redis redis-cli --rdb /data/dump.rdb >/dev/null 2>&1 || true
    $DOCKER_CMD cp his_redis:/data/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb" 2>/dev/null || true
    
    if [ -f "$BACKUP_DIR/redis_$DATE.rdb" ]; then
        echo -e "${GREEN}✓${NC} Redis备份完成: redis_$DATE.rdb"
        SIZE=$(du -h "$BACKUP_DIR/redis_$DATE.rdb" | cut -f1)
        echo "  大小: $SIZE"
    else
        echo -e "${YELLOW}⚠${NC} Redis备份失败或数据为空"
    fi
else
    echo -e "${YELLOW}⚠${NC} Redis容器未运行，跳过Redis备份"
fi

# 清理旧备份
echo ""
echo "清理 $RETENTION_DAYS 天前的备份..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +$RETENTION_DAYS -delete
echo -e "${GREEN}✓${NC} 清理完成"

echo ""
echo "=========================================="
echo "备份完成"
echo "=========================================="
echo "备份目录: $BACKUP_DIR"
echo ""

