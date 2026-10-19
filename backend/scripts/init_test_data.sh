#!/bin/bash
# 初始化测试数据脚本

set -e

echo "=========================================="
echo "初始化测试数据"
echo "=========================================="

cd "$(dirname "$0")/.."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装"
    exit 1
fi

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "警告: 未检测到虚拟环境，建议在虚拟环境中运行"
fi

# 安装依赖（如果需要）
echo "检查Python依赖..."
python3 -c "import pydantic_settings" 2>/dev/null || {
    echo "安装依赖..."
    pip install -q pydantic-settings sqlalchemy psycopg2-binary passlib[bcrypt] python-jose[cryptography] cryptography
}

# 执行初始化脚本
echo ""
echo "开始初始化测试数据..."
echo ""

python3 scripts/init_test_data.py

echo ""
echo "=========================================="
echo "测试数据初始化完成！"
echo "=========================================="
echo ""
echo "所有用户密码已设置为: 111111"
echo ""
echo "测试用户列表（租户1和租户2各有一份）:"
echo "  - admin1 / admin2 (系统管理员)"
echo "  - doctor11 / doctor12 (医生)"
echo "  - doctor21 / doctor22 (医生)"
echo "  - nurse1 / nurse2 (护士)"
echo "  - pharmacist1 / pharmacist2 (药师)"
echo "  - cashier1 / cashier2 (收费员)"
echo ""

