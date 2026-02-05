# ==========================================
# Stage 1: 构建前端
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/ui

# 复制前端依赖文件
COPY ui/package*.json ./

# 安装依赖
RUN npm install

# 复制前端源码
COPY ui/ ./

# 构建前端
RUN npm run build

# ==========================================
# Stage 2: 构建最终镜像
# ==========================================
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 包管理器
RUN pip install uv

# 复制 Python 项目配置
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-dev

# 复制后端源码
COPY app/ ./app/
COPY app.py ./

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/ui/dist ./ui/dist

# 创建数据目录
RUN mkdir -p /app/data /app/file

# 设置环境变量
ENV MINERU_CENTER_HOST=0.0.0.0
ENV MINERU_CENTER_PORT=8000
ENV MINERU_CENTER_DEBUG=false

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/stats || exit 1

# 启动命令
CMD ["uv", "run", "python", "app.py"]
