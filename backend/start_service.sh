#!/bin/bash
# 后端服务启动脚本

set -e

echo "=========================================="
echo "启动门诊诊所管理系统后端服务"
echo "=========================================="

# 切换到后端目录
cd "$(dirname "$0")"
BACKEND_DIR=$(pwd)

echo ""
echo "1. 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 未安装"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION"

# 检查虚拟环境
if [ -d "venv" ]; then
    echo ""
    echo "2. 激活虚拟环境..."
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
else
    echo ""
    echo "2. 未找到虚拟环境，使用系统Python..."
fi

# 检查依赖
echo ""
echo "3. 检查依赖..."
if python3 -c "import fastapi" 2>/dev/null; then
    echo "✓ FastAPI 已安装"
else
    echo "✗ FastAPI 未安装"
    echo "  请运行: pip3 install --user fastapi uvicorn[standard]"
    exit 1
fi

if python3 -c "import uvicorn" 2>/dev/null; then
    echo "✓ Uvicorn 已安装"
else
    echo "✗ Uvicorn 未安装"
    echo "  请运行: pip3 install --user uvicorn[standard]"
    exit 1
fi

# 检查数据库连接
echo ""
echo "4. 检查数据库配置..."
if [ -f ".env" ]; then
    echo "✓ 找到.env配置文件"
else
    echo "⚠ 未找到.env文件，使用默认配置"
fi

# 启动服务
echo ""
echo "5. 启动服务..."
echo "   服务地址: http://localhost:8000"
echo "   API文档: http://localhost:8000/api/docs"
echo "   按 Ctrl+C 停止服务"
echo ""

# 尝试启动服务
if command -v uvicorn &> /dev/null; then
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    # 如果uvicorn不在PATH中，尝试使用python -m
    python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi

