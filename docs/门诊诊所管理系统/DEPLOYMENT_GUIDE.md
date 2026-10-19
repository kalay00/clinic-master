# 门诊诊所管理系统 - 部署指南

**版本**: v1.0  
**最后更新**: 2024-12-19  
**适用版本**: HIS 0.1.0+

---

## 目录

- [一、部署概述](#一部署概述)
- [二、环境要求](#二环境要求)
- [三、快速部署（一键部署）](#三快速部署一键部署)
- [四、手动部署](#四手动部署)
- [五、生产环境部署](#五生产环境部署)
- [六、配置说明](#六配置说明)
- [七、验证和测试](#七验证和测试)
- [八、常见问题](#八常见问题)
- [九、维护和升级](#九维护和升级)

---

## 一、部署概述

### 1.1 系统架构

门诊诊所管理系统采用微服务架构，包含以下组件：

- **后端服务**: FastAPI (Python 3.9+)
- **前端**: 原生 HTML/CSS/JavaScript
- **数据库**: PostgreSQL 15+
- **缓存**: Redis 7+
- **消息队列**: RabbitMQ 3.8+
- **Web服务器**: Nginx (可选，用于反向代理和静态文件服务)

### 1.2 部署方式

系统支持两种部署方式：

1. **Docker Compose部署**（推荐）
   - 适用于开发、测试和生产环境
   - 自动管理所有服务依赖
   - 一键启动和停止

2. **手动部署**
   - 适用于特殊需求或定制化部署
   - 需要手动安装和配置各组件

---

## 二、环境要求

### 2.1 系统要求

#### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB 可用空间
- **操作系统**: Linux (Ubuntu 20.04+ / CentOS 7+ / RHEL 8+)

#### 推荐配置
- **CPU**: 4核心+
- **内存**: 8GB RAM+
- **磁盘**: 50GB+ SSD
- **操作系统**: Ubuntu 22.04 LTS / CentOS 8+

### 2.2 软件依赖

#### Docker Compose部署方式
- **Docker**: 20.10+ 或 **Podman**: 4.0+
- **Docker Compose**: 2.0+ 或 **podman-compose**: 1.0+

#### 手动部署方式
- **Python**: 3.9+
- **PostgreSQL**: 15+
- **Redis**: 7+
- **RabbitMQ**: 3.8+
- **Nginx**: 1.18+ (可选)

### 2.3 网络要求

- **端口要求**:
  - 8000: 后端API服务
  - 5432: PostgreSQL数据库
  - 6379: Redis缓存
  - 5672: RabbitMQ AMQP
  - 15672: RabbitMQ管理界面
  - 80/443: Nginx Web服务器（可选）

---

## 三、快速部署（一键部署）

### 3.1 使用一键部署脚本

```bash
# 1. 克隆项目
git clone <repository_url>
cd his

# 2. 运行一键部署脚本
bash scripts/deploy.sh

# 3. 按照提示完成配置
```

一键部署脚本会自动：
- 检查环境依赖
- 创建配置文件
- 启动Docker服务
- 初始化数据库
- 启动后端服务
- 验证部署状态

### 3.2 部署后访问

部署成功后，可以通过以下地址访问：

- **API文档**: http://localhost:8000/api/docs
- **前端页面**: http://localhost:8000
- **RabbitMQ管理**: http://localhost:15672
  - 用户名: `his_mq_user`
  - 密码: `his_mq_password` (默认)

---

## 四、手动部署

### 4.1 准备环境

#### 4.1.1 安装Docker/Podman

**Ubuntu/Debian:**
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

**CentOS/RHEL:**
```bash
# 安装Podman
sudo yum install -y podman podman-compose

# 或安装Docker
sudo yum install -y docker docker-compose
sudo systemctl enable --now docker
```

#### 4.1.2 克隆项目

```bash
git clone <repository_url>
cd his
```

### 4.2 配置环境变量

#### 4.2.1 创建.env文件

```bash
cp env.example .env
```

#### 4.2.2 编辑.env文件

必须修改以下配置（生产环境）：

```bash
# 数据库配置
POSTGRES_PASSWORD=your_strong_password_here
DATABASE_URL=postgresql://his_user:your_strong_password_here@postgres:5432/his_db

# Redis配置
REDIS_PASSWORD=your_redis_password_here

# RabbitMQ配置
RABBITMQ_PASSWORD=your_rabbitmq_password_here

# JWT密钥（必须修改）
SECRET_KEY=your_very_long_random_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# 生产环境配置
APP_ENV=production
DEBUG=false
```

#### 4.2.3 生成密钥

```bash
# 生成JWT密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成加密密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4.3 启动基础服务

#### 4.3.1 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 或使用podman-compose
podman-compose up -d
```

#### 4.3.2 验证服务状态

```bash
# 检查容器状态
docker ps
# 或
podman ps

# 检查服务健康状态
docker-compose ps
```

### 4.4 初始化数据库

#### 4.4.1 等待数据库就绪

```bash
# 等待PostgreSQL启动完成（约30秒）
sleep 30

# 验证数据库连接
docker exec -it his_postgres psql -U his_user -d his_db -c "SELECT version();"
```

#### 4.4.2 运行数据库迁移

```bash
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head
```

#### 4.4.3 初始化基础数据

```bash
# 初始化数据库表和基础数据
python3 -m app.core.init_db

# 初始化测试数据（可选，仅用于开发/测试）
python3 -m app.core.init_test_data
```

### 4.5 启动后端服务

#### 4.5.1 开发环境

```bash
cd backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4.5.2 生产环境

使用systemd管理服务（见5.1节）或使用Gunicorn：

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 五、生产环境部署

### 5.1 使用systemd管理服务

#### 5.1.1 创建服务文件

创建 `/etc/systemd/system/his-backend.service`:

```ini
[Unit]
Description=HIS Backend Service
After=network.target postgres.service redis.service

[Service]
Type=simple
User=his
Group=his
WorkingDirectory=/opt/his/backend
Environment="PATH=/opt/his/backend/venv/bin"
EnvironmentFile=/opt/his/.env
ExecStart=/opt/his/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 5.1.2 创建系统用户

```bash
sudo useradd -r -s /bin/false his
sudo mkdir -p /opt/his
sudo chown -R his:his /opt/his
```

#### 5.1.3 启用和启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable his-backend
sudo systemctl start his-backend
sudo systemctl status his-backend
```

### 5.2 Nginx配置

#### 5.2.1 创建Nginx配置

创建 `/etc/nginx/sites-available/his`:

```nginx
# 上游后端服务
upstream his_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# HTTP服务器（重定向到HTTPS）
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS服务器
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 客户端最大上传大小
    client_max_body_size 100M;
    
    # 日志配置
    access_log /var/log/nginx/his_access.log;
    error_log /var/log/nginx/his_error.log;
    
    # 前端静态文件
    location / {
        root /opt/his/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api {
        proxy_pass http://his_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket支持（如果需要）
    location /ws {
        proxy_pass http://his_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5.2.2 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/his /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5.2.3 配置SSL证书（Let's Encrypt）

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 5.3 防火墙配置

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 5.4 数据备份

#### 5.4.1 数据库备份脚本

创建 `scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/his/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份PostgreSQL
docker exec his_postgres pg_dump -U his_user his_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 备份Redis（可选）
docker exec his_redis redis-cli --rdb /data/dump.rdb
docker cp his_redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# 删除30天前的备份
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
```

#### 5.4.2 配置定时备份

```bash
# 编辑crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /opt/his/scripts/backup.sh
```

---

## 六、配置说明

### 6.1 环境变量说明

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `DATABASE_URL` | PostgreSQL连接URL | 自动构建 | 是 |
| `POSTGRES_USER` | 数据库用户名 | `his_user` | 否 |
| `POSTGRES_PASSWORD` | 数据库密码 | `his_password` | 是 |
| `POSTGRES_DB` | 数据库名称 | `his_db` | 否 |
| `REDIS_URL` | Redis连接URL | 自动构建 | 是 |
| `REDIS_PASSWORD` | Redis密码 | `redis_password` | 是 |
| `RABBITMQ_USER` | RabbitMQ用户名 | `his_mq_user` | 否 |
| `RABBITMQ_PASSWORD` | RabbitMQ密码 | `his_mq_password` | 是 |
| `SECRET_KEY` | JWT密钥 | 无 | 是 |
| `ENCRYPTION_KEY` | 加密密钥 | 无 | 是 |
| `APP_ENV` | 环境类型 | `development` | 否 |
| `DEBUG` | 调试模式 | `true` | 否 |

### 6.2 多租户配置

系统支持多租户，每个租户可以配置独立的域名和设置：

- 租户通过域名识别（`domain`字段）
- 支持租户代码登录
- 支持HTTP Header指定租户（`X-Tenant-Id`或`X-Tenant-Code`）

### 6.3 平台管理员

系统包含平台管理员功能，用于管理所有租户：

- 平台管理员登录: `/platform-login.html`
- 默认账号: `platform_admin` / `111111` (首次部署后需修改)

---

## 七、验证和测试

### 7.1 健康检查

```bash
# 检查后端服务
curl http://localhost:8000/health

# 检查数据库连接
docker exec his_postgres pg_isready -U his_user

# 检查Redis连接
docker exec his_redis redis-cli -a redis_password ping
```

### 7.2 API测试

```bash
# 访问API文档
curl http://localhost:8000/api/docs

# 测试登录接口
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"111111","tenant_code":"TEST001"}'
```

### 7.3 运行测试套件

```bash
cd /opt/his
bash tests/quick_test.sh
```

---

## 八、常见问题

### 8.1 数据库连接失败

**问题**: 后端无法连接到PostgreSQL

**解决方案**:
1. 检查PostgreSQL容器是否运行: `docker ps | grep postgres`
2. 检查环境变量: `docker exec his_postgres env | grep POSTGRES`
3. 检查网络连接: `docker network ls`
4. 查看日志: `docker logs his_postgres`

### 8.2 Redis连接失败

**问题**: Redis连接超时

**解决方案**:
1. 检查Redis密码配置是否一致
2. 检查Redis容器状态: `docker ps | grep redis`
3. 测试连接: `docker exec his_redis redis-cli -a redis_password ping`

### 8.3 端口冲突

**问题**: 端口已被占用

**解决方案**:
1. 检查端口占用: `netstat -tulpn | grep :8000`
2. 修改`.env`文件中的端口配置
3. 修改`docker-compose.yml`中的端口映射

### 8.4 数据库迁移失败

**问题**: Alembic迁移失败

**解决方案**:
1. 检查数据库连接配置
2. 查看迁移脚本: `alembic history`
3. 手动执行迁移: `alembic upgrade head --sql`
4. 回滚迁移: `alembic downgrade -1`

### 8.5 前端页面无法访问

**问题**: 前端页面404或空白

**解决方案**:
1. 检查Nginx配置是否正确
2. 检查静态文件路径
3. 检查文件权限: `ls -la /opt/his/frontend`
4. 查看Nginx错误日志: `tail -f /var/log/nginx/error.log`

---

## 九、维护和升级

### 9.1 日常维护

#### 查看服务状态

```bash
# Docker服务
docker-compose ps

# Systemd服务
sudo systemctl status his-backend

# 查看日志
docker-compose logs -f
sudo journalctl -u his-backend -f
```

#### 清理日志

```bash
# Docker日志清理
docker system prune -f

# 应用日志清理（如果配置了日志轮转）
logrotate -f /etc/logrotate.d/his
```

### 9.2 升级流程

#### 9.2.1 备份数据

```bash
bash scripts/backup.sh
```

#### 9.2.2 停止服务

```bash
# 停止后端服务
sudo systemctl stop his-backend
# 或
docker-compose stop backend
```

#### 9.2.3 更新代码

```bash
cd /opt/his
git pull origin main
```

#### 9.2.4 更新依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 9.2.5 运行数据库迁移

```bash
alembic upgrade head
```

#### 9.2.6 重启服务

```bash
sudo systemctl restart his-backend
# 或
docker-compose restart backend
```

### 9.3 性能优化

#### 9.3.1 数据库优化

- 定期执行`VACUUM ANALYZE`
- 配置连接池大小
- 创建必要的索引

#### 9.3.2 Redis优化

- 配置内存限制
- 启用持久化
- 使用Redis集群（大规模部署）

#### 9.3.3 应用优化

- 调整Gunicorn worker数量
- 启用响应压缩
- 配置CDN（前端静态资源）

---

## 十、附录

### 10.1 相关文档

- [项目说明文档](../说明文档.md)
- [数据库设计文档](DATABASE_DESIGN.md)
- [API接口文档](API_DOCUMENTATION.md)
- [测试指南](TEST_EXECUTION_GUIDE.md)

### 10.2 技术支持

- 问题反馈: 提交Issue到项目仓库
- 文档更新: 参考本文档进行更新

---

**文档版本**: v1.0  
**最后更新**: 2024-12-19  
**维护者**: 开发团队
