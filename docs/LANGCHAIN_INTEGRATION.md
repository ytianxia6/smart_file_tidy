# LangChain 集成文档

## 概述

智能文件整理助手已集成 LangChain 框架，提供更强大的 AI Agent 能力。Agent 模式可以自主决策、理解上下文、并执行复杂的文件整理任务。

## 架构设计

### 核心组件

```
CLI层
  ↓
LangChain Agent (决策引擎)
  ↓
├─ LangChain LLM (Claude/OpenAI/Custom/Local)
└─ LangChain Tools
    ├─ FileScanner Tool (扫描文件)
    ├─ FileAnalyzer Tool (分析文件内容)
    ├─ FileOperator Tool (移动/重命名)
    └─ ValidationTool (验证操作)
```

### 工作流程

1. **文件扫描**: Agent 使用 FileScanner Tool 扫描目录
2. **内容分析**: 使用 FileAnalyzer Tool 深度分析文件内容
3. **方案制定**: Agent 基于分析结果自主制定整理方案
4. **安全验证**: 使用 ValidationTool 验证操作安全性
5. **执行操作**: 使用 FileOperator Tool 执行文件操作
6. **结果报告**: 向用户报告执行结果和统计信息

## 使用指南

### 1. Agent 模式整理文件

使用 Agent 模式智能整理文件（推荐）：

```bash
# 基本用法
smart-tidy agent /path/to/directory --request "按文件类型分类"

# 使用特定AI提供商
smart-tidy agent /path/to/directory --request "整理学术论文" --provider claude

# 仅模拟操作（不实际执行）
smart-tidy agent /path/to/directory --request "清理重复文件" --dry-run
```

**示例需求**：
- "按文件类型分类到不同文件夹"
- "将所有PDF论文移动到Papers文件夹"
- "按年份组织照片"
- "清理临时文件和重复文件"
- "整理代码文件，按编程语言分类"

### 2. 获取整理建议

让 Agent 分析目录并提供整理建议（不执行操作）：

```bash
smart-tidy suggest /path/to/directory
```

Agent 会：
- 分析目录结构和文件分布
- 识别文件类型和命名模式
- 提出多种整理方案
- 说明每种方案的优缺点

### 3. 分析单个文件

深度分析文件内容和特征：

```bash
smart-tidy analyze /path/to/file.pdf
```

输出信息：
- 文件基本信息（大小、类型、修改时间）
- 文件元数据（PDF标题、作者、页数等）
- 内容分析（主题、关键词、语言等）
- 分类建议

### 4. 交互式对话

与 Agent 进行交互式对话：

```bash
smart-tidy chat
```

你可以：
- 询问文件整理建议
- 逐步优化整理方案
- 了解特定文件的信息
- 学习文件管理最佳实践

输入 `quit` 或 `exit` 退出对话。

## 配置

### LangChain 配置

在 `config/default_config.yaml` 中配置：

```yaml
langchain:
  agent:
    type: openai-tools  # Agent类型
    verbose: true       # 是否显示详细信息
    max_iterations: 15  # 最大迭代次数
    max_execution_time: 300  # 超时时间（秒）
  
  tools:
    file_scanner:
      max_files: 1000
      recursive: true
    
    file_analyzer:
      content_analysis: true
      max_content_size: 2000  # 分析的最大字符数
    
    file_operator:
      dry_run: false
      batch_size: 50
```

### AI 提供商配置

通过 `.env` 文件配置 API 密钥：

```ini
# Claude
ANTHROPIC_API_KEY=sk-ant-xxx

# OpenAI
OPENAI_API_KEY=sk-xxx

# 自定义API
CUSTOM_API_BASE_URL=https://api.example.com/v1
CUSTOM_API_KEY=sk-xxx
CUSTOM_API_MODEL=your-model

# 本地LLM (Ollama)
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3.1
```

## LangChain Tools 详解

### FileScannerTool

扫描目录并获取文件信息。

**功能**：
- 列出目录中的所有文件
- 提取文件基本信息
- 读取文件内容样本
- 提取文件元数据

**参数**：
- `directory`: 目标目录路径
- `recursive`: 是否递归扫描（默认False）
- `extensions`: 文件扩展名过滤
- `include_content`: 是否包含内容样本（默认True）

### FileAnalyzerTool

深度分析单个文件的内容和特征。

**功能**：
- 识别文件类型
- 提取文件元数据
- 分析文件内容
- 提取关键信息和模式

**参数**：
- `file_path`: 文件路径
- `analyze_content`: 是否分析内容（默认True）

### FileOperatorTool

执行文件系统操作。

**功能**：
- 移动文件
- 重命名文件
- 创建文件夹

**参数**：
- `operation_type`: 操作类型（move/rename/create_folder）
- `source`: 源路径
- `target`: 目标路径
- `reason`: 操作原因

**安全特性**：
- 自动验证文件存在
- 自动处理命名冲突
- 所有操作可记录和撤销

### ValidationTool

验证文件和路径状态。

**功能**：
- 检查文件是否存在
- 验证路径有效性
- 检查磁盘空间

**参数**：
- `validation_type`: 验证类型（file_exists/path_valid/disk_space）
- `paths`: 要验证的路径（逗号分隔）

## 高级特性

### 1. 对话记忆

Agent 具有会话记忆能力，可以：
- 记住之前的对话内容
- 理解上下文和引用
- 学习用户偏好
- 提供连贯的交互体验

### 2. 自主决策

Agent 可以根据情况自主决策：
- 选择合适的工具
- 制定执行计划
- 处理边缘情况
- 优化操作流程

### 3. 内容理解

基于 LLM 的深度内容分析：
- 语义级别的文件分类
- 智能关键词提取
- 内容主题识别
- 上下文感知

### 4. 错误处理

智能错误处理和恢复：
- 自动验证操作安全性
- 处理文件名冲突
- 提供清晰的错误信息
- 支持操作撤销

## 传统模式 vs Agent 模式

### 传统模式

```bash
smart-tidy organize /path/to/dir --request "按类型分类"
```

**特点**：
- 单次执行
- 预定义工作流
- 固定的分类逻辑
- 较快的执行速度

### Agent 模式

```bash
smart-tidy agent /path/to/dir --request "按类型分类"
```

**特点**：
- 自主决策
- 灵活的工作流
- 智能的分类逻辑
- 更强的适应能力

**建议**：
- 简单任务：使用传统模式
- 复杂任务：使用 Agent 模式
- 探索性任务：使用 `suggest` 和 `chat` 命令

## 性能优化

### 1. Token 优化

- 限制文件内容样本长度
- 批量处理文件
- 精简 Prompt 设计

### 2. 缓存策略

- 缓存文件分析结果
- 缓存 LLM 响应
- 复用元数据提取

### 3. 并发处理

- 并行扫描文件
- 并行分析内容
- 批量执行操作

## 故障排除

### 问题1: Agent 初始化失败

**错误**: "Agent模式初始化失败"

**解决**：
1. 检查 LangChain 依赖是否安装：`pip install -r requirements.txt`
2. 检查 API 密钥是否配置
3. 查看详细错误信息

### 问题2: Token 超限

**错误**: "Token limit exceeded"

**解决**：
1. 减少单次处理的文件数量
2. 使用 `--dry-run` 测试
3. 调整 `max_content_size` 配置

### 问题3: 连接超时

**错误**: "Connection timeout"

**解决**：
1. 检查网络连接
2. 增加 `max_execution_time`
3. 使用本地 LLM (Ollama)

## 最佳实践

### 1. 逐步执行

对于大型目录：
1. 先使用 `suggest` 获取建议
2. 使用 `--dry-run` 模拟执行
3. 分批执行操作

### 2. 明确需求

提供清晰的需求描述：
- ✅ "将所有PDF学术论文按主题分类到不同文件夹"
- ❌ "整理文件"

### 3. 利用对话

使用 `chat` 命令：
- 讨论最佳方案
- 逐步优化需求
- 学习文件管理知识

### 4. 定期备份

虽然支持撤销，但建议：
- 定期创建备份
- 重要操作前手动备份
- 使用版本控制（如 Git）

## 示例场景

### 场景1: 整理学术论文

```bash
# 1. 先获取建议
smart-tidy suggest ~/Downloads/Papers

# 2. 使用 Agent 整理
smart-tidy agent ~/Downloads/Papers \
  --request "将PDF论文按研究领域分类，并用有意义的名称重命名"

# 3. 分析特定文件
smart-tidy analyze ~/Downloads/Papers/paper1.pdf
```

### 场景2: 清理下载文件夹

```bash
smart-tidy agent ~/Downloads \
  --request "清理临时文件、重复文件，按文件类型分类保留有用文件" \
  --dry-run  # 先预览
```

### 场景3: 组织项目文件

```bash
smart-tidy chat  # 进入交互模式

# 然后与 Agent 对话：
> 我想整理我的项目文件夹，包含代码、文档、数据文件，应该如何组织？
> 帮我整理 ~/Projects/MyApp 目录
> 分析 ~/Projects/MyApp/README.md 文件
```

## 扩展开发

### 创建自定义 Tool

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class MyCustomToolInput(BaseModel):
    param: str = Field(..., description="参数描述")

class MyCustomTool(BaseTool):
    name = "my_custom_tool"
    description = "工具描述"
    args_schema = MyCustomToolInput
    
    def _run(self, param: str) -> str:
        # 实现工具逻辑
        return f"Result: {param}"
```

### 添加到 Agent

```python
from src.langchain_integration.agent import FileOrganizerAgent

# 创建 Agent
agent = FileOrganizerAgent(...)

# 添加自定义工具
agent.tools.append(MyCustomTool())
```

## 相关资源

- [LangChain 官方文档](https://python.langchain.com/)
- [Agent 概念介绍](https://python.langchain.com/docs/modules/agents/)
- [自定义 Tools](https://python.langchain.com/docs/modules/agents/tools/)
- [项目 GitHub](https://github.com/your-repo/smart-file-tidy)

## 反馈和贡献

欢迎提交 Issue 和 Pull Request！

- 报告 Bug
- 建议新功能
- 改进文档
- 分享使用案例
