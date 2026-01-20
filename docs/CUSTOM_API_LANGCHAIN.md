# 自定义API与LangChain集成指南

本文档详细说明如何使用自定义OpenAI兼容API（如DeepSeek、通义千问、Moonshot等）与LangChain Agent配合使用。

## 快速开始

### 1. 配置环境变量

在项目根目录创建或编辑 `.env` 文件：

```bash
# 设置使用自定义API
DEFAULT_AI_PROVIDER=custom

# 自定义API配置
CUSTOM_API_BASE_URL=https://api.example.com/v1
CUSTOM_API_KEY=sk-your-api-key
CUSTOM_API_MODEL=your-model-name
```

### 2. 验证配置

运行测试脚本验证配置：

```bash
python examples/test_custom_api.py
```

### 3. 使用Agent

```bash
# 使用Agent模式整理文件
smart-tidy agent ./test_files --request "按类型分类"

# 与Agent对话
smart-tidy chat

# 获取整理建议
smart-tidy suggest ./test_files
```

## 常见服务配置示例

### DeepSeek

DeepSeek 提供高性价比的API服务。

**.env 配置**:
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
CUSTOM_API_KEY=sk-your-deepseek-key
CUSTOM_API_MODEL=deepseek-chat
```

**特点**:
- 价格低廉
- 支持中英文
- 响应速度快

### 阿里云通义千问 (DashScope)

**.env 配置**:
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CUSTOM_API_KEY=sk-your-dashscope-key
CUSTOM_API_MODEL=qwen-plus
```

**模型选择**:
- `qwen-turbo` - 轻量快速
- `qwen-plus` - 平衡性能
- `qwen-max` - 最强性能

### Moonshot AI (月之暗面)

**.env 配置**:
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.moonshot.cn/v1
CUSTOM_API_KEY=sk-your-moonshot-key
CUSTOM_API_MODEL=moonshot-v1-8k
```

**模型选择**:
- `moonshot-v1-8k` - 8K上下文
- `moonshot-v1-32k` - 32K上下文
- `moonshot-v1-128k` - 128K上下文

### 智谱AI (GLM)

**.env 配置**:
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://open.bigmodel.cn/api/paas/v4
CUSTOM_API_KEY=your-zhipu-key
CUSTOM_API_MODEL=glm-4
```

**模型选择**:
- `glm-4` - GLM-4标准版
- `glm-4-air` - 轻量版
- `glm-4-flash` - 快速版

### SiliconFlow

提供多种开源模型。

**.env 配置**:
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.siliconflow.cn/v1
CUSTOM_API_KEY=sk-your-siliconflow-key
CUSTOM_API_MODEL=Qwen/Qwen2-7B-Instruct
```

**热门模型**:
- `Qwen/Qwen2-7B-Instruct` - 通义千问
- `deepseek-ai/DeepSeek-V2-Chat` - DeepSeek
- `meta-llama/Meta-Llama-3-8B-Instruct` - Llama 3

### 本地部署 (vLLM/Ollama)

如果您在本地部署了兼容OpenAI API的模型服务：

**.env 配置**:
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=http://localhost:8000/v1
CUSTOM_API_KEY=sk-no-key-required
CUSTOM_API_MODEL=your-local-model
```

## 完整配置示例

### .env 文件示例

```bash
# ============================================
# 智能文件整理助手配置
# ============================================

# AI提供商选择
# 可选值: claude, openai, custom, local
DEFAULT_AI_PROVIDER=custom

# ============================================
# 自定义API配置（使用DeepSeek示例）
# ============================================
CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
CUSTOM_API_KEY=sk-your-deepseek-api-key
CUSTOM_API_MODEL=deepseek-chat

# ============================================
# 可选：其他提供商配置（如需要）
# ============================================

# Claude (如有)
# ANTHROPIC_API_KEY=sk-ant-xxx

# OpenAI (如有)
# OPENAI_API_KEY=sk-xxx

# 本地Ollama (如有)
# LOCAL_LLM_BASE_URL=http://localhost:11434
# LOCAL_LLM_MODEL=llama3.1
```

## 配置验证

### 方法1: 使用测试脚本

```bash
python examples/test_custom_api.py
```

这将测试：
- ✅ API连接是否正常
- ✅ 模型是否可用
- ✅ Agent是否能正常工作

### 方法2: 使用CLI测试

```bash
# 测试对话功能
smart-tidy chat
# 输入: 你好
# 如果收到回复，说明配置成功

# 测试文件分析
smart-tidy suggest ./test_files
```

### 方法3: Python代码测试

```python
from src.utils import ConfigManager
from src.langchain_integration import LLMFactory

# 加载配置
config_manager = ConfigManager()
provider = config_manager.get_default_provider()
ai_config = config_manager.get_ai_config(provider)

# 创建LLM
llm = LLMFactory.create_llm(provider, ai_config)

# 测试连接
response = llm.invoke("你好，请回复'连接成功'")
print(f"LLM响应: {response.content}")
```

## 常见问题

### Q1: 提示 "自定义API地址未配置"

**原因**: 未正确设置环境变量

**解决**:
1. 确认 `.env` 文件在项目根目录
2. 确认文件包含 `CUSTOM_API_BASE_URL`
3. 重启终端或重新加载环境变量

### Q2: 提示 "API密钥未配置"

**原因**: `CUSTOM_API_KEY` 未设置或格式错误

**解决**:
1. 检查 `.env` 文件中的 `CUSTOM_API_KEY`
2. 确认API密钥有效
3. 某些服务不需要密钥，可以设置为任意值：
   ```bash
   CUSTOM_API_KEY=sk-no-key-required
   ```

### Q3: 连接超时或失败

**原因**: 网络问题或API地址错误

**解决**:
1. 检查网络连接
2. 确认API地址正确（包括 `/v1` 后缀）
3. 测试API是否可访问：
   ```bash
   curl -X POST https://api.example.com/v1/chat/completions \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "your-model", "messages": [{"role": "user", "content": "Hello"}]}'
   ```

### Q4: 模型不支持或不可用

**原因**: 模型名称错误或模型未启用

**解决**:
1. 查看API提供商的模型列表
2. 确认模型名称拼写正确
3. 某些服务需要先启用模型

### Q5: Agent执行失败

**原因**: 模型能力不足或配置问题

**解决**:
1. 确认模型支持 Function Calling（工具调用）
2. 尝试使用更强大的模型
3. 检查 `config/default_config.yaml` 中的 LangChain 配置

## 性能优化

### 1. 选择合适的模型

不同任务建议使用不同级别的模型：

**简单任务**（文件扫描、基本分类）:
- DeepSeek Chat
- Qwen-Turbo
- Moonshot-v1-8k

**复杂任务**（内容深度分析、智能决策）:
- Qwen-Max
- Moonshot-v1-32k
- GLM-4

### 2. 调整配置参数

编辑 `config/default_config.yaml`:

```yaml
langchain:
  agent:
    verbose: false  # 关闭详细日志，提升速度
    max_iterations: 10  # 减少迭代次数
    max_execution_time: 180  # 缩短超时时间
  
  tools:
    file_scanner:
      max_files: 500  # 减少单次扫描文件数
    
    file_analyzer:
      max_content_size: 1000  # 减少内容分析长度
```

### 3. 使用干运行模式

在正式执行前先测试：

```bash
smart-tidy agent ./large_directory --request "整理文件" --dry-run
```

## 高级配置

### 自定义温度和Token限制

在 `config/default_config.yaml` 中：

```yaml
ai:
  providers:
    custom:
      base_url: https://api.example.com/v1
      model: your-model
      api_key: your-key
      max_tokens: 4096
      temperature: 0.7  # 0.0-1.0，越低越确定
```

通过环境变量也可以：

```bash
# 在 .env 中（需要修改代码支持）
CUSTOM_API_MAX_TOKENS=8192
CUSTOM_API_TEMPERATURE=0.5
```

### 多个自定义API切换

如果您有多个API服务，可以通过修改 `.env` 快速切换：

```bash
# 方案1: DeepSeek
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
CUSTOM_API_KEY=sk-deepseek-key
CUSTOM_API_MODEL=deepseek-chat

# 方案2: 通义千问（注释掉上面的，启用下面的）
# DEFAULT_AI_PROVIDER=custom
# CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# CUSTOM_API_KEY=sk-qwen-key
# CUSTOM_API_MODEL=qwen-plus
```

## 成本估算

使用自定义API的成本参考（2026年1月）：

| 服务商 | 模型 | 输入价格 | 输出价格 | 适用场景 |
|--------|------|---------|---------|----------|
| DeepSeek | deepseek-chat | ¥1/M tokens | ¥2/M tokens | 高性价比 |
| 通义千问 | qwen-plus | ¥4/M tokens | ¥12/M tokens | 平衡性能 |
| Moonshot | moonshot-v1-8k | ¥12/M tokens | ¥12/M tokens | 长文本 |
| 智谱AI | glm-4 | ¥10/M tokens | ¥10/M tokens | 中文优化 |

**估算示例**：
- 整理100个文件，每个文件分析约2000 tokens
- 总输入：约200K tokens
- 总输出：约50K tokens
- 使用DeepSeek：约 ¥0.20-0.30

## 最佳实践

### 1. 安全存储API密钥

- ✅ 使用 `.env` 文件，并添加到 `.gitignore`
- ✅ 不要在代码中硬编码密钥
- ✅ 定期轮换API密钥
- ❌ 不要将密钥提交到Git仓库

### 2. 监控API使用

- 定期检查API使用量
- 设置API配额限制
- 关注成本变化

### 3. 错误处理

```python
from src.langchain_integration import FileOrganizerAgent

try:
    agent = FileOrganizerAgent(
        llm_provider='custom',
        config=config,
        dry_run=True,
        verbose=False
    )
    result = agent.organize_files(directory, request)
except ValueError as e:
    print(f"配置错误: {e}")
    print("请检查 .env 文件中的配置")
except Exception as e:
    print(f"执行错误: {e}")
```

### 4. 批量处理

对于大量文件，分批处理：

```bash
# 先获取建议
smart-tidy suggest ./large_directory

# 分批执行
smart-tidy agent ./large_directory/batch1 --request "整理"
smart-tidy agent ./large_directory/batch2 --request "整理"
```

## 故障排查清单

遇到问题时，按以下顺序检查：

- [ ] `.env` 文件是否存在于项目根目录
- [ ] `DEFAULT_AI_PROVIDER=custom` 是否设置
- [ ] `CUSTOM_API_BASE_URL` 是否正确（包括协议和路径）
- [ ] `CUSTOM_API_KEY` 是否有效
- [ ] `CUSTOM_API_MODEL` 名称是否正确
- [ ] 网络是否能访问API地址
- [ ] API密钥是否有足够余额
- [ ] 模型是否支持 Function Calling
- [ ] LangChain依赖是否已安装

## 获取帮助

如果您遇到问题：

1. **查看日志**: 使用 `--verbose` 参数查看详细日志
2. **测试API**: 使用 `curl` 或 Postman 测试API连接
3. **查看文档**: 阅读API提供商的官方文档
4. **提交Issue**: 在GitHub仓库提交问题

## 相关资源

- [配置指南](CONFIGURATION.md)
- [LangChain集成](LANGCHAIN_INTEGRATION.md)
- [自定义API配置](CUSTOM_API.md)
- [快速开始](../QUICKSTART.md)
