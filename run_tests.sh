#!/bin/bash
# 测试运行脚本

set -e

echo "=========================================="
echo "门诊诊所管理系统 - 测试运行脚本"
echo "=========================================="

# 检查Python版本
echo "检查Python版本..."
python3 --version

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "警告: 未检测到虚拟环境，建议使用虚拟环境运行测试"
fi

# 安装依赖
echo ""
echo "安装测试依赖..."
cd "$(dirname "$0")/backend"
pip install -r requirements.txt

# 返回项目根目录
cd ..

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
export DATABASE_URL="sqlite:///:memory:"
export SECRET_KEY="test-secret-key-for-testing-only"

# 运行测试
echo ""
echo "运行单元测试..."
pytest tests/unit/ -v --tb=short

echo ""
echo "运行集成测试..."
pytest tests/integration/ -v --tb=short

echo ""
echo "生成测试覆盖率报告..."
pytest tests/ --cov=backend/app --cov-report=term-missing --cov-report=html

echo ""
echo "=========================================="
echo "测试完成！"
echo "覆盖率报告: htmlcov/index.html"
echo "=========================================="

