# API 文档

## 核心类

### Controller

主控制器，协调所有模块。

```python
from src.utils import ConfigManager
from src.core import Controller

config = ConfigManager()
controller = Controller(config, ai_provider='claude')
```

#### 方法

##### `scan_directory(directory, recursive=False, extensions=None)`

扫描目录并返回文件列表。

**参数：**
- `directory` (str): 目录路径
- `recursive` (bool): 是否递归扫描
- `extensions` (set): 文件扩展名过滤

**返回：** `List[FileInfo]`

##### `generate_plan(files, user_request)`

生成文件整理方案。

**参数：**
- `files` (List[FileInfo]): 文件列表
- `user_request` (str): 用户需求描述

**返回：** `List[Operation]`

##### `execute_operations(operations, create_backup=True)`

执行文件操作。

**参数：**
- `operations` (List[Operation]): 操作列表
- `create_backup` (bool): 是否创建备份

**返回：** `OperationResult`

---

### FileScanner

文件扫描器。

```python
from src.core import FileScanner

scanner = FileScanner(max_file_size_mb=100, max_depth=5)
files = scanner.scan_directory('/path/to/dir')
```

#### 方法

##### `scan_directory(directory, recursive=False, extensions=None, include_metadata=True, include_content=False)`

扫描目录。

##### `extract_metadata(file_path)`

提取文件元数据。

##### `sample_content(file_path, max_chars=1000)`

读取文件内容样本。

---

### SmartClassifier

智能分类器。

```python
from src.core import SmartClassifier
from src.ai import ClaudeAdapter

ai_adapter = ClaudeAdapter(api_key='your-key')
classifier = SmartClassifier(ai_adapter)

operations = classifier.classify_batch(files, "整理需求", context={})
```

#### 方法

##### `classify_batch(files, user_request, context=None)`

批量分类文件。

##### `refine_with_feedback(previous_operations, feedback, files)`

根据反馈优化分类。

---

## AI适配器

### ClaudeAdapter

```python
from src.ai import ClaudeAdapter

adapter = ClaudeAdapter(
    api_key='your-key',
    model='claude-3-5-sonnet-20241022',
    max_tokens=4096,
    temperature=0.7
)
```

### OpenAIAdapter

```python
from src.ai import OpenAIAdapter

adapter = OpenAIAdapter(
    api_key='your-key',
    model='gpt-4-turbo-preview',
    max_tokens=4096,
    temperature=0.7
)
```

### LocalLLMAdapter

```python
from src.ai import LocalLLMAdapter

adapter = LocalLLMAdapter(
    base_url='http://localhost:11434',
    model='llama3.1',
    timeout=120
)
```

---

## 数据模型

### FileInfo

文件信息模型。

```python
from src.models import FileInfo

file_info = FileInfo.from_path('/path/to/file.txt')
print(file_info.name)
print(file_info.size_human)
print(file_info.extension)
```

**属性：**
- `path` (str): 文件路径
- `name` (str): 文件名
- `extension` (str): 扩展名
- `size` (int): 文件大小（字节）
- `size_human` (str): 人类可读的大小
- `created_time` (datetime): 创建时间
- `modified_time` (datetime): 修改时间
- `metadata` (dict): 元数据
- `content_sample` (str): 内容样本

### Operation

操作模型。

```python
from src.models import Operation, OperationType

op = Operation(
    type=OperationType.MOVE,
    source='/source/file.txt',
    target='/target/file.txt',
    reason='分类原因',
    confidence=0.95
)
```

**属性：**
- `id` (str): 操作ID
- `type` (OperationType): 操作类型（MOVE/RENAME/CREATE_FOLDER）
- `source` (str): 源路径
- `target` (str): 目标路径
- `reason` (str): 操作原因
- `confidence` (float): 置信度（0-1）

### OperationResult

操作结果模型。

```python
from src.models import OperationResult

result = OperationResult(
    total=10,
    success_count=8,
    failed_count=2
)

print(f"成功率: {result.success_rate:.1%}")
```

---

## 安全机制

### OperationLogger

操作日志记录器。

```python
from src.safety import OperationLogger

logger = OperationLogger(log_dir='data/logs')
logger.log_operation(operation, 'success')

recent = logger.get_recent_operations(limit=10)
```

### BackupManager

备份管理器。

```python
from src.safety import BackupManager

backup_mgr = BackupManager(backup_dir='data/backups')
backup_id = backup_mgr.create_backup_point(['/file1.txt', '/file2.txt'])

# 恢复备份
backup_mgr.restore_backup(backup_id)
```

### UndoManager

撤销管理器。

```python
from src.safety import UndoManager

undo_mgr = UndoManager(max_history=10)
undo_mgr.record_operations(operations)

# 撤销最后一次操作
if undo_mgr.can_undo():
    undo_mgr.undo_last()
```

---

## 配置管理

### ConfigManager

```python
from src.utils import ConfigManager

config = ConfigManager()

# 获取配置
provider = config.get('ai.default_provider')
batch_size = config.get('file_operations.batch_size', default=50)

# 设置配置
config.set('ai.default_provider', 'openai')
config.save_config()

# 获取AI配置
ai_config = config.get_ai_config('claude')
```
