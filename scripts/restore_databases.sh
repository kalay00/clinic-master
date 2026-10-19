#!/bin/bash
# 数据库恢复脚本
# 功能：从备份文件恢复PostgreSQL和Redis数据库

set -e

# 配置变量
BACKUP_DIR="/数据库备份目录"
PG_CONTAINER="his_postgres"
REDIS_CONTAINER="his_redis"
PG_USER="his_user"
PG_DB="his_db"
REDIS_PASSWORD="redis_password"

echo "=========================================="
echo "数据库恢复工具"
echo "=========================================="
echo ""

# 检查备份目录是否存在
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ 备份目录不存在: $BACKUP_DIR"
    exit 1
fi

# 列出可用的备份文件
echo "可用的PostgreSQL备份文件:"
echo "----------------------------------------"
ls -lh "$BACKUP_DIR" | grep "his_postgres_" | awk '{print NR". "$9" ("$5")"}'
echo ""

echo "可用的Redis备份文件:"
echo "----------------------------------------"
ls -lh "$BACKUP_DIR" | grep "his_redis_" | awk '{print NR". "$9" ("$5")"}'
echo ""

# 提示用户选择
read -p "请输入PostgreSQL备份文件名（或按Enter跳过）: " PG_BACKUP_FILE
read -p "请输入Redis备份文件名（或按Enter跳过）: " REDIS_BACKUP_FILE

# 恢复PostgreSQL
if [ -n "$PG_BACKUP_FILE" ]; then
    PG_BACKUP_PATH="${BACKUP_DIR}/${PG_BACKUP_FILE}"
    
    if [ ! -f "$PG_BACKUP_PATH" ]; then
        echo "❌ PostgreSQL备份文件不存在: $PG_BACKUP_PATH"
        exit 1
    fi
    
    echo ""
    echo "=========================================="
    echo "恢复PostgreSQL数据库..."
    echo "备份文件: $PG_BACKUP_FILE"
    echo "=========================================="
    
    read -p "⚠️  警告：这将覆盖现有数据库！确认继续？(yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo "已取消恢复操作"
        exit 0
    fi
    
    # 复制备份文件到容器
    echo "复制备份文件到容器..."
    podman cp "$PG_BACKUP_PATH" ${PG_CONTAINER}:/tmp/restore.dump
    
    # 执行恢复（先删除现有数据，再恢复）
    echo "执行数据库恢复..."
    podman exec ${PG_CONTAINER} pg_restore -U ${PG_USER} -d ${PG_DB} -c --if-exists -F c /tmp/restore.dump
    
    # 删除容器内的临时文件
    podman exec ${PG_CONTAINER} rm /tmp/restore.dump
    
    echo "✅ PostgreSQL数据库恢复完成"
fi

# 恢复Redis
if [ -n "$REDIS_BACKUP_FILE" ]; then
    REDIS_BACKUP_PATH="${BACKUP_DIR}/${REDIS_BACKUP_FILE}"
    
    if [ ! -f "$REDIS_BACKUP_PATH" ]; then
        echo "❌ Redis备份文件不存在: $REDIS_BACKUP_PATH"
        exit 1
    fi
    
    echo ""
    echo "=========================================="
    echo "恢复Redis数据库..."
    echo "备份文件: $REDIS_BACKUP_FILE"
    echo "=========================================="
    
    read -p "⚠️  警告：这将覆盖现有Redis数据！确认继续？(yes/no): " CONFIRM
    
    if [ "$CONFIRM" != "yes" ]; then
        echo "已取消恢复操作"
        exit 0
    fi
    
    # 停止Redis容器
    echo "停止Redis容器..."
    podman stop ${REDIS_CONTAINER}
    
    # 复制备份文件到容器
    echo "复制备份文件到容器..."
    podman cp "$REDIS_BACKUP_PATH" ${REDIS_CONTAINER}:/data/dump.rdb
    
    # 启动Redis容器
    echo "启动Redis容器..."
    podman start ${REDIS_CONTAINER}
    
    # 等待Redis启动
    sleep 3
    
    # 验证Redis是否正常
    if podman exec ${REDIS_CONTAINER} redis-cli -a ${REDIS_PASSWORD} ping > /dev/null 2>&1; then
        echo "✅ Redis数据库恢复完成"
    else
        echo "❌ Redis恢复后验证失败"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "恢复操作完成！"
echo "=========================================="

