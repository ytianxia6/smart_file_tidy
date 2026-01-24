基于当前的Python项目smart_file_tidy，我需要将其功能封装为API接口，并开发一个现代化的前端Web界面来操作这些API接口。具体要求如下：

1. API接口开发：
- 将smart_file_tidy的核心功能（文件扫描、分类、整理、配置管理等）封装为RESTful API或GraphQL API
- 使用Python技术栈（推荐FastAPI或Flask）开发后端API服务
- API应支持项目现有的所有功能，包括但不限于：目录扫描、AI驱动的文件分类、文件操作执行、配置管理、历史记录查询、撤销操作等
- 确保API安全性，包含适当的认证和授权机制
- 提供完整的API文档

2. 前端界面开发：
- 使用最新的Next.js（App Router）作为前端框架
- 使用shadcn/ui组件库构建用户界面
- 使用Tailwind CSS进行样式设计
- 实现响应式设计，支持桌面端和移动端访问

3. 功能完整性：
- 前端界面应能够完整操作smart_file_tidy的所有核心功能
- 包括交互式文件整理、实时预览、操作确认、进度显示、历史记录查看等功能
- 提供直观的用户界面来配置AI提供商（Claude、OpenAI、本地模型、自定义API等）
- 支持文件操作的可视化展示和管理

4. 集成要求：
- 前端通过API接口与Python后端通信
- 实现前后端分离架构
- 确保数据传输的安全性和效率
- 提供良好的用户体验和错误处理机制

请提供完整的解决方案，包括后端API设计、前端界面设计以及前后端集成方案。



实现完成！已成功将 smart_file_tidy 封装为 API 并开发了现代化的 Web 界面。

## 完成的工作

### 后端 API (FastAPI)
- **入口**: `src/api/main.py`
- **数据模型**: `src/api/models/` (requests.py, responses.py)
- **服务层**: `src/api/services/` (scan_service, organize_service, history_service, task_manager)
- **路由**: `src/api/routers/` (scan, organize, history, config, backup, ai)
- **SSE 流式响应**: `src/api/sse/stream.py`

### 前端 Web (Next.js 15 + shadcn/ui)
- **首页**: `/` - 功能导航
- **扫描页面**: `/scan` - 目录扫描和文件列表
- **整理页面**: `/organize` - 智能整理工作流（支持 Agent 模式）
- **历史页面**: `/history` - 操作历史和撤销
- **配置页面**: `/config` - AI 提供商配置
- **AI 对话页面**: `/chat` - 流式对话

### API 端点
| 模块 | 端点 |
|------|------|
| 扫描 | POST `/api/v1/scan`, GET `/api/v1/scan/{id}` |
| 整理 | POST `/api/v1/organize/plan`, `/execute`, `/agent` |
| AI | POST `/api/v1/ai/suggest`, `/analyze`, `/chat/stream` |
| 历史 | GET `/api/v1/history/operations`, POST `/undo` |
| 配置 | GET `/api/v1/config`, PUT `/config/ai` |

## 启动方式

```bash
# 后端 (端口 8000)
cd smart_file_tidy
uvicorn src.api.main:app --reload --port 8000

# 前端 (端口 3000)
cd web
npm run dev
```

访问 http://localhost:3000 即可使用 Web 界面，前端会自动代理 API 请求到后端。





请帮我更新项目的README.md文件，仅添加关于新开发的Web界面功能的相关信息。具体包括：

1. 在适当位置添加Web界面功能的介绍
2. 包含Web界面的主要特性说明
3. 添加启动和使用Web界面的方法（前端和后端的启动命令）
4. 说明Web界面包含的功能模块（如扫描、整理、历史记录、配置、AI对话等）
5. 保持原有README内容不变，只在合适的位置插入新的Web功能相关内容
6. 格式要与现有README风格保持一致，使用适当的Markdown格式

请不要修改README中现有的其他内容，只需专注于添加Web界面相关的说明部分。


我来先读取现有的README.md文件，了解其结构和风格，然后添加Web界面相关的内容。
我来更新README.md文件，添加Web界面相关的说明。我会在适当位置插入内容，保持原有风格。
README.md 已更新完成，添加了以下Web界面相关内容：

**1. 功能特性部分** (第22行)
- 新增 "Web界面" 特性条目

**2. 快速开始章节** (第151-182行)
- 新增 "4. Web界面（可选）" 章节
- 包含后端和前端启动命令
- 列出5个功能模块说明
- 说明技术特性（Next.js 16、SSE等）
- 标注API文档地址

**3. 技术架构部分** (第254-282行)
- 架构图新增 Web层 和 API层
- 新增 "Web技术栈" 说明块

所有原有内容保持不变，新增内容与现有README风格一致。