# 门诊诊所管理系统 - 后端Dockerfile
# 构建上下文: outpatient-management-system/ (compose 中 build.context: ../)
# 运行时将宿主机 backend/ 挂载到容器 /backend
FROM python:3.13.2

# 工作目录与运行时挂载路径保持一致
WORKDIR /backend

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖（asyncmy/pymysql 等可能需要 gcc 编译）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY ./backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY ./backend/ .

# 创建非root用户，并预建上传目录（确保运行时可写）
RUN mkdir -p /backend/uploads && \
    useradd -m -u 1000 hisuser && \
    chown -R hisuser:hisuser /backend

USER hisuser

# 暴露端口（与 compose 中 9000:9000 对应）
EXPOSE 9000

# 健康检查（使用标准库 urllib，避免额外依赖）
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9000/health')" || exit 1

# 启动命令（本系统入口为 app.main:app）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
