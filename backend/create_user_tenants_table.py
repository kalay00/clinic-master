"""
创建 user_tenants 表的脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text
from app.core.logger import logger

def create_user_tenants_table():
    """创建 user_tenants 表"""
    try:
        with engine.connect() as conn:
            # 检查表是否已存在
            check_sql = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_tenants'
                );
            """)
            result = conn.execute(check_sql)
            exists = result.scalar()
            
            if exists:
                logger.info("user_tenants 表已存在，跳过创建")
                return
            
            # 创建表
            create_sql = text("""
                CREATE TABLE user_tenants (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
                    is_primary BOOLEAN DEFAULT FALSE,
                    last_accessed_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT uq_user_tenant UNIQUE (user_id, tenant_id)
                );
                
                CREATE INDEX ix_user_tenants_user_id ON user_tenants(user_id);
                CREATE INDEX ix_user_tenants_tenant_id ON user_tenants(tenant_id);
                
                COMMENT ON TABLE user_tenants IS '用户租户关联表';
                COMMENT ON COLUMN user_tenants.id IS '主键ID';
                COMMENT ON COLUMN user_tenants.user_id IS '用户ID';
                COMMENT ON COLUMN user_tenants.tenant_id IS '租户ID';
                COMMENT ON COLUMN user_tenants.is_primary IS '是否为主要租户';
                COMMENT ON COLUMN user_tenants.last_accessed_at IS '最后访问时间';
                COMMENT ON COLUMN user_tenants.created_at IS '创建时间';
                COMMENT ON COLUMN user_tenants.updated_at IS '更新时间';
            """)
            
            conn.execute(create_sql)
            conn.commit()
            logger.info("✅ user_tenants 表创建成功")
            
            # 为现有用户创建关联记录（如果用户和租户存在）
            # 获取所有用户及其租户
            populate_sql = text("""
                INSERT INTO user_tenants (user_id, tenant_id, is_primary, created_at, updated_at)
                SELECT 
                    u.id as user_id,
                    u.tenant_id,
                    TRUE as is_primary,
                    u.created_at,
                    u.updated_at
                FROM users u
                WHERE u.tenant_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM user_tenants ut 
                    WHERE ut.user_id = u.id AND ut.tenant_id = u.tenant_id
                )
                ON CONFLICT (user_id, tenant_id) DO NOTHING;
            """)
            
            result = conn.execute(populate_sql)
            conn.commit()
            logger.info(f"✅ 为现有用户创建了 {result.rowcount} 条关联记录")
            
    except Exception as e:
        logger.error(f"❌ 创建 user_tenants 表失败: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    create_user_tenants_table()

