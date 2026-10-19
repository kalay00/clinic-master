#!/bin/bash
# 数据库备份脚本
# 功能：备份PostgreSQL和Redis数据库到指定目录

set -e

# 配置变量
BACKUP_DIR="/数据库备份目录"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PG_CONTAINER="his_postgres"
REDIS_CONTAINER="his_redis"
PG_USER="his_user"
PG_DB="his_db"
REDIS_PASSWORD="redis_password"

# 创建备份目录（如果不存在）
if [ ! -d "$BACKUP_DIR" ]; then
    echo "创建备份目录: $BACKUP_DIR"
    sudo mkdir -p "$BACKUP_DIR"
    sudo chown laknl:laknl "$BACKUP_DIR"
fi

echo "=========================================="
echo "开始备份数据库"
echo "备份时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "备份目录: $BACKUP_DIR"
echo "=========================================="

# 1. 备份PostgreSQL数据库
echo ""
echo "1. 备份PostgreSQL数据库..."
PG_BACKUP_FILE="his_postgres_${TIMESTAMP}.dump"
PG_TMP_FILE="/tmp/${PG_BACKUP_FILE}"

# 在容器内执行备份
podman exec $PG_CONTAINER pg_dump -U $PG_USER -d $PG_DB -F c -f $PG_TMP_FILE

# 从容器复制到宿主机
podman cp ${PG_CONTAINER}:${PG_TMP_FILE} ${BACKUP_DIR}/${PG_BACKUP_FILE}

# 删除容器内的临时文件
podman exec $PG_CONTAINER rm $PG_TMP_FILE

if [ -f "${BACKUP_DIR}/${PG_BACKUP_FILE}" ]; then
    PG_SIZE=$(du -h "${BACKUP_DIR}/${PG_BACKUP_FILE}" | cut -f1)
    echo "✅ PostgreSQL备份完成: ${PG_BACKUP_FILE} (${PG_SIZE})"
else
    echo "❌ PostgreSQL备份失败"
    exit 1
fi

# 2. 备份Redis数据库
echo ""
echo "2. 备份Redis数据库..."
REDIS_BACKUP_FILE="his_redis_${TIMESTAMP}.rdb"

# 执行Redis后台保存
echo "执行Redis BGSAVE..."
podman exec $REDIS_CONTAINER redis-cli -a $REDIS_PASSWORD BGSAVE

# 等待BGSAVE完成
echo "等待Redis保存完成..."
sleep 5

# 检查BGSAVE是否完成
while true; do
    SAVE_STATUS=$(podman exec $REDIS_CONTAINER redis-cli -a $REDIS_PASSWORD LASTSAVE)
    CURRENT_TIME=$(date +%s)
    if [ -n "$SAVE_STATUS" ]; then
        break
    fi
    sleep 1
done

# 从容器复制RDB文件到宿主机
podman cp ${REDIS_CONTAINER}:/data/dump.rdb ${BACKUP_DIR}/${REDIS_BACKUP_FILE}

if [ -f "${BACKUP_DIR}/${REDIS_BACKUP_FILE}" ]; then
    REDIS_SIZE=$(du -h "${BACKUP_DIR}/${REDIS_BACKUP_FILE}" | cut -f1)
    echo "✅ Redis备份完成: ${REDIS_BACKUP_FILE} (${REDIS_SIZE})"
else
    echo "❌ Redis备份失败"
    exit 1
fi

# 3. 创建备份信息文件
echo ""
echo "3. 创建备份信息文件..."
INFO_FILE="${BACKUP_DIR}/backup_info_${TIMESTAMP}.txt"
cat > "$INFO_FILE" << EOF
数据库备份信息
================
备份时间: $(date '+%Y-%m-%d %H:%M:%S')
备份目录: $BACKUP_DIR

PostgreSQL备份:
  文件: ${PG_BACKUP_FILE}
  大小: ${PG_SIZE}
  容器: ${PG_CONTAINER}
  数据库: ${PG_DB}
  用户: ${PG_USER}

Redis备份:
  文件: ${REDIS_BACKUP_FILE}
  大小: ${REDIS_SIZE}
  容器: ${REDIS_CONTAINER}

恢复说明:
  PostgreSQL恢复:
    podman exec -i ${PG_CONTAINER} pg_restore -U ${PG_USER} -d ${PG_DB} -c < ${BACKUP_DIR}/${PG_BACKUP_FILE}

  Redis恢复:
    podman cp ${BACKUP_DIR}/${REDIS_BACKUP_FILE} ${REDIS_CONTAINER}:/data/dump.rdb
    podman restart ${REDIS_CONTAINER}
EOF

echo "✅ 备份信息文件: backup_info_${TIMESTAMP}.txt"

# 4. 显示备份结果
echo ""
echo "=========================================="
echo "备份完成！"
echo "=========================================="
echo "备份文件列表:"
ls -lh "$BACKUP_DIR" | grep -E "his_postgres_|his_redis_|backup_info_" | tail -3
echo ""
echo "备份目录: $BACKUP_DIR"
echo "=========================================="

