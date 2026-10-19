"""
数据库会话管理
提供数据库会话的上下文管理器
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    获取数据库会话的上下文管理器
    
    Yields:
        Session: 数据库会话对象
    
    Example:
        ```python
        with get_db_session() as db:
            user = db.query(User).first()
        ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

