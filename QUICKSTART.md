# 快速开始

5分钟快速上手 Smart File Tidy！

## 1. 安装 (1分钟)

```bash
# 克隆仓库
git clone https://github.com/yourusername/smart-file-tidy.git
cd smart-file-tidy

# 安装依赖
pip install -r requirements.txt

# 安装工具
pip install -e .
```

## 2. 配置 (2分钟)

### 第一步：创建配置文件

```bash
# 复制环境变量模板
cp .env.example .env
```

### 第二步：选择AI提供商并编辑.env

用文本编辑器打开 `.env` 文件，选择以下方案之一：

#### 方案A: 使用Claude (推荐)

```bash
# 编辑 .env 文件
DEFAULT_AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

获取API Key: https://console.anthropic.com/

#### 方案B: 使用OpenAI

```bash
# 编辑 .env 文件
DEFAULT_AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
```

获取API Key: https://platform.openai.com/api-keys

#### 方案C: 使用本地模型（完全免费）

```bash
# 1. 安装并启动Ollama (访问 https://ollama.ai)
ollama pull llama3.1
ollama serve

# 2. 编辑 .env 文件
DEFAULT_AI_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3.1
```

#### 方案D: 使用自定义API（第三方服务）

支持任何兼容OpenAI API的服务。以下是常见服务的配置：

**通义千问 (阿里云DashScope)**
```bash
# 编辑 .env 文件
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CUSTOM_API_KEY=sk-your-dashscope-key
CUSTOM_API_MODEL=qwen-plus
```

**DeepSeek**
```bash
# 编辑 .env 文件
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
CUSTOM_API_KEY=sk-your-deepseek-key
CUSTOM_API_MODEL=deepseek-chat
```

**Moonshot (月之暗面)**
```bash
# 编辑 .env 文件
DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.moonshot.cn/v1
CUSTOM_API_KEY=sk-your-moonshot-key
CUSTOM_API_MODEL=moonshot-v1-8k
```

💡 **提示**: `.env.example` 文件中包含了更多服务的配置示例（智谱AI、文心一言、硅基流动等），直接取消注释并填入你的API Key即可！

查看[自定义API详细指南](docs/CUSTOM_API.md)了解所有支持的服务。

### 第三步：测试连接

```bash
smart-tidy config test
```

看到 "✓ 连接成功" 即可！

## 3. 第一次使用 (2分钟)

### 创建测试环境

```bash
# 创建测试目录和文件
mkdir test_files
cd test_files

# 创建一些测试文件
echo "Test content" > document.txt
echo "Report 2023" > report_2023.pdf
echo "Invoice" > invoice_2024.pdf
echo "Photo" > photo.jpg
```

### 运行交互式整理

```bash
smart-tidy interactive ./test_files
```

### 示例对话

```
✓ 发现 4 个文件

请描述您的整理需求: 把PDF文件移动到documents文件夹

AI正在分析...

操作预览：
序号  操作   文件                   目标
1    move   report_2023.pdf       documents/report_2023.pdf
2    move   invoice_2024.pdf      documents/invoice_2024.pdf

是否执行以上操作？[y/N]: y

✓ 完成！移动了 2 个文件
```

## 常用命令速查

```bash
# 单次整理
smart-tidy organize ~/Downloads --request "整理所有图片"

# 交互式整理（推荐）
smart-tidy interactive ~/Documents

# 递归扫描子目录
smart-tidy organize ~/Files --recursive --request "按类型分类"

# 预览模式（不实际执行）
smart-tidy organize ~/Test --dry-run --request "整理文件"

# 查看历史
smart-tidy history

# 撤销操作
smart-tidy undo

# 查看配置
smart-tidy config show

# 帮助
smart-tidy --help
```

## 实用场景

### 场景1：整理下载文件夹

```bash
smart-tidy interactive ~/Downloads
> 把所有PDF文档移动到Documents，图片移动到Pictures
```

### 场景2：清理桌面

```bash
smart-tidy interactive ~/Desktop
> 按文件类型整理，创建对应的文件夹
```

### 场景3：整理工作文档

```bash
smart-tidy interactive ~/Work
> 把2023年的文档移动到Archive/2023，当前年度的保留
```

### 场景4：分类照片

```bash
smart-tidy organize ~/Photos --recursive --request "按年份和月份整理"
```

## 最佳实践

1. **先预览后执行**
   ```bash
   smart-tidy organize ~/folder --dry-run --request "需求"
   ```

2. **使用交互式模式**
   - 可以查看结果
   - 提供反馈优化
   - 更安全可控

3. **重要文件先备份**
   - 工具有自动备份
   - 但重要文件建议额外备份

4. **分批次整理**
   - 大量文件分多次整理
   - 每次聚焦一个目标

5. **利用反馈学习**
   ```
   > 整理PDF
   （查看结果）
   > 数字文件名的不是论文，请分开
   （AI学习并优化）
   ```

## 故障排除

### 问题1：无法连接AI服务

```bash
# 检查API Key
smart-tidy config show

# 测试连接
smart-tidy config test

# 查看详细错误
smart-tidy organize ~/test --request "test" --dry-run
```

### 问题2：文件没有移动

- 检查是否使用了 `--dry-run` 参数
- 查看操作历史：`smart-tidy history`
- 检查文件权限

### 问题3：分类不准确

- 提供更详细的需求描述
- 使用交互式模式并提供反馈
- 考虑使用不同的AI模型

## 下一步

- 阅读[完整使用指南](docs/USAGE.md)
- 查看[API文档](docs/API.md)
- 浏览[示例代码](examples/)
- 参与[贡献](CONTRIBUTING.md)

## 获取帮助

- 提交Issue: https://github.com/yourusername/smart-file-tidy/issues
- 查看文档: [docs/](docs/)
- 运行 `smart-tidy --help`

祝您使用愉快！ 🎉
