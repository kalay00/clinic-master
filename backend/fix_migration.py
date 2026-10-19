"""
修复迁移版本并执行新迁移
"""
from app.core.database import engine
from sqlalchemy import text

def fix_migration():
    """修复迁移版本"""
    with engine.connect() as conn:
        # 检查alembic_version表是否存在
        try:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.fetchone()
            if version:
                print(f"当前迁移版本: {version[0]}")
            else:
                # 插入初始版本
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('001_initial')"))
                conn.commit()
                print("✅ 已设置迁移版本为 001_initial")
        except Exception as e:
            # 表不存在，创建表并插入版本
            print(f"创建alembic_version表: {str(e)}")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL PRIMARY KEY
                )
            """))
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('001_initial')"))
            conn.commit()
            print("✅ 已创建alembic_version表并设置版本为 001_initial")

if __name__ == "__main__":
    fix_migration()

