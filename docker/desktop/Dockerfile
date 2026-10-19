# 桌面端（Vue3 + Vite + Electron）Dockerfile —— 多阶段构建
# 仅在容器内构建 Web 静态资源（vite build），并跳过 Electron 二进制下载，
# 因此无需 GUI / macOS 签名即可用 Docker 完成构建与部署测试。
# 运行阶段用 nginx 托管 dist/，并将 /api、/uploads、/ws 反向代理到后端 his-backend。

# ===================== 构建阶段 =====================
FROM node:22-alpine AS builder

WORKDIR /app

# 跳过 Electron / Puppeteer 二进制下载（只需要 vite build，不需要 electron 运行时）
ENV ELECTRON_SKIP_BINARY_DOWNLOAD=1 \
    PUPPETEER_SKIP_DOWNLOAD=1 \
    NODE_OPTIONS=--max-old-space-size=2048

# 使用国内镜像加速依赖安装
RUN npm config set registry https://registry.npmmirror.com

# 仅复制依赖清单先安装（利用 Docker 层缓存）
COPY desktop/package.json ./

RUN npm install

# 注入 Docker 环境 API 地址为相对路径，由 nginx 统一反向代理到后端
ARG VITE_API_BASE_URL=/api/v1
ARG VITE_USE_MOCK=false
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_USE_MOCK=$VITE_USE_MOCK

# 复制源码并构建（输出到 /app/dist）
COPY desktop/ .
RUN npm run build

# ===================== 运行阶段 =====================
FROM nginx:alpine

# 托管构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx 站点配置（托管 SPA + 反向代理后端）
COPY docker/desktop/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
