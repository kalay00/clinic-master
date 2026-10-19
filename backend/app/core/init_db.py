"""
数据库初始化脚本
用于创建初始数据和基础配置
"""
from sqlalchemy.orm import Session

# 注意：database.py 里 engine 别名指向 async_engine；建表是同步操作，必须用 sync_engine
from app.core.database import sync_engine as engine, Base
from app.core.database import BaseModel


def init_database() -> None:
    """
    初始化数据库
    创建所有表结构
    """
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def init_data() -> None:
    """
    初始化基础数据
    创建系统默认数据
    """
    from app.core.init_test_data import init_test_data
    
    print("初始化基础数据...")
    init_test_data()
    print("基础数据初始化完成！")


if __name__ == "__main__":
    init_database()
    init_data()

