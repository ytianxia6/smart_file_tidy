# 项目结构说明

## 完整目录树

```
smart_file_tidy/
├── src/                          # 源代码
│   ├── __init__.py
│   ├── models/                   # 数据模型
│   │   ├── __init__.py
│   │   ├── file_info.py         # 文件信息模型
│   │   └── operation.py         # 操作记录模型
│   ├── utils/                    # 工具函数
│   │   ├── __init__.py
│   │   ├── config.py            # 配置管理
│   │   ├── file_metadata.py     # 文件元数据提取
│   │   └── pdf_reader.py        # PDF内容读取
│   ├── core/                     # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── file_scanner.py      # 文件扫描器
│   │   ├── file_operator.py     # 文件操作器
│   │   ├── classifier.py        # 智能分类器
│   │   └── controller.py        # 主控制器
│   ├── ai/                       # AI集成层
│   │   ├── __init__.py
│   │   ├── base_adapter.py      # AI适配器基类
│   │   ├── claude_adapter.py    # Claude适配器
│   │   ├── openai_adapter.py    # OpenAI适配器
│   │   ├── local_adapter.py     # 本地模型适配器
│   │   ├── prompt_builder.py    # Prompt构建器
│   │   └── adapter_factory.py   # 适配器工厂
│   ├── safety/                   # 安全机制
│   │   ├── __init__.py
│   │   ├── operation_log.py     # 操作日志
│   │   ├── backup.py            # 备份管理
│   │   └── undo_manager.py      # 撤销管理
│   └── cli/                      # CLI界面
│       ├── __init__.py
│       ├── main.py              # 主入口
│       ├── commands.py          # 命令实现
│       └── config_commands.py   # 配置命令
├── tests/                        # 测试文件
│   ├── __init__.py
│   ├── conftest.py              # Pytest配置
│   ├── test_models.py           # 模型测试
│   ├── test_file_scanner.py     # 文件扫描器测试
│   ├── test_file_operator.py    # 文件操作器测试
│   ├── test_classifier.py       # 分类器测试
│   ├── test_safety.py           # 安全机制测试
│   └── test_integration.py      # 集成测试
├── config/                       # 配置文件
│   └── default_config.yaml      # 默认配置
├── data/                         # 数据存储（gitignore）
│   ├── logs/                    # 操作日志
│   └── backups/                 # 备份数据
├── docs/                         # 文档
│   ├── API.md                   # API文档
│   └── USAGE.md                 # 使用指南
├── examples/                     # 示例代码
│   ├── basic_usage.py           # 基本使用
│   └── custom_classifier.py     # 自定义分类器
├── .github/                      # GitHub配置
│   └── workflows/
│       └── test.yml             # CI/CD配置
├── requirements.txt              # 依赖列表
├── setup.py                      # 安装配置
├── pytest.ini                    # Pytest配置
├── .gitignore                    # Git忽略文件
├── LICENSE                       # MIT许可证
├── README.md                     # 项目说明
├── CHANGELOG.md                  # 更新日志
├── CONTRIBUTING.md               # 贡献指南
└── PROJECT_STRUCTURE.md          # 本文件
```

## 模块说明

### 1. 数据模型层 (src/models/)

定义核心数据结构：
- `FileInfo`: 文件信息（路径、大小、元数据等）
- `Operation`: 文件操作（移动、重命名等）
- `OperationResult`: 批量操作结果

### 2. 工具层 (src/utils/)

提供通用工具函数：
- `ConfigManager`: 配置管理（YAML、环境变量）
- `FileMetadataExtractor`: 提取PDF、图片等文件的元数据
- `PDFReader`: 读取PDF内容和分析文件名模式

### 3. 核心业务层 (src/core/)

实现主要业务逻辑：
- `FileScanner`: 扫描目录、收集文件信息、提取元数据
- `FileOperator`: 执行文件操作（移动、重命名、创建文件夹）
- `SmartClassifier`: 智能分类、规则学习、反馈优化
- `Controller`: 主控制器，协调各模块

### 4. AI集成层 (src/ai/)

AI提供商适配：
- `BaseAIAdapter`: 适配器基类，定义统一接口
- `ClaudeAdapter`: Anthropic Claude适配器
- `OpenAIAdapter`: OpenAI GPT适配器
- `LocalLLMAdapter`: 本地模型（Ollama）适配器
- `PromptBuilder`: 构建AI提示词
- `AIAdapterFactory`: 适配器工厂

### 5. 安全机制层 (src/safety/)

确保操作安全：
- `OperationLogger`: 记录所有操作到JSONL日志
- `BackupManager`: 创建备份点、恢复备份
- `UndoManager`: 撤销最近的操作

### 6. CLI界面层 (src/cli/)

命令行交互：
- `main.py`: Typer应用入口、命令定义
- `commands.py`: 实现organize、interactive、undo、history命令
- `config_commands.py`: 配置管理命令

## 数据流

```
用户输入
  ↓
CLI层 (main.py, commands.py)
  ↓
Controller (协调各模块)
  ↓
├─→ FileScanner (扫描文件)
│     ↓
│   FileInfo列表
│     ↓
├─→ SmartClassifier (分类)
│     ├─→ AI Adapter (调用AI)
│     │     ↓
│     │   分类方案
│     ↓
│   Operation列表
│     ↓
├─→ FileOperator (执行操作)
│     ├─→ BackupManager (备份)
│     ├─→ OperationLogger (日志)
│     └─→ UndoManager (撤销记录)
│     ↓
│   OperationResult
│     ↓
└─→ 返回结果给用户
```

## 配置文件

### config/default_config.yaml

配置项包括：
- AI提供商设置（模型、token数、温度等）
- 文件操作参数（批次大小、文件大小限制、扫描深度）
- 安全配置（备份、确认、历史记录数）
- 日志配置（级别、保留天数）

### .env (用户创建)

敏感信息：
- `ANTHROPIC_API_KEY`: Claude API密钥
- `OPENAI_API_KEY`: OpenAI API密钥
- `LOCAL_LLM_BASE_URL`: 本地模型地址
- `DEFAULT_AI_PROVIDER`: 默认提供商

## 数据存储

### data/logs/

JSONL格式的操作日志：
- 文件名: `YYYY-MM-DD.jsonl`
- 每行一个JSON对象
- 记录：时间戳、操作类型、源路径、目标路径、状态、错误信息

### data/backups/

备份点目录：
- 目录名: `YYYYMMDD_HHMMSS`
- 内容: `manifest.json`（文件元信息和哈希值）
- 不复制实际文件，节省空间

## 测试

### 单元测试

- `test_models.py`: 数据模型测试
- `test_file_scanner.py`: 文件扫描功能测试
- `test_file_operator.py`: 文件操作功能测试
- `test_classifier.py`: 分类逻辑测试
- `test_safety.py`: 安全机制测试

### 集成测试

- `test_integration.py`: 端到端工作流测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_file_scanner.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 代码质量

- **类型提示**: 所有函数都有完整的类型注解
- **文档字符串**: 所有公共方法都有docstring
- **错误处理**: 完善的异常处理和用户友好的错误消息
- **日志记录**: 关键操作都有日志记录
- **测试覆盖**: 核心功能都有测试覆盖

## 扩展指南

### 添加新的AI提供商

1. 继承 `BaseAIAdapter`
2. 实现 `generate_classification` 和 `refine_with_feedback`
3. 在 `AIAdapterFactory` 中注册

### 添加新的文件类型支持

1. 在 `FileMetadataExtractor` 中添加提取方法
2. 在 `FileScanner` 中调用新的提取方法

### 添加自定义分类规则

1. 继承 `SmartClassifier`
2. 重写 `_apply_rules` 方法
3. 在 `Controller` 中使用自定义分类器

## 性能考虑

- **并发扫描**: 使用 `ThreadPoolExecutor` 并行提取元数据
- **分批处理**: 大量文件分批操作，避免内存溢出
- **缓存机制**: 可扩展添加文件hash和元数据缓存
- **增量扫描**: 可扩展记录上次扫描时间，仅处理新增/修改文件

## 安全考虑

- **操作前预览**: 显示操作列表供用户确认
- **自动备份**: 操作前记录文件状态
- **撤销功能**: 可回退最近的操作
- **日志审计**: 所有操作都有详细日志
- **冲突处理**: 自动处理文件名冲突，不覆盖已存在文件
