"""
数据库类型适配器
处理不同数据库之间的类型差异
"""
from sqlalchemy import TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import JSONB, ARRAY as PG_ARRAY
from app.core.config import settings


class JSONBType(TypeDecorator):
    """
    JSONB类型适配器
    在PostgreSQL中使用JSONB，在SQLite中使用JSON
    """
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class ArrayType(TypeDecorator):
    """
    ARRAY类型适配器
    在PostgreSQL中使用ARRAY，在SQLite中使用JSON
    """
    impl = JSON
    cache_ok = True
    
    def __init__(self, item_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_type = item_type
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_ARRAY(self.item_type))
        else:
            return dialect.type_descriptor(JSON())

