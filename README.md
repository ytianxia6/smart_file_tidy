# 智能文件整理助手 (Smart File Tidy)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

基于AI的智能文件分类和整理工具，支持自然语言交互，帮助您高效管理本地文件。

## ✨ 功能特性

- 🤖 **AI Agent驱动**：基于LangChain的智能Agent，自主决策和规划
- 🧠 **深度理解**：语义级别的文件内容分析和分类
- 🛠️ **工具化设计**：标准化的LangChain Tools，易于扩展
- 📁 **智能分类**：基于文件名、类型、元数据和内容进行分类
- 🔄 **对话交互**：支持与Agent对话，逐步优化整理方案
- 🛡️ **安全可靠**：操作前预览、自动备份、支持撤销
- 🚀 **批量处理**：高效处理大量文件，智能分批执行
- 🎨 **友好界面**：美观的CLI界面，清晰的操作预览
- 📝 **操作日志**：完整的操作记录，支持审计
- 🔧 **高度可扩展**：模块化设计，易于扩展新功能
- 🌐 **广泛兼容**：支持Claude、OpenAI、本地模型和任何OpenAI兼容API
- 🌍 **Web界面**：现代化的Web管理界面，支持可视化操作和实时进度追踪

## 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/smart-file-tidy.git
cd smart-file-tidy

# 安装依赖
pip install -r requirements.txt

# 安装工具
pip install -e .
```

## 🚀 快速开始

详细教程请查看 [QUICKSTART.md](QUICKSTART.md)

### 1. 配置AI提供商

**一键配置：**

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件，选择以下方案之一：
```

**方案A: Claude（推荐）**
```bash
# 编辑 .env
DEFAULT_AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key
```

**方案B: OpenAI**
```bash
# 编辑 .env
DEFAULT_AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

**方案C: 本地模型（免费）**
```bash
# 先启动: ollama pull llama3.1 && ollama serve
# 编辑 .env
DEFAULT_AI_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3.1
```

**方案D: 自定义API（通义千问/DeepSeek等）** ⭐
```bash
# 复制自定义API配置模板
cp env.custom.example .env

# 编辑 .env，填写您的API信息
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
CUSTOM_API_KEY=sk-your-key
CUSTOM_API_MODEL=deepseek-chat

# 验证配置
python examples/test_custom_api.py
```

💡 **使用自定义API？** 
- 查看 [自定义API与LangChain集成指南](docs/CUSTOM_API_LANGCHAIN.md) 获取详细配置说明
- `env.custom.example` 包含了6种常见服务的配置示例（DeepSeek、通义千问、Moonshot等）

**测试连接：**
```bash
# 完整测试
python examples/test_custom_api.py

# 或快速测试
smart-tidy chat
```

### 2. 开始整理

**🌟 Agent模式（推荐 - 基于LangChain）**

```bash
# Agent智能整理（自主决策）
smart-tidy agent ~/Downloads --request "按文件类型智能分类"

# 获取整理建议（不执行操作）
smart-tidy suggest ~/Downloads

# 分析单个文件
smart-tidy analyze ~/Downloads/paper.pdf

# 与Agent对话
smart-tidy chat
```

**传统模式**

```bash
# 交互式模式
smart-tidy interactive ~/Downloads

# 单次整理
smart-tidy organize ~/Downloads --request "把所有PDF论文整理到论文文件夹"

# 预览模式
smart-tidy organize ~/Downloads --request "整理图片" --dry-run
```

### 3. 其他命令

```bash
# 查看操作历史
smart-tidy history --limit 20

# 撤销最后一次操作
smart-tidy undo

# 查看配置
smart-tidy config show

# 查看帮助
smart-tidy --help
```

### 4. Web界面（可选）

除了命令行工具，本项目还提供现代化的Web管理界面。

> **新手用户？** 如果您从未安装过 Node.js，请先阅读 [Node.js 安装与运行指南](web/NODEJS_SETUP_GUIDE.md) 获取详细的环境配置教程。

**启动服务：**

```bash
# 终端1: 启动API后端服务
uvicorn src.api.main:app --reload --port 8000

# 终端2: 启动Web前端
cd web && npm run dev
```

访问 `http://localhost:3000` 即可使用Web界面。

**Web界面功能模块：**

- **文件扫描**：可视化目录扫描，查看文件统计和详细列表
- **智能整理**：引导式整理工作流，支持Agent模式和传统模式
- **历史记录**：查看操作历史，一键撤销最近操作
- **配置管理**：可视化配置AI提供商（Claude/OpenAI/本地/自定义）
- **AI对话**：与AI助手实时对话，支持流式响应

**技术特性：**

- 基于 Next.js 16 + React 19 构建
- 使用 shadcn/ui 和 Tailwind CSS 实现现代UI
- SSE (Server-Sent Events) 实现实时进度更新
- RESTful API 设计，便于集成和扩展

API文档地址：`http://localhost:8000/docs`

## 📖 文档

- [快速开始](QUICKSTART.md) - 5分钟上手指南
- [自定义API快速开始](CUSTOM_API_QUICKSTART.md) - 使用DeepSeek/通义千问等服务 🔥
- [LangChain集成](docs/LANGCHAIN_INTEGRATION.md) - Agent模式完整指南 ⭐
- [LangChain 故障排除](LANGCHAIN_FIX_GUIDE.md) - 导入错误修复指南 🔧
- [自定义API与LangChain](docs/CUSTOM_API_LANGCHAIN.md) - 详细配置和故障排除
- [使用指南](docs/USAGE.md) - 详细使用说明
- [自定义API配置](docs/CUSTOM_API.md) - 传统模式的第三方AI服务配置
- [API文档](docs/API.md) - 开发者API参考
- [项目结构](PROJECT_STRUCTURE.md) - 项目架构说明
- [贡献指南](CONTRIBUTING.md) - 如何贡献代码

## 💡 使用场景示例

### 场景1：整理下载文件夹中的论文

```bash
$ smart-tidy interactive ~/Downloads

> 请描述整理需求: 把所有PDF论文移动到论文收藏文件夹
> 
> AI分析中...
> 发现82个PDF文件
> 
> 操作预览：
> ✓ 移动 82个文件到 ~/Documents/论文收藏/
> 
> 执行? [y/N]: y
> ✓ 完成！移动了82个文件
```

### 场景2：迭代优化分类

```bash
> 请描述整理需求: 其中有些不是论文，把简历、发票等文档分开
> 
> AI重新分类中...
> 
> 发现以下非论文文件：
> - 15个简历/发票类文档 -> ~/Documents/财务文件/
> - 8个数字文件名文档 -> ~/Documents/其他文档/
> 
> 执行? [y/N]: y
> ✓ 完成！重新分类了23个文件
```

## 配置说明

配置文件位于 `config/default_config.yaml`，可自定义：

- AI提供商和模型选择
- 批处理大小
- 文件扫描深度
- 备份策略
- 日志级别

## 开发

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 代码格式化
black src/
```

## 🏗️ 技术架构

```
Web层 (Next.js + React)
    ↓
API层 (FastAPI)
    ↓
CLI层 (Typer + Rich)
    ↓
控制器层 (协调业务逻辑)
    ↓
├─ AI适配器层 (Claude/OpenAI/Local)
├─ 文件服务层 (扫描/操作/元数据)
└─ 安全服务层 (日志/备份/撤销)
```

**核心技术：**
- Python 3.9+
- Typer (CLI框架)
- Rich (美化输出)
- Pydantic (数据验证)
- PyPDF2/pdfplumber (PDF处理)
- Anthropic/OpenAI SDK (AI集成)

**Web技术栈：**
- FastAPI (RESTful API)
- Next.js 16 + React 19 (前端框架)
- shadcn/ui + Tailwind CSS (UI组件)
- SSE (实时通信)

详见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_file_scanner.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目。

### 贡献者

感谢所有为这个项目做出贡献的人！

## 📊 项目状态

- ✅ 核心功能完整
- ✅ 测试覆盖充分
- ✅ 文档完善
- 🚀 生产就绪

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🙏 致谢

**核心功能：**
- [Anthropic](https://www.anthropic.com/) - Claude AI
- [OpenAI](https://openai.com/) - GPT模型
- [Ollama](https://ollama.ai/) - 本地模型支持
- [Typer](https://typer.tiangolo.com/) - CLI框架
- [Rich](https://rich.readthedocs.io/) - 终端美化

**Web界面：**
- [Next.js](https://nextjs.org/) - React全栈框架
- [React](https://react.dev/) - 用户界面库
- [TypeScript](https://www.typescriptlang.org/) - 类型安全的JavaScript
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Python API框架
- [shadcn/ui](https://ui.shadcn.com/) - 可定制UI组件库
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的CSS框架
- [Radix UI](https://www.radix-ui.com/) - 无障碍组件原语

## 📮 联系方式

- 提交Issue: [GitHub Issues](https://github.com/yourusername/smart-file-tidy/issues)
- 讨论: [GitHub Discussions](https://github.com/yourusername/smart-file-tidy/discussions)

---

**如果这个项目对您有帮助，请给个⭐️Star支持一下！**
