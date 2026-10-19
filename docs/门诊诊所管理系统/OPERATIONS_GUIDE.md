# 运维指南

## 一、日常运维

### 1.1 服务监控

#### 健康检查

```bash
# 检查API健康状态
curl http://localhost:8000/health

# 检查数据库连接
curl http://localhost:8000/api/v1/health
```

#### 服务状态

```bash
# 检查所有服务状态
sudo systemctl status his
sudo systemctl status postgresql
sudo systemctl status redis
sudo systemctl status rabbitmq-server
```

### 1.2 日志管理

#### 查看日志

```bash
# 实时查看应用日志
tail -f /opt/his/backend/logs/app.log

# 查看错误日志
tail -f /opt/his/backend/logs/error.log

# 查看系统日志
sudo journalctl -u his -f
```

#### 日志清理

```bash
# 手动清理旧日志
find /opt/his/backend/logs -name "*.log" -mtime +30 -delete
```

### 1.3 性能监控

#### 数据库性能

```sql
-- 查看慢查询
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- 查看连接数
SELECT count(*) FROM pg_stat_activity;

-- 查看表大小
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### 应用性能

```bash
# 查看进程资源使用
top -p $(pgrep -f "uvicorn")

# 查看内存使用
free -h

# 查看磁盘使用
df -h
```

## 二、备份策略

### 2.1 数据库备份

#### 自动备份脚本

创建 `/opt/his/scripts/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/his/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/his_db_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

pg_dump -U his_user -d his_db | gzip > $BACKUP_FILE

# 删除30天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "备份完成: $BACKUP_FILE"
```

配置cron任务:

```bash
# 每天凌晨2点备份
0 2 * * * /opt/his/scripts/backup_db.sh
```

### 2.2 配置文件备份

```bash
# 备份配置文件
tar -czf /opt/his/backups/config_$(date +%Y%m%d).tar.gz \
    /opt/his/backend/.env \
    /opt/his/backend/alembic.ini \
    /etc/nginx/sites-available/his
```

## 三、故障处理

### 3.1 服务异常

#### 应用服务无法启动

1. 检查日志: `journalctl -u his -n 100`
2. 检查端口占用: `lsof -i :8000`
3. 检查数据库连接: `psql -U his_user -d his_db`
4. 检查环境变量: `cat /opt/his/backend/.env`

#### 数据库连接失败

1. 检查PostgreSQL服务: `sudo systemctl status postgresql`
2. 检查用户权限: `psql -U postgres -c "\du"`
3. 检查防火墙: `sudo ufw status`

#### Redis连接失败

1. 检查Redis服务: `sudo systemctl status redis`
2. 测试连接: `redis-cli -h localhost -p 6379 ping`
3. 检查密码配置

### 3.2 性能问题

#### 数据库慢查询

```sql
-- 启用慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- 查看慢查询
SELECT * FROM pg_stat_statements 
WHERE mean_exec_time > 1000 
ORDER BY mean_exec_time DESC;
```

#### 内存不足

1. 检查内存使用: `free -h`
2. 优化数据库连接池大小
3. 增加服务器内存或使用swap

### 3.3 数据恢复

#### 从备份恢复

```bash
# 停止应用
sudo systemctl stop his

# 恢复数据库
gunzip < backup_20241219.sql.gz | psql -U his_user -d his_db

# 启动应用
sudo systemctl start his
```

## 四、安全维护

### 4.1 定期更新

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 更新Python依赖
cd /opt/his/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### 4.2 密钥轮换

```bash
# 更新JWT密钥
# 编辑 .env 文件，更新 SECRET_KEY
# 重启服务
sudo systemctl restart his
```

### 4.3 访问控制

```bash
# 检查防火墙规则
sudo ufw status

# 限制SSH访问
sudo ufw allow from <trusted_ip> to any port 22
```

## 五、扩容方案

### 5.1 水平扩容

- 使用负载均衡器（Nginx/HAProxy）
- 部署多个应用实例
- 共享数据库和Redis

### 5.2 垂直扩容

- 增加服务器CPU和内存
- 优化数据库配置
- 使用SSD存储

## 六、监控告警

### 6.1 监控指标

- CPU使用率
- 内存使用率
- 磁盘使用率
- 数据库连接数
- API响应时间
- 错误率

### 6.2 告警配置

配置Prometheus + Grafana或使用云监控服务。

## 七、第三方服务配置

### 7.1 配置阿里云短信

1. 登录管理后台
2. 进入"系统设置" -> "第三方服务配置"
3. 选择"阿里云短信"
4. 填写配置参数：
   - AccessKey ID
   - AccessKey Secret
   - 签名名称
   - 模板代码
5. 点击"测试"验证配置
6. 保存并启用

### 7.2 配置支付宝

1. 登录支付宝开放平台获取：
   - App ID
   - 应用私钥
   - 支付宝公钥
2. 在管理后台配置支付宝参数
3. 设置回调URL
4. 测试配置

### 7.3 配置微信支付

1. 登录微信支付商户平台获取：
   - App ID
   - 商户号
   - API密钥
   - 证书文件
2. 上传证书文件到服务器
3. 在管理后台配置微信支付参数
4. 设置回调URL
5. 测试配置

### 7.4 配置银联支付

1. 登录银联商户平台获取：
   - 商户号
   - 商户密钥
2. 在管理后台配置银联支付参数
3. 设置回调URL
4. 测试配置

## 八、维护检查清单

### 每日检查

- [ ] 服务运行状态
- [ ] 错误日志检查
- [ ] 数据库连接检查
- [ ] 磁盘空间检查

### 每周检查

- [ ] 备份文件完整性
- [ ] 性能指标检查
- [ ] 安全日志检查
- [ ] 依赖更新检查

### 每月检查

- [ ] 数据库优化（VACUUM、ANALYZE）
- [ ] 日志文件清理
- [ ] 安全更新
- [ ] 性能分析报告

