"""
Celery应用配置
"""
from celery import Celery
from app.core.config import settings

# 创建Celery应用
celery_app = Celery(
    "his",
    broker=settings.RABBITMQ_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=settings.RABBITMQ_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 任务超时时间（秒）
    task_soft_time_limit=240,  # 任务软超时时间（秒）
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

