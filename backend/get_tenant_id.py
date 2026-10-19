"""
获取租户ID用于测试
"""
from app.core.database import engine
from sqlalchemy import text

def get_tenant_id():
    """获取第一个租户ID"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM tenants LIMIT 1"))
        row = result.fetchone()
        if row:
            print(row[0])
            return str(row[0])
        else:
            print("None")
            return None

if __name__ == "__main__":
    get_tenant_id()

