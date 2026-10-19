#!/usr/bin/env python3
"""测试数据库连接"""
import sys
from app.core.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ 数据库连接成功")
        sys.exit(0)
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
    sys.exit(1)

