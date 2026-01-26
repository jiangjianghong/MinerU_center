# MinerU Center

MinerU Center 是一个统一管理多个 MinerU 实例的中心服务，提供请求队列管理、负载均衡、热配置等功能。

## 功能特性

- **任务队列管理**：基于优先级的任务队列，支持配置队列大小限制
- **实例池管理**：管理多个 MinerU 实例，支持健康检查
- **负载均衡**：自动将任务分发到空闲实例
- **热配置**：无需重启即可更新服务配置
- **实时监控**：基于 WebSocket 的队列和实例状态实时更新
- **重试机制**：失败任务自动重试，支持配置重试策略

## 项目结构

```
MinerU_center/
├── app/                     # 后端代码
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── models/              # 数据模型
│   ├── services/            # 核心服务
│   ├── api/                 # API 路由
│   └── utils/               # 工具函数
├── ui/                      # 前端代码 (Vue 3 + Element Plus)
│   ├── src/
│   │   ├── main.js
│   │   ├── App.vue
│   │   ├── api/             # API 客户端
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # 状态管理
│   │   └── i18n/            # 国际化
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── pyproject.toml
├── run.py
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (Python 包管理器)

### 安装与运行

```bash
cd MinerU_center

# 安装后端依赖
uv sync

# 构建前端
cd ui
npm install
npm run build
cd ..

# 启动服务
uv run python run.py
```

服务启动后访问 http://localhost:8000/ui

### 开发模式

```bash
# 终端 1：启动后端
uv run python run.py

# 终端 2：启动前端开发服务器
cd ui
npm run dev
```

前端开发服务器运行在 http://localhost:5173，会自动代理 API 请求到后端。

## API 接口

### 任务接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/tasks` | 提交任务 |
| GET | `/api/tasks/{task_id}` | 获取任务状态/结果 |
| GET | `/api/tasks` | 获取任务列表 |
| DELETE | `/api/tasks/{task_id}` | 取消任务 |

**提交任务请求体：**
```json
{
  "async": false,
  "priority": 5,
  "payload": {
    "file_url": "...",
    "options": {}
  }
}
```

### 实例接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/instances` | 获取所有实例 |
| POST | `/api/instances` | 添加实例 |
| DELETE | `/api/instances/{id}` | 移除实例 |
| POST | `/api/instances/{id}/enable` | 启用实例 |
| POST | `/api/instances/{id}/disable` | 禁用实例 |

### 配置接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/config` | 获取当前配置 |
| PATCH | `/api/config` | 更新配置（热更新） |

### 统计接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats` | 获取实时统计 |
| WS | `/api/stats/ws` | WebSocket 实时推送 |

## 配置项说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `task_timeout` | 300 | 任务执行超时时间（秒） |
| `queue_timeout` | 600 | 排队超时时间（秒） |
| `max_queue_size` | 100 | 最大队列长度 |
| `enable_priority` | true | 是否启用优先级调度 |
| `max_retries` | 3 | 最大重试次数 |
| `retry_delay` | 5 | 重试间隔（秒） |
| `health_check_interval` | 30 | 健康检查间隔（秒） |
| `instance_timeout` | 10 | 实例请求超时（秒） |

## 使用示例

### 提交同步任务
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"payload": {"file_url": "test.pdf"}}'
```

### 提交异步任务
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"async": true, "priority": 8, "payload": {"file_url": "test.pdf"}}'
```

### 添加 MinerU 实例
```bash
curl -X POST http://localhost:8000/api/instances \
  -H "Content-Type: application/json" \
  -d '{"name": "MinerU-1", "url": "http://localhost:8080"}'
```

### 更新配置
```bash
curl -X PATCH http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{"max_retries": 5, "task_timeout": 600}'
```

## 界面说明

界面支持中英文切换，默认显示中文。点击右上角的语言按钮可以切换语言。

## 许可证

MIT
