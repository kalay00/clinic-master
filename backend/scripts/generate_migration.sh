#!/bin/bash
# 生成数据库迁移脚本

cd "$(dirname "$0")/.."

# 检查是否安装了alembic
if ! python -c "import alembic" 2>/dev/null; then
    echo "请先安装alembic: pip install alembic"
    exit 1
fi

# 生成迁移脚本
echo "正在生成数据库迁移脚本..."
alembic revision --autogenerate -m "initial_migration_all_models"

echo "迁移脚本生成完成！"
echo "请检查 alembic/versions/ 目录下的最新迁移文件"
echo "然后执行: alembic upgrade head"

