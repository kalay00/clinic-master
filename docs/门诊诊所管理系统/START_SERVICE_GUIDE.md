# 后端服务启动指南

## 一、环境要求

### 1.1 Python版本
- Python 3.8+

### 1.2 必需依赖
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL数据库
- Redis（可选）

## 二、安装依赖

### 方法1：使用pip安装（推荐）

```bash
cd /home/laknl/his/backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 方法2：使用系统包管理器

如果pip不可用，可以使用系统包管理器：

```bash
# CentOS/RHEL
sudo yum install python3-pip python3-devel postgresql-devel

# 或使用dnf
sudo dnf install python3-pip python3-devel postgresql-devel

# 然后安装Python包
pip3 install --user fastapi uvicorn[standard] sqlalchemy psycopg2-binary
```

### 方法3：手动安装

```bash
cd /home/laknl/his/backend

# 安装核心依赖
python3 -m pip install --user fastapi
python3 -m pip install --user "uvicorn[standard]"
python3 -m pip install --user sqlalchemy
python3 -m pip install --user psycopg2-binary
python3 -m pip install --user pydantic pydantic-settings
python3 -m pip install --user "python-jose[cryptography]"
python3 -m pip install --user "passlib[bcrypt]"
python3 -m pip install --user python-multipart
python3 -m pip install --user redis
```

## 三、配置数据库

### 3.1 确保PostgreSQL运行

```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 如果未运行，启动PostgreSQL
sudo systemctl start postgresql
```

### 3.2 创建数据库（如果未创建）

```bash
# 连接到PostgreSQL
sudo -u postgres psql

# 创建数据库
CREATE DATABASE his_db;
CREATE USER his_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE his_db TO his_user;
\q
```

### 3.3 初始化数据库

```bash
cd /home/laknl/his/backend

# 运行数据库迁移（如果有）
# alembic upgrade head

# 初始化测试数据
python3 -m app.core.init_test_data
```

## 四、启动服务

### 4.1 开发模式启动

```bash
cd /home/laknl/his/backend

# 激活虚拟环境（如果使用）
source venv/bin/activate

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4.2 生产模式启动

```bash
cd /home/laknl/his/backend

# 使用gunicorn（需要先安装）
pip install gunicorn

# 启动服务
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4.3 后台运行

```bash
cd /home/laknl/his/backend

# 使用nohup后台运行
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/his_backend.log 2>&1 &

# 查看日志
tail -f /tmp/his_backend.log
```

## 五、验证服务

### 5.1 检查服务状态

```bash
# 检查健康接口
curl http://localhost:8000/health

# 检查API文档
curl http://localhost:8000/api/docs

# 浏览器访问
# http://localhost:8000/api/docs
```

### 5.2 测试平台管理员登录

```bash
curl -X POST http://localhost:8000/api/v1/platform/login \
  -H "Content-Type: application/json" \
  -d '{"username":"platform_admin","password":"111111"}'
```

## 六、常见问题

### 6.1 ModuleNotFoundError

**问题**: `ModuleNotFoundError: No module named 'uvicorn'`

**解决**:
```bash
# 安装uvicorn
pip3 install --user uvicorn[standard]

# 或使用系统路径
export PATH=$PATH:~/.local/bin
```

### 6.2 端口被占用

**问题**: `Address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
uvicorn app.main:app --port 8001
```

### 6.3 数据库连接失败

**问题**: `could not connect to server`

**解决**:
1. 检查PostgreSQL是否运行
2. 检查数据库配置（.env文件）
3. 检查防火墙设置
4. 验证数据库用户权限

### 6.4 缺少依赖

**问题**: `ImportError: cannot import name 'xxx'`

**解决**:
```bash
# 安装缺失的依赖
pip3 install --user <package_name>

# 或重新安装所有依赖
pip3 install --user -r requirements.txt
```

## 七、Docker方式启动（可选）

如果系统环境复杂，可以使用Docker：

```bash
cd /home/laknl/his

# 使用docker-compose启动
docker-compose up -d

# 或使用podman-compose
podman-compose up -d
```

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  

