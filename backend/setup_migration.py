"""
设置迁移版本并执行新迁移
"""
from app.core.database import engine
from sqlalchemy import text

def setup_migration():
    """设置迁移版本"""
    with engine.begin() as conn:  # 使用begin()自动提交
        # 创建alembic_version表（如果不存在）
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL PRIMARY KEY
                )
            """))
            print("✅ 创建alembic_version表")
        except Exception as e:
            print(f"⚠️  alembic_version表可能已存在: {str(e)}")
        
        # 检查当前版本
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.fetchone()
        
        if version:
            print(f"当前迁移版本: {version[0]}")
        else:
            # 插入初始版本（因为表已存在）
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('001_initial')"))
            print("✅ 已设置迁移版本为 001_initial")

if __name__ == "__main__":
    setup_migration()

