"""
FastAPI主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import BaseAppException, exception_to_http_exception, CustomException
from app.core.response import success_response, error_response
from app.core.middleware.tenant import tenant_middleware
from app.core.middleware.jwt_auth import jwt_auth_middleware
from app.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：自动建表（模型变更自动创建新表）+ 初始化基础数据
    from app.scripts.initialize import InitializeData

    await InitializeData().init_db()
    yield
    # 关闭：释放异步引擎连接池
    from app.core.database import async_engine

    await async_engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="门诊诊所管理系统API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 多租户中间件（先注册=后执行，使用 JWT 解析出的用户信息中的 tenant_id）
app.middleware("http")(tenant_middleware)

# JWT认证中间件（后注册=先执行，先提取用户信息写入 request.state.user）
app.middleware("http")(jwt_auth_middleware)


@app.exception_handler(BaseAppException)
async def app_exception_handler(request: Request, exc: BaseAppException):
    """
    应用异常处理器
    
    Args:
        request: 请求对象
        exc: 异常对象
    
    Returns:
        JSONResponse: 错误响应
    """
    logger.error(f"应用异常: {exc.message}", exc_info=exc)
    return error_response(
        message=exc.message,
        code=exc.code,
        details=exc.details
    )


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """
    统一业务异常处理器（对齐 FastapiAdmin: CustomException）
    """
    logger.error(f"业务异常: {exc.msg}", exc_info=exc)
    return error_response(
        message=exc.msg,
        code=exc.code,
        details=exc.data,
        status_code=exc.status_code,
    )


# 专门处理FastAPI的RequestValidationError（必须在Exception处理器之前注册）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    FastAPI请求验证错误处理器
    
    Args:
        request: 请求对象
        exc: RequestValidationError异常对象
    
    Returns:
        JSONResponse: 错误响应
    """
    raw_errors = exc.errors()
    error_messages = []
    sanitized_errors = []
    for error in raw_errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "验证失败")
        error_messages.append(f"{field}: {msg}")
        # 清洗不可 JSON 序列化的对象（如校验器抛出的 ValueError 实例），避免 500
        sanitized = dict(error)
        ctx = sanitized.get("ctx")
        if isinstance(ctx, dict):
            sanitized["ctx"] = {
                k: (str(v) if isinstance(v, Exception) else v)
                for k, v in ctx.items()
            }
        sanitized_errors.append(sanitized)
    logger.warning(f"请求验证失败: {', '.join(error_messages)}")
    return error_response(
        message=f"请求数据验证失败: {', '.join(error_messages)}",
        code=422,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"errors": sanitized_errors}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器
    
    Args:
        request: 请求对象
        exc: 异常对象
    
    Returns:
        JSONResponse: 错误响应
    """
    logger.error(f"未处理的异常: {str(exc)}", exc_info=exc)
    return error_response(
        message="服务器内部错误",
        code=500
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    
    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理函数
    
    Returns:
        Response: 响应对象
    """
    import time
    
    start_time = time.time()
    
    # 记录请求信息
    tenant_id = getattr(request.state, "tenant_id", None)
    logger.info(
        f"请求: {request.method} {request.url.path} - "
        f"客户端: {request.client.host if request.client else 'unknown'} - "
        f"租户: {tenant_id or 'N/A'}"
    )
    
    response = await call_next(request)
    
    # 记录响应信息
    process_time = time.time() - start_time
    logger.info(
        f"响应: {request.method} {request.url.path} - "
        f"状态码: {response.status_code} - "
        f"耗时: {process_time:.3f}s"
    )
    
    return response

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/api")
async def api_root():
    """
    API根路径
    
    Returns:
        JSONResponse: API根路径响应
    """
    return success_response(
        data={
            "message": f"{settings.PROJECT_NAME}API",
            "version": settings.VERSION,
            "project_name": settings.PROJECT_NAME,
            "docs": "/api/docs",
        }
    )


@app.get("/health")
async def health_check():
    """
    健康检查
    
    Returns:
        JSONResponse: 健康检查响应
    """
    from app.core.redis_client import RedisClient
    from sqlalchemy import text

    # 检查数据库连接（异步）
    db_status = "healthy"
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        db_status = "unhealthy"
    
    # 检查Redis连接
    redis_status = "healthy" if RedisClient.test_connection() else "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"
    
    return success_response(
        data={
            "status": overall_status,
            "database": db_status,
            "redis": redis_status,
        }
    )

# 静态文件服务（前端资源 + 上传文件）
# 注意挂载顺序：具体的 "/uploads" 挂载必须在 "/" 前端挂载之前注册。
# 否则 "/" 的 Mount 会匹配所有路径（含 /uploads/*），把请求交给 frontend 的
# StaticFiles 处理而找不到文件，返回 404。
import os
from pathlib import Path

# 挂载上传文件目录
# __file__ = /backend/app/main.py → parents[1] = /backend（请勿再追加 .parent，否则会指向容器根目录 /）
# 容器以非 root 用户运行，不能在 / 下创建目录，故上传目录置于工作目录 /backend 内
project_root = Path(__file__).resolve().parents[1]
upload_path = project_root / settings.UPLOAD_DIR  # /backend/uploads
upload_path.mkdir(parents=True, exist_ok=True)  # 确保目录存在
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

# 挂载前端静态文件（最后注册，"/" 会匹配所有路径，必须放在具体挂载之后）
# 容器内 frontend 通过 compose 卷挂载在 /frontend（与 /backend 平级的独立路径）。
# 物理路径固定为 /frontend，避免依赖“backend 是项目子目录”的目录结构假设。
frontend_path = "/frontend"
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

