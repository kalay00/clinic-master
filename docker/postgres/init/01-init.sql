-- PostgreSQL 初始化脚本
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 设置时区
SET timezone = 'Asia/Shanghai';

-- 创建数据库（如果不存在）
-- 注意：PostgreSQL容器启动时会自动创建数据库，这里主要是创建扩展和初始化配置

