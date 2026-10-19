"""
应用配置管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 项目信息
    PROJECT_NAME: str = "诊所管理系统"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 数据库配置
    # 优先使用DATABASE_URL，如果没有则从单独参数构建
    DATABASE_URL: str = ""
    POSTGRES_USER: str = "his_user"
    POSTGRES_PASSWORD: str = "his_password"
    POSTGRES_DB: str = "his_db"
    POSTGRES_HOST: str = "localhost"  # Docker环境使用postgres，本地环境使用localhost
    POSTGRES_PORT: int = 5432
    
    # Redis配置
    # 优先使用REDIS_URL，如果没有则从单独参数构建
    REDIS_URL: str = ""
    REDIS_HOST: str = "localhost"  # Docker环境使用redis，本地环境使用localhost
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "redis_password"
    REDIS_DB: int = 0
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 加密配置
    ENCRYPTION_KEY: str = "your-encryption-key-change-in-production"
    
    # 消息队列配置
    RABBITMQ_URL: str = "amqp://his_mq_user:his_mq_password@localhost:5672/"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"  # 上传文件存储目录（相对于项目根目录）
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 最大上传文件大小（5MB）
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]  # 允许的图片扩展名
    
    model_config = SettingsConfigDict(
        env_file=None,  # 不使用.env文件，使用代码中的默认值
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # 忽略未定义的字段
    )
    
    def __init__(self, **kwargs):
        """初始化配置，自动构建DATABASE_URL和REDIS_URL"""
        super().__init__(**kwargs)
        
        # 如果没有提供DATABASE_URL，从单独参数构建
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        
        # 如果没有提供REDIS_URL，从单独参数构建
        if not self.REDIS_URL:
            if self.REDIS_PASSWORD:
                self.REDIS_URL = (
                    f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
                )
            else:
                self.REDIS_URL = (
                    f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
                )


settings = Settings()

