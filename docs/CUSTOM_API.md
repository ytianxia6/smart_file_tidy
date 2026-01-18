# 自定义AI接口使用指南

本工具支持任何兼容OpenAI API格式的第三方服务。

## 支持的服务示例

### 1. Azure OpenAI

**编辑 `.env` 文件：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
CUSTOM_API_KEY=your-azure-api-key
CUSTOM_API_MODEL=gpt-4
```

### 2. 通义千问（阿里云DashScope）

**编辑 `.env` 文件：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CUSTOM_API_KEY=sk-your-dashscope-key
CUSTOM_API_MODEL=qwen-plus
```

获取API Key: https://dashscope.console.aliyun.com/

### 3. 文心一言（百度千帆）

**编辑 `.env` 文件：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat
CUSTOM_API_KEY=your-qianfan-key
CUSTOM_API_MODEL=ernie-bot-4
```

获取API Key: https://console.bce.baidu.com/qianfan/

### 4. 智谱AI（GLM）

**编辑 `.env` 文件：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://open.bigmodel.cn/api/paas/v4
CUSTOM_API_KEY=your-zhipu-key
CUSTOM_API_MODEL=glm-4
```

获取API Key: https://open.bigmodel.cn/

### 5. Moonshot（月之暗面）

**编辑 `.env` 文件：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.moonshot.cn/v1
CUSTOM_API_KEY=sk-your-moonshot-key
CUSTOM_API_MODEL=moonshot-v1-8k
```

获取API Key: https://platform.moonshot.cn/

### 6. DeepSeek

**编辑 `.env` 文件：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
CUSTOM_API_KEY=sk-your-deepseek-key
CUSTOM_API_MODEL=deepseek-chat
```

获取API Key: https://platform.deepseek.com/

### 7. 硅基流动（SiliconFlow）

**编辑 `.env` 文件：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.siliconflow.cn/v1
CUSTOM_API_KEY=your-siliconflow-token
CUSTOM_API_MODEL=Qwen/Qwen2-7B-Instruct
```

获取API Key: https://siliconflow.cn/

### 8. 自部署的模型服务

如果您使用 vLLM、FastChat 或其他提供OpenAI兼容API的服务：

**编辑 `.env` 文件：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=http://localhost:8000/v1
CUSTOM_API_KEY=dummy
CUSTOM_API_MODEL=your-model-name
```

## 配置方法

### 方法1：使用.env文件（推荐）⭐

这是最简单、最安全的配置方式。

**步骤：**

1. 复制模板文件
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，取消注释并填入你的配置

**示例 - 通义千问：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CUSTOM_API_KEY=sk-your-dashscope-key
CUSTOM_API_MODEL=qwen-plus
```

**示例 - DeepSeek：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
CUSTOM_API_KEY=sk-your-deepseek-key
CUSTOM_API_MODEL=deepseek-chat
```

**示例 - Azure OpenAI：**
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
CUSTOM_API_KEY=your-azure-key
CUSTOM_API_MODEL=gpt-4
```

💡 **优势：**
- ✅ 配置集中在一个文件
- ✅ 敏感信息不会泄露（`.env`已在`.gitignore`中）
- ✅ 易于备份和迁移
- ✅ 支持多环境切换

### 方法2：使用命令行配置（快捷方式）

适合快速切换配置：

```bash
smart-tidy config set-provider custom \
  --base-url "https://api.example.com/v1" \
  --api-key "your-api-key" \
  --model "model-name"
```

此命令会自动写入`.env`文件。

### 方法3：直接编辑配置文件（高级）

仅在需要更复杂配置时使用。编辑 `config/default_config.yaml`:

```yaml
ai:
  default_provider: custom
  providers:
    custom:
      base_url: https://api.example.com/v1
      api_key: your-api-key
      model: model-name
      max_tokens: 4096
      temperature: 0.7
```

## 测试配置

配置完成后，测试连接：

```bash
smart-tidy config test --provider custom
```

## 常见问题

### Q1: 如何找到正确的base_url？

A: 查看您的AI服务提供商的API文档，通常是类似 `https://api.example.com/v1` 的格式。确保URL包含 `/v1` 后缀。

### Q2: API Key应该填写什么？

A: 填写您从AI服务提供商获取的API密钥或访问令牌。每个提供商的叫法可能不同（API Key、Access Token、Secret Key等）。

### Q3: 如何知道模型名称？

A: 查看您的AI服务提供商的模型列表文档。不同提供商的模型名称格式不同：
- OpenAI: `gpt-4`, `gpt-3.5-turbo`
- Azure: 您的部署名称
- 通义千问: `qwen-plus`, `qwen-turbo`
- 文心一言: `ernie-bot-4`, `ernie-bot-turbo`

### Q4: 遇到 "API调用失败" 错误怎么办？

A: 检查以下几点：
1. base_url是否正确（包括协议和路径）
2. API Key是否有效
3. 模型名称是否正确
4. 账户是否有足够的余额/配额
5. 网络连接是否正常

### Q5: 如何切换回内置的AI提供商？

```bash
# 切换回Claude
smart-tidy config set-provider claude --api-key your-claude-key

# 切换回OpenAI
smart-tidy config set-provider openai --api-key your-openai-key
```

## 高级配置

### 调整token数量

```yaml
ai:
  providers:
    custom:
      max_tokens: 8192  # 增加到8192
```

### 调整温度参数

```yaml
ai:
  providers:
    custom:
      temperature: 0.5  # 降低温度提高确定性
```

### 添加多个自定义服务

您可以在配置文件中添加多个自定义服务：

```yaml
ai:
  default_provider: custom1
  providers:
    custom1:
      base_url: https://api.service1.com/v1
      api_key: key1
      model: model1
    custom2:
      base_url: https://api.service2.com/v1
      api_key: key2
      model: model2
```

然后使用时指定：

```bash
smart-tidy organize ~/files --request "整理" --provider custom2
```

## 兼容性说明

本工具使用标准的OpenAI API格式，要求第三方服务支持：

- `POST /v1/chat/completions` 端点
- 标准的请求格式（messages、model、max_tokens等参数）
- 标准的响应格式（choices、message、content等字段）

如果您的服务提供商声称兼容OpenAI API，那么应该可以无缝使用。

## 获取帮助

如果在配置自定义API时遇到问题：

1. 查看提供商的API文档
2. 检查错误消息中的具体提示
3. 在项目GitHub提交Issue
4. 参考本文档中的示例配置
