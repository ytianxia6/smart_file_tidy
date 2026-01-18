# 智能文件整理助手 (Smart File Tidy)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

基于AI的智能文件分类和整理工具，支持自然语言交互，帮助您高效管理本地文件。

## ✨ 功能特性

- 🤖 **AI驱动**：支持Claude、OpenAI、本地模型（Ollama）和**自定义API**
- 📁 **智能分类**：基于文件名、类型、元数据和内容进行分类
- 🔄 **迭代优化**：支持多轮对话，根据反馈调整分类策略
- 🛡️ **安全可靠**：操作前预览、自动备份、支持撤销
- 🚀 **批量处理**：高效处理大量文件，分批执行
- 🎨 **友好界面**：美观的CLI界面，清晰的操作预览
- 📝 **操作日志**：完整的操作记录，支持审计
- 🔧 **高度可扩展**：模块化设计，易于扩展新功能
- 🌐 **广泛兼容**：支持任何兼容OpenAI API的第三方服务

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

**方案D: 自定义API（通义千问/DeepSeek等）**
```bash
# 编辑 .env
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.example.com/v1
CUSTOM_API_KEY=your-key
CUSTOM_API_MODEL=model-name
```

💡 `.env.example`包含了8+种常见服务的配置示例！

**测试连接：**
```bash
smart-tidy config test
```

### 2. 开始整理

```bash
# 交互式模式（推荐）
smart-tidy interactive ~/Downloads

# 单次整理
smart-tidy organize ~/Downloads --request "把所有PDF论文整理到论文文件夹"

# 预览模式
smart-tidy organize ~/Downloads --request "整理图片" --dry-run

# 递归扫描
smart-tidy organize ~/Documents --recursive --request "按年份分类"
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

## 📖 文档

- [快速开始](QUICKSTART.md) - 5分钟上手指南
- [使用指南](docs/USAGE.md) - 详细使用说明
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

- [Anthropic](https://www.anthropic.com/) - Claude AI
- [OpenAI](https://openai.com/) - GPT模型
- [Ollama](https://ollama.ai/) - 本地模型支持
- [Typer](https://typer.tiangolo.com/) - CLI框架
- [Rich](https://rich.readthedocs.io/) - 终端美化

## 📮 联系方式

- 提交Issue: [GitHub Issues](https://github.com/yourusername/smart-file-tidy/issues)
- 讨论: [GitHub Discussions](https://github.com/yourusername/smart-file-tidy/discussions)

---

**如果这个项目对您有帮助，请给个⭐️Star支持一下！**
