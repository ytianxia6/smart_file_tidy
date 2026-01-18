# 配置指南

本文档详细说明 Smart File Tidy 的所有配置方式。

## 配置优先级

配置按以下优先级生效（从高到低）：

1. **环境变量** (`.env` 文件)
2. **配置文件** (`config/default_config.yaml`)
3. **默认值** (代码中定义)

💡 **推荐使用 `.env` 文件进行配置**，因为：
- 敏感信息（API Key）不会被提交到版本控制
- 配置集中，易于管理
- 支持多环境切换

---

## 方式1: 使用 .env 文件（推荐）⭐

### 第一步：创建配置文件

```bash
cp .env.example .env
```

### 第二步：编辑配置

用任何文本编辑器打开 `.env` 文件：

```bash
# Windows
notepad .env

# macOS/Linux
nano .env
# 或
vim .env
```

### 第三步：选择AI提供商

#### Claude
```bash
DEFAULT_AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

#### OpenAI
```bash
DEFAULT_AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

#### 本地模型
```bash
DEFAULT_AI_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3.1
```

#### 自定义API
```bash
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.example.com/v1
CUSTOM_API_KEY=your-key
CUSTOM_API_MODEL=model-name
```

### .env 完整示例

```bash
# AI提供商选择
DEFAULT_AI_PROVIDER=claude

# Claude
ANTHROPIC_API_KEY=sk-ant-xxx

# OpenAI (如需使用，取消注释)
# OPENAI_API_KEY=sk-xxx

# 本地模型 (如需使用，取消注释)
# LOCAL_LLM_BASE_URL=http://localhost:11434
# LOCAL_LLM_MODEL=llama3.1

# 自定义API - 通义千问示例 (如需使用，取消注释)
# CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# CUSTOM_API_KEY=sk-xxx
# CUSTOM_API_MODEL=qwen-plus

# 高级配置 (可选)
# BATCH_SIZE=50
# MAX_FILE_SIZE_MB=100
# SCAN_MAX_DEPTH=5
```

---

## 方式2: 使用CLI命令（快捷方式）

CLI命令提供快速配置，实际上是帮你写入 `.env` 文件。

### Claude
```bash
smart-tidy config set-provider claude --api-key sk-ant-xxx
```

### OpenAI
```bash
smart-tidy config set-provider openai --api-key sk-xxx
```

### 本地模型
```bash
smart-tidy config set-provider local \
  --base-url http://localhost:11434 \
  --model llama3.1
```

### 自定义API
```bash
smart-tidy config set-provider custom \
  --base-url https://api.example.com/v1 \
  --api-key your-key \
  --model model-name
```

---

## 方式3: 编辑配置文件（高级）

适用于需要精细控制的场景。

编辑 `config/default_config.yaml`:

```yaml
ai:
  default_provider: claude
  providers:
    claude:
      model: claude-3-5-sonnet-20241022
      max_tokens: 4096
      temperature: 0.7
    custom:
      base_url: https://api.example.com/v1
      api_key: your-key  # 不推荐直接写在这里
      model: model-name
      max_tokens: 4096
      temperature: 0.7
```

⚠️ **注意**：不建议在配置文件中直接写入 API Key，应使用环境变量。

---

## 环境变量参考

### AI提供商选择
| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DEFAULT_AI_PROVIDER` | 默认提供商 | `claude`, `openai`, `local`, `custom` |

### Claude
| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ANTHROPIC_API_KEY` | Claude API密钥 | `sk-ant-xxx` |

### OpenAI
| 变量名 | 说明 | 示例 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | `sk-xxx` |

### 本地模型
| 变量名 | 说明 | 示例 |
|--------|------|------|
| `LOCAL_LLM_BASE_URL` | Ollama服务地址 | `http://localhost:11434` |
| `LOCAL_LLM_MODEL` | 模型名称 | `llama3.1`, `qwen2` |

### 自定义API
| 变量名 | 说明 | 示例 |
|--------|------|------|
| `CUSTOM_API_BASE_URL` | API基础地址 | `https://api.example.com/v1` |
| `CUSTOM_API_KEY` | API密钥 | `sk-xxx` |
| `CUSTOM_API_MODEL` | 模型名称 | `qwen-plus`, `deepseek-chat` |

### 高级配置（可选）
| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `BATCH_SIZE` | 批处理大小 | `50` |
| `MAX_FILE_SIZE_MB` | 最大文件大小(MB) | `100` |
| `SCAN_MAX_DEPTH` | 最大扫描深度 | `5` |

---

## 多环境管理

### 场景1：开发和生产环境

创建不同的环境文件：

```bash
.env.development  # 开发环境
.env.production   # 生产环境
```

使用时指定：
```bash
# 开发环境
cp .env.development .env

# 生产环境
cp .env.production .env
```

### 场景2：多个API提供商

在 `.env` 中配置所有提供商，通过 `DEFAULT_AI_PROVIDER` 切换：

```bash
# 配置所有提供商
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx
CUSTOM_API_BASE_URL=https://api.example.com/v1
CUSTOM_API_KEY=sk-xxx
CUSTOM_API_MODEL=model-name

# 选择当前使用的提供商
DEFAULT_AI_PROVIDER=claude  # 改为 openai 或 custom 即可切换
```

---

## 验证配置

### 查看当前配置
```bash
smart-tidy config show
```

### 测试连接
```bash
smart-tidy config test
```

### 测试指定提供商
```bash
smart-tidy config test --provider custom
```

---

## 安全建议

### 1. 保护 .env 文件

确保 `.env` 在 `.gitignore` 中：
```
.env
.env.*
!.env.example
```

### 2. 不要提交敏感信息

❌ **不要做：**
- 将 `.env` 提交到 Git
- 在配置文件中硬编码 API Key
- 在代码中直接写入密钥

✅ **应该做：**
- 使用 `.env` 文件
- 使用 `.env.example` 作为模板
- 定期轮换 API Key

### 3. 权限管理

```bash
# Linux/macOS: 限制 .env 文件权限
chmod 600 .env
```

---

## 故障排除

### 问题1：找不到API Key

**症状**：
```
错误: Claude API Key未配置
```

**解决**：
1. 检查 `.env` 文件是否存在
2. 确认变量名正确（如 `ANTHROPIC_API_KEY`）
3. 确认没有多余的空格或引号
4. 重新加载配置：`smart-tidy config test`

### 问题2：配置不生效

**可能原因**：
1. `.env` 文件位置不对（应在项目根目录）
2. 环境变量格式错误
3. 缓存问题

**解决**：
```bash
# 检查配置
smart-tidy config show

# 重新设置
smart-tidy config set-provider claude --api-key sk-xxx

# 测试
smart-tidy config test
```

### 问题3：自定义API连接失败

**检查清单**：
- [ ] `CUSTOM_API_BASE_URL` 格式正确（包含 `/v1` 后缀）
- [ ] `CUSTOM_API_KEY` 有效
- [ ] `CUSTOM_API_MODEL` 名称正确
- [ ] 网络连接正常
- [ ] API服务可访问

---

## 更多帮助

- [快速开始](../QUICKSTART.md)
- [自定义API指南](CUSTOM_API.md)
- [API文档](API.md)
- [GitHub Issues](https://github.com/yourusername/smart-file-tidy/issues)
