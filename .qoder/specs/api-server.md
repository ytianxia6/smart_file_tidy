# Smart File Tidy Web 界面实现计划

## 概述

将 smart_file_tidy 的核心功能封装为 RESTful API，并开发现代化前端 Web 界面。

- **后端**: FastAPI + SSE (Server-Sent Events)
- **前端**: Next.js 16 (App Router + Turbopack) + shadcn/ui + Tailwind CSS
- **部署**: 同一端口 (Next.js proxy.ts 代理到 FastAPI)
- **认证**: 暂不需要
- **Node.js**: 20.9+ (Next.js 16 要求)

## 一、项目结构

```
smart_file_tidy/
├── src/
│   ├── api/                      # 新增：FastAPI 应用
│   │   ├── main.py               # FastAPI 入口
│   │   ├── dependencies.py       # 依赖注入
│   │   ├── models/               # API Pydantic 模型
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   ├── routers/              # 路由模块
│   │   │   ├── scan.py
│   │   │   ├── organize.py
│   │   │   ├── history.py
│   │   │   ├── backup.py
│   │   │   └── config.py
│   │   ├── services/             # 服务层（封装核心模块）
│   │   │   ├── scan_service.py
│   │   │   ├── organize_service.py
│   │   │   ├── history_service.py
│   │   │   └── task_manager.py
│   │   └── sse/                  # SSE 流式响应
│   │       └── stream.py
│   ├── core/                     # 现有核心模块（不修改）
│   ├── cli/                      # 现有 CLI（不修改）
│   └── ...
├── web/                          # 新增：前端应用
│   ├── app/                      # Next.js App Router
│   ├── proxy.ts                  # Next.js 16 代理配置（替代 middleware）
│   ├── components/
│   ├── lib/
│   └── ...
└── requirements-api.txt          # API 额外依赖
```

## 二、API 端点设计

### 2.1 扫描 `/api/v1/scan`

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/scan` | 扫描目录 |
| GET | `/api/v1/scan/{scan_id}` | 获取扫描结果 |

### 2.2 整理 `/api/v1/organize`

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/organize/plan` | 生成整理方案（不执行） |
| POST | `/api/v1/organize/execute` | 执行整理方案 |
| POST | `/api/v1/organize/agent` | Agent 模式整理 |
| GET | `/api/v1/organize/{task_id}` | 查询任务状态 |
| POST | `/api/v1/organize/refine` | 根据反馈优化方案 |

### 2.3 AI `/api/v1/ai`

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/ai/suggest` | 获取整理建议 |
| POST | `/api/v1/ai/analyze` | 分析单个文件 |
| POST | `/api/v1/ai/chat` | AI 对话 |

### 2.4 历史 `/api/v1/history`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/history/operations` | 操作历史列表 |
| POST | `/api/v1/history/undo` | 撤销最后操作 |

### 2.5 备份 `/api/v1/backup`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/backup/points` | 备份点列表 |
| POST | `/api/v1/backup/create` | 创建备份 |
| POST | `/api/v1/backup/restore` | 恢复备份 |
| DELETE | `/api/v1/backup/{id}` | 删除备份 |

### 2.6 配置 `/api/v1/config`

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/config` | 获取配置 |
| PUT | `/api/v1/config/ai` | 更新 AI 配置 |
| POST | `/api/v1/config/validate` | 验证配置 |

### 2.7 SSE (Server-Sent Events)

| 路径 | 描述 |
|------|------|
| `GET /api/v1/organize/{task_id}/stream` | 整理任务实时进度 |
| `POST /api/v1/ai/chat/stream` | AI 对话流式输出 |

## 三、关键数据模型

### 请求模型

```python
# ScanRequest
class ScanRequest(BaseModel):
    directory: str
    recursive: bool = False
    extensions: Optional[List[str]] = None
    include_metadata: bool = True

# OrganizeAgentRequest
class OrganizeAgentRequest(BaseModel):
    directory: str
    request: str
    provider: Optional[str] = None  # claude/openai/local/custom
    dry_run: bool = False
    create_backup: bool = True

# ExecuteRequest
class ExecuteRequest(BaseModel):
    operations: List[OperationModel]
    create_backup: bool = True
```

### 响应模型

```python
# ScanResponse
class ScanResponse(BaseModel):
    scan_id: str
    total_files: int
    files: List[FileInfoModel]
    stats: Dict[str, Any]

# TaskResponse
class TaskResponse(BaseModel):
    task_id: str
    status: Literal["pending", "running", "completed", "failed"]
    progress: int = 0
    operations: Optional[List[OperationModel]] = None
    result: Optional[OperationResultModel] = None
    error: Optional[str] = None
```

## 四、前端页面结构

```
web/app/
├── layout.tsx                    # 根布局（导航栏）
├── page.tsx                      # 首页
├── scan/page.tsx                 # 文件扫描
├── organize/
│   ├── page.tsx                  # 整理工作流
│   └── result/[taskId]/page.tsx  # 执行结果
├── history/page.tsx              # 操作历史
├── config/page.tsx               # 配置管理
└── chat/page.tsx                 # AI 对话
```

### 核心组件

| 组件 | 描述 |
|------|------|
| `FileList` | 文件列表（虚拟滚动） |
| `OperationPreview` | 操作预览表格 |
| `OrganizeWorkflow` | 整理工作流（步骤向导） |
| `ProgressBar` | 实时进度条 |
| `AIProviderSelector` | AI 提供商选择器 |
| `ChatInterface` | AI 对话界面 |
| `BackupManager` | 备份管理面板 |

## 五、实现步骤

### 阶段 1: 后端 API 基础

1. **创建 FastAPI 应用结构**
   - 文件: `src/api/main.py`
   - 配置 CORS、中间件、异常处理

2. **实现服务层**
   - `src/api/services/scan_service.py` - 封装 FileScanner
   - `src/api/services/organize_service.py` - 封装 Controller
   - `src/api/services/history_service.py` - 封装 OperationLogger
   - `src/api/services/task_manager.py` - 任务状态管理

3. **实现 API 路由**
   - `src/api/routers/scan.py`
   - `src/api/routers/organize.py`
   - `src/api/routers/history.py`
   - `src/api/routers/config.py`
   - `src/api/routers/backup.py`

4. **添加依赖注入**
   - `src/api/dependencies.py` - ConfigManager、Controller 注入

### 阶段 2: SSE 实时通信

1. **实现 SSE 端点**
   - `src/api/sse/stream.py` - 流式响应工具函数
   - `src/api/routers/organize.py` - 添加 `/{task_id}/stream` 端点

2. **修改 FileOperator 支持进度回调**
   - 添加 `progress_callback` 参数

### 阶段 3: 前端基础设施

1. **初始化 Next.js 16 项目**
   ```bash
   npx create-next-app@latest web --typescript --tailwind --app --turbopack
   cd web
   npx shadcn@latest init
   ```

2. **安装依赖**
   ```bash
   npm install swr
   npx shadcn@latest add button card table dialog toast progress tabs input textarea select
   ```

3. **配置 proxy.ts (Next.js 16 代理)**
   ```typescript
   // web/proxy.ts
   import { proxy } from 'next/server'
   
   export default proxy({
     '/api/v1': 'http://localhost:8000',
   })
   ```

4. **创建 API 客户端**
   - `web/lib/api/client.ts`
   - `web/lib/api/scan.ts`
   - `web/lib/api/organize.ts`
   - `web/lib/api/sse.ts`

### 阶段 4: 核心功能页面

1. **扫描页面** - `web/app/scan/page.tsx`
   - 目录输入
   - 扫描选项
   - 文件列表展示

2. **整理工作流** - `web/app/organize/page.tsx`
   - Step 1: 选择目录
   - Step 2: 输入需求
   - Step 3: 预览方案
   - Step 4: 执行操作

3. **历史页面** - `web/app/history/page.tsx`
   - 操作时间线
   - 撤销功能

4. **配置页面** - `web/app/config/page.tsx`
   - AI 提供商配置
   - API Key 管理

### 阶段 5: AI 交互功能

1. **AI 对话** - `web/app/chat/page.tsx`
   - 流式输出支持
   - 上下文管理

2. **智能建议集成**
   - 一键获取建议
   - 应用建议到方案

### 阶段 6: 测试与优化

1. **API 测试**
   - pytest 单元测试

2. **性能优化**
   - 虚拟滚动
   - 响应缓存

## 六、关键文件清单

### 后端关键文件

| 文件 | 描述 |
|------|------|
| `src/api/main.py` | FastAPI 入口 |
| `src/api/services/organize_service.py` | 核心业务逻辑 |
| `src/api/routers/organize.py` | 整理 API 端点 |
| `src/api/sse/stream.py` | SSE 流式响应 |
| `src/api/services/task_manager.py` | 任务状态管理 |

### 前端关键文件

| 文件 | 描述 |
|------|------|
| `web/app/organize/page.tsx` | 整理工作流主页 |
| `web/proxy.ts` | Next.js 16 API 代理配置 |
| `web/lib/api/organize.ts` | API 客户端 |
| `web/lib/api/sse.ts` | SSE 客户端管理 |
| `web/components/organize/OrganizeWorkflow.tsx` | 工作流组件 |

### 依赖配置

**requirements-api.txt**
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
sse-starlette>=1.8.0
```

## 七、验证方案

1. **启动后端** (开发模式，端口 8000)
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

2. **启动前端** (开发模式，端口 3000，Turbopack 默认启用)
   ```bash
   cd web && npm run dev
   ```

3. **生产部署** (同一端口)
   - Next.js API Routes 代理请求到 FastAPI
   - 或使用 Nginx 反向代理

4. **测试工作流**
   - 访问 http://localhost:3000
   - 扫描测试目录
   - 生成整理方案
   - 执行操作（观察 SSE 实时进度）
   - 查看历史记录
   - 测试撤销功能
   - 测试 AI 对话（流式输出）

5. **API 文档**
   - 访问 http://localhost:8000/docs

## 八、安全与部署考虑

1. **路径验证** - 防止目录遍历攻击
2. **CORS 配置** - 开发时允许 localhost:3000
3. **敏感信息** - API Key 环境变量存储
4. **Next.js 16 代理配置** (proxy.ts)
   ```typescript
   // web/proxy.ts
   import { proxy } from 'next/server'
   
   export default proxy({
     '/api/v1': {
       target: 'http://localhost:8000',
       // 生产环境可改为内部服务地址
     },
   })
   ```
