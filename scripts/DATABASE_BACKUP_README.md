# 数据库备份和恢复说明

## 备份目录

备份文件存储在：`/数据库备份目录`

## 备份脚本

### 自动备份脚本

**脚本位置**: `scripts/backup_databases.sh`

**使用方法**:
```bash
bash scripts/backup_databases.sh
```

**功能**:
- 自动备份PostgreSQL数据库（自定义格式）
- 自动备份Redis数据库（RDB格式）
- 生成备份信息文件
- 显示备份结果和文件大小

**备份文件命名规则**:
- PostgreSQL: `his_postgres_YYYYMMDD_HHMMSS.dump`
- Redis: `his_redis_YYYYMMDD_HHMMSS.rdb`
- 备份信息: `backup_info_YYYYMMDD_HHMMSS.txt`

## 恢复脚本

### 数据库恢复脚本

**脚本位置**: `scripts/restore_databases.sh`

**使用方法**:
```bash
bash scripts/restore_databases.sh
```

**功能**:
- 交互式选择备份文件
- 恢复PostgreSQL数据库
- 恢复Redis数据库
- 安全确认机制

## 手动备份方法

### PostgreSQL备份

```bash
# 1. 在容器内执行备份
podman exec his_postgres pg_dump -U his_user -d his_db -F c -f /tmp/backup.dump

# 2. 从容器复制到宿主机
podman cp his_postgres:/tmp/backup.dump /数据库备份目录/his_postgres_$(date +%Y%m%d_%H%M%S).dump

# 3. 删除容器内的临时文件
podman exec his_postgres rm /tmp/backup.dump
```

### Redis备份

```bash
# 1. 执行Redis后台保存
podman exec his_redis redis-cli -a redis_password BGSAVE

# 2. 等待保存完成（通常几秒钟）
sleep 5

# 3. 从容器复制RDB文件到宿主机
podman cp his_redis:/data/dump.rdb /数据库备份目录/his_redis_$(date +%Y%m%d_%H%M%S).rdb
```

## 手动恢复方法

### PostgreSQL恢复

```bash
# 1. 复制备份文件到容器
podman cp /数据库备份目录/his_postgres_YYYYMMDD_HHMMSS.dump his_postgres:/tmp/restore.dump

# 2. 执行恢复（-c 表示先删除现有对象）
podman exec his_postgres pg_restore -U his_user -d his_db -c -F c /tmp/restore.dump

# 3. 删除容器内的临时文件
podman exec his_postgres rm /tmp/restore.dump
```

### Redis恢复

```bash
# 1. 停止Redis容器
podman stop his_redis

# 2. 复制备份文件到容器
podman cp /数据库备份目录/his_redis_YYYYMMDD_HHMMSS.rdb his_redis:/data/dump.rdb

# 3. 启动Redis容器
podman start his_redis

# 4. 验证Redis是否正常
podman exec his_redis redis-cli -a redis_password ping
```

## 定时备份

### 使用cron定时备份

编辑crontab:
```bash
crontab -e
```

添加定时任务（每天凌晨2点备份）:
```bash
0 2 * * * /home/laknl/his/scripts/backup_databases.sh >> /home/laknl/his/logs/backup.log 2>&1
```

### 备份保留策略

建议定期清理旧备份文件，只保留最近N天的备份：

```bash
# 删除7天前的备份文件
find /数据库备份目录 -name "his_postgres_*.dump" -mtime +7 -delete
find /数据库备份目录 -name "his_redis_*.rdb" -mtime +7 -delete
find /数据库备份目录 -name "backup_info_*.txt" -mtime +7 -delete
```

## 备份验证

### 验证PostgreSQL备份

```bash
# 检查备份文件格式
podman exec his_postgres pg_restore -l /tmp/backup.dump | head -20
```

### 验证Redis备份

```bash
# 检查RDB文件是否存在
podman exec his_redis ls -lh /data/dump.rdb
```

## 注意事项

1. **备份前检查**
   - 确保数据库容器正在运行
   - 确保有足够的磁盘空间
   - 确保备份目录有写权限

2. **恢复前准备**
   - ⚠️ **恢复操作会覆盖现有数据**
   - 恢复前建议先备份当前数据
   - 恢复时确保数据库容器正在运行

3. **备份文件管理**
   - 定期检查备份文件完整性
   - 定期清理旧备份文件
   - 建议将重要备份文件复制到其他位置

4. **安全建议**
   - 备份文件包含敏感数据，注意权限控制
   - 建议加密存储备份文件
   - 定期测试恢复流程

## 故障排查

### PostgreSQL备份失败

1. 检查容器是否运行: `podman ps | grep his_postgres`
2. 检查数据库连接: `podman exec his_postgres psql -U his_user -d his_db -c "SELECT 1;"`
3. 检查磁盘空间: `df -h`

### Redis备份失败

1. 检查容器是否运行: `podman ps | grep his_redis`
2. 检查Redis连接: `podman exec his_redis redis-cli -a redis_password ping`
3. 检查BGSAVE状态: `podman exec his_redis redis-cli -a redis_password LASTSAVE`

## 相关文件

- 备份脚本: `scripts/backup_databases.sh`
- 恢复脚本: `scripts/restore_databases.sh`
- 备份目录: `/数据库备份目录`
- 环境配置: `env.example`

