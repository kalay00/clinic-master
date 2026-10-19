#!/bin/bash
# 门诊诊所管理系统 - 一键部署脚本
# 版本: v1.0
# 日期: 2024-12-19

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        return 1
    fi
    return 0
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        log_warning "端口 $port 已被占用"
        return 1
    fi
    return 0
}

# 主函数
main() {
    echo "=========================================="
    echo "门诊诊所管理系统 - 一键部署脚本"
    echo "=========================================="
    echo ""
    
    # 步骤1: 检查环境
    log_info "步骤 1/8: 检查环境依赖..."
    
    # 检查Docker或Podman
    if check_command docker; then
        DOCKER_CMD="docker"
        COMPOSE_CMD="docker-compose"
        log_success "检测到 Docker"
    elif check_command podman; then
        DOCKER_CMD="podman"
        if check_command podman-compose; then
            COMPOSE_CMD="podman-compose"
        else
            COMPOSE_CMD="podman compose"
        fi
        log_success "检测到 Podman"
    else
        log_error "未检测到 Docker 或 Podman，请先安装"
        exit 1
    fi
    
    # 检查Python
    if ! check_command python3; then
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    log_success "Python: $PYTHON_VERSION"
    
    # 步骤2: 检查配置文件
    log_info "步骤 2/8: 检查配置文件..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，从 env.example 创建..."
        cp env.example .env
        log_warning "请编辑 .env 文件，修改以下关键配置:"
        echo "  - POSTGRES_PASSWORD"
        echo "  - REDIS_PASSWORD"
        echo "  - RABBITMQ_PASSWORD"
        echo "  - SECRET_KEY (运行: python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
        echo "  - ENCRYPTION_KEY (运行: python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
        echo ""
        read -p "按 Enter 继续（或按 Ctrl+C 退出以编辑配置）..."
    else
        log_success ".env 文件已存在"
    fi
    
    # 加载环境变量
    set -a
    source .env
    set +a
    
    # 步骤3: 检查端口
    log_info "步骤 3/8: 检查端口占用..."
    
    PORTS_TO_CHECK=(8000 5432 6379 5672 15672)
    PORT_CONFLICT=false
    
    for port in "${PORTS_TO_CHECK[@]}"; do
        if check_port "$port"; then
            log_success "端口 $port 可用"
        else
            PORT_CONFLICT=true
        fi
    done
    
    if [ "$PORT_CONFLICT" = true ]; then
        log_warning "检测到端口冲突，部署可能失败"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 步骤4: 启动Docker服务
    log_info "步骤 4/8: 启动Docker服务..."
    
    if [ "$COMPOSE_CMD" = "docker-compose" ] || [ "$COMPOSE_CMD" = "podman-compose" ]; then
        log_info "使用 $COMPOSE_CMD 启动服务..."
        $COMPOSE_CMD up -d
    else
        log_info "使用 $COMPOSE_CMD 启动服务..."
        $COMPOSE_CMD up -d
    fi
    
    log_success "Docker服务已启动"
    
    # 等待服务就绪
    log_info "等待服务启动（30秒）..."
    sleep 30
    
    # 步骤5: 验证服务状态
    log_info "步骤 5/8: 验证服务状态..."
    
    if [ "$DOCKER_CMD" = "docker" ]; then
        SERVICES=$(docker ps --filter "name=his_" --format "{{.Names}}")
    else
        SERVICES=$(podman ps --filter "name=his_" --format "{{.Names}}")
    fi
    
    if [ -z "$SERVICES" ]; then
        log_error "未检测到运行中的服务"
        log_info "查看服务日志:"
        if [ "$COMPOSE_CMD" = "docker-compose" ] || [ "$COMPOSE_CMD" = "podman-compose" ]; then
            $COMPOSE_CMD logs --tail=50
        else
            $COMPOSE_CMD logs --tail=50
        fi
        exit 1
    fi
    
    log_success "运行中的服务:"
    echo "$SERVICES" | while read -r service; do
        echo "  - $service"
    done
    
    # 步骤6: 初始化数据库
    log_info "步骤 6/8: 初始化数据库..."
    
    cd backend
    
    # 检查Python依赖
    if [ ! -d "venv" ]; then
        log_info "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    log_info "激活虚拟环境并安装依赖..."
    source venv/bin/activate || true
    
    log_info "安装Python依赖（可能需要几分钟）..."
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    # 等待PostgreSQL完全就绪
    log_info "等待PostgreSQL就绪..."
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if $DOCKER_CMD exec his_postgres pg_isready -U "${POSTGRES_USER:-his_user}" >/dev/null 2>&1; then
            log_success "PostgreSQL已就绪"
            break
        fi
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep 2
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_error "PostgreSQL启动超时"
        exit 1
    fi
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    if [ -f "alembic.ini" ]; then
        alembic upgrade head || log_warning "数据库迁移失败或已是最新版本"
    else
        log_warning "未找到alembic.ini，跳过迁移"
    fi
    
    # 初始化数据库表
    log_info "初始化数据库表..."
    python3 -m app.core.init_db || log_warning "数据库初始化失败或表已存在"
    
    # 询问是否初始化测试数据
    echo ""
    read -p "是否初始化测试数据？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "初始化测试数据..."
        python3 -m app.core.init_test_data || log_warning "测试数据初始化失败"
        log_success "测试数据已初始化"
        log_info "默认测试账号:"
        log_info "  平台管理员: platform_admin / 111111"
        log_info "  租户管理员: admin / 111111 (租户: TEST001)"
    fi
    
    cd ..
    
    # 步骤7: 启动后端服务（可选）
    log_info "步骤 7/8: 后端服务配置..."
    
    echo ""
    read -p "是否现在启动后端服务？(Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        log_info "启动后端服务..."
        cd backend
        
        # 检查uvicorn是否安装
        if ! python3 -c "import uvicorn" 2>/dev/null; then
            log_warning "uvicorn未安装，正在安装..."
            pip install uvicorn[standard]
        fi
        
        log_success "后端服务启动命令:"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
        echo ""
        log_info "提示: 使用 systemd 管理生产环境服务（参考部署文档）"
        
        # 询问是否现在启动
        read -p "是否现在启动后端服务？(Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            log_info "正在启动后端服务（按 Ctrl+C 停止）..."
            python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
            BACKEND_PID=$!
            sleep 5
            
            if ps -p $BACKEND_PID > /dev/null; then
                log_success "后端服务已启动 (PID: $BACKEND_PID)"
            fi
        fi
        
        cd ..
    fi
    
    # 步骤8: 部署验证
    log_info "步骤 8/8: 部署验证..."
    
    echo ""
    log_success "部署完成！"
    echo ""
    echo "=========================================="
    echo "服务访问信息"
    echo "=========================================="
    echo "后端API:     http://localhost:8000"
    echo "API文档:     http://localhost:8000/api/docs"
    echo "前端页面:    http://localhost:8000"
    echo "RabbitMQ:    http://localhost:15672"
    echo "             用户名: ${RABBITMQ_USER:-his_mq_user}"
    echo "             密码: ${RABBITMQ_PASSWORD:-his_mq_password}"
    echo ""
    echo "PostgreSQL:  localhost:${POSTGRES_PORT:-5432}"
    echo "             数据库: ${POSTGRES_DB:-his_db}"
    echo "             用户: ${POSTGRES_USER:-his_user}"
    echo ""
    echo "Redis:       localhost:${REDIS_PORT:-6379}"
    echo "=========================================="
    echo ""
    log_info "常用命令:"
    echo "  查看服务状态: $COMPOSE_CMD ps"
    echo "  查看服务日志: $COMPOSE_CMD logs -f"
    echo "  停止服务:     $COMPOSE_CMD down"
    echo "  重启服务:     $COMPOSE_CMD restart"
    echo ""
    log_info "下一步:"
    echo "  1. 编辑 .env 文件，修改生产环境配置"
    echo "  2. 配置 Nginx 反向代理（参考部署文档）"
    echo "  3. 配置 systemd 服务（参考部署文档）"
    echo "  4. 配置 SSL 证书"
    echo "  5. 设置数据备份计划"
    echo ""
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查上述输出"; exit 1' ERR

# 执行主函数
main "$@"

