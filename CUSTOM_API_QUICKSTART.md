# 自定义API快速开始指南

> 如果您没有 Claude 或 OpenAI 的 API 密钥，可以使用国内的AI服务（如 DeepSeek、通义千问等）。

## 🚀 3步快速配置

### 步骤1: 复制配置模板

```bash
# Windows
copy env.custom.example .env

# Linux/Mac
cp env.custom.example .env
```

### 步骤2: 编辑配置

打开 `.env` 文件，选择一个服务并填写您的API信息：

**推荐：DeepSeek（高性价比）**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
CUSTOM_API_KEY=sk-your-deepseek-key
CUSTOM_API_MODEL=deepseek-chat
```

**或者：通义千问**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CUSTOM_API_KEY=sk-your-qwen-key
CUSTOM_API_MODEL=qwen-plus
```

> 💡 更多服务配置请查看 `env.custom.example` 文件中的注释

### 步骤3: 验证配置

```bash
python examples/test_custom_api.py
```

如果看到 "🎉 所有测试通过！"，说明配置成功！

## 🎯 开始使用

### Agent模式（推荐）

```bash
# 智能整理文件
smart-tidy agent ./test_files --request "按文件类型分类"

# 获取整理建议
smart-tidy suggest ./test_files

# 与AI助手对话
smart-tidy chat
```

### 传统模式

```bash
# 交互式整理
smart-tidy interactive ./test_files

# 单次整理
smart-tidy organize ./test_files --request "整理PDF文件"
```

## 📚 获取API密钥

### DeepSeek
1. 访问 https://platform.deepseek.com/
2. 注册并登录
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制密钥到 `.env` 文件

### 通义千问
1. 访问 https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 开通 DashScope 服务
4. 创建API密钥
5. 复制密钥到 `.env` 文件

### Moonshot AI
1. 访问 https://platform.moonshot.cn/
2. 注册并登录
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制密钥到 `.env` 文件

## ❓ 常见问题

### Q: 提示"自定义API地址未配置"
**A**: 检查 `.env` 文件是否在项目根目录，并确认包含 `CUSTOM_API_BASE_URL`

### Q: 提示"API密钥未配置"
**A**: 确认 `.env` 文件中的 `CUSTOM_API_KEY` 已正确填写

### Q: 连接超时
**A**: 
1. 检查网络连接
2. 确认API地址正确（包括 `/v1` 后缀）
3. 尝试使用其他服务

### Q: 测试失败
**A**: 运行详细测试查看具体错误：
```bash
python examples/test_custom_api.py
```

## 📖 详细文档

- [自定义API与LangChain集成指南](docs/CUSTOM_API_LANGCHAIN.md) - 完整配置说明
- [LangChain集成文档](docs/LANGCHAIN_INTEGRATION.md) - Agent使用指南
- [配置文档](docs/CONFIGURATION.md) - 所有配置选项

## 💡 提示

- 使用 `--dry-run` 参数先预览操作，不实际执行
- DeepSeek 价格最低，适合测试和日常使用
- 通义千问支持更长的上下文，适合处理大文件
- 所有配置都在 `.env` 文件中，方便管理

## 🎉 开始整理您的文件吧！

配置完成后，就可以使用AI助手智能整理文件了：

```bash
smart-tidy agent ~/Downloads --request "帮我整理下载文件夹"
```
