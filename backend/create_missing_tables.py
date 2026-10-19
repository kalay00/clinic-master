"""
创建缺失的表（用于测试）
"""
from app.core.database import engine
from sqlalchemy import text

def create_missing_tables():
    """创建缺失的表"""
    with engine.begin() as conn:
        # 创建permissions表（完整版）
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID,
                    name VARCHAR(50) NOT NULL,
                    code VARCHAR(100) NOT NULL UNIQUE,
                    resource VARCHAR(50) NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            print("✅ 创建permissions表")
            
            # 如果表已存在，检查并添加缺失的字段
            try:
                conn.execute(text("ALTER TABLE permissions ADD COLUMN IF NOT EXISTS created_by UUID"))
                conn.execute(text("ALTER TABLE permissions ADD COLUMN IF NOT EXISTS updated_by UUID"))
                print("✅ 更新permissions表字段")
            except:
                pass
        except Exception as e:
            print(f"⚠️  permissions表可能已存在: {str(e)}")
            # 尝试添加缺失的字段
            try:
                conn.execute(text("ALTER TABLE permissions ADD COLUMN IF NOT EXISTS created_by UUID"))
                conn.execute(text("ALTER TABLE permissions ADD COLUMN IF NOT EXISTS updated_by UUID"))
                print("✅ 更新permissions表字段")
            except:
                pass
        
        # 创建roles表（简化版）
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS roles (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    code VARCHAR(50) NOT NULL,
                    description TEXT,
                    is_system BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    UNIQUE(tenant_id, code)
                )
            """))
            print("✅ 创建roles表")
        except Exception as e:
            print(f"⚠️  roles表可能已存在: {str(e)}")
        
        # 创建departments表（简化版）
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS departments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    code VARCHAR(20),
                    parent_id UUID,
                    sort_order INTEGER DEFAULT 0,
                    description TEXT,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    deleted_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✅ 创建departments表")
        except Exception as e:
            print(f"⚠️  departments表可能已存在: {str(e)}")
        
        # 创建role_permissions表（关联表）
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS role_permissions (
                    role_id UUID NOT NULL,
                    permission_id UUID NOT NULL,
                    PRIMARY KEY (role_id, permission_id)
                )
            """))
            print("✅ 创建role_permissions表")
        except Exception as e:
            print(f"⚠️  role_permissions表可能已存在: {str(e)}")
        
        # 创建user_roles表（用户角色关联表）
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id UUID NOT NULL,
                    role_id UUID NOT NULL,
                    PRIMARY KEY (user_id, role_id)
                )
            """))
            print("✅ 创建user_roles表")
        except Exception as e:
            print(f"⚠️  user_roles表可能已存在: {str(e)}")
        
        # 创建family_members表（患者家庭成员）
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS family_members (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID,
                    patient_id UUID NOT NULL,
                    relation VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    gender VARCHAR(10),
                    birthday DATE,
                    age INTEGER,
                    phone VARCHAR(20),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    deleted_at TIMESTAMP WITH TIME ZONE,
                    created_by UUID,
                    updated_by UUID
                )
            """))
            print("✅ 创建family_members表")
        except Exception as e:
            print(f"⚠️  family_members表可能已存在: {str(e)}")

        print("✅ 所有必要的表已创建或已存在")

if __name__ == "__main__":
    create_missing_tables()

