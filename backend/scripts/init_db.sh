#!/bin/bash
# 数据库初始化脚本

set -e

echo "开始初始化数据库..."

# 检查数据库连接
echo "检查数据库连接..."
python -c "
from app.core.database import engine
try:
    with engine.connect() as conn:
        print('数据库连接成功！')
except Exception as e:
    print(f'数据库连接失败: {e}')
    exit(1)
"

# 运行Alembic迁移
echo "运行数据库迁移..."
cd "$(dirname "$0")/.."
alembic upgrade head

# 初始化基础数据
echo "初始化基础数据..."
python -m app.core.init_db

echo "数据库初始化完成！"

