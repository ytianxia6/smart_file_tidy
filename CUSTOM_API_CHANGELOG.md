# 自定义API功能更新日志

## [0.2.0] - 2026-01-18

### 新增功能

#### 🌐 自定义AI接口支持

添加了对任何兼容OpenAI API格式的第三方服务的支持！

**核心特性：**

1. **新增 CustomAPIAdapter**
   - 位置：`src/ai/custom_adapter.py`
   - 支持自定义API地址、密钥和模型名称
   - 完全兼容OpenAI API格式

2. **配置方式**
   ```bash
   # CLI命令配置
   smart-tidy config set-provider custom \
     --base-url "https://api.example.com/v1" \
     --api-key "your-api-key" \
     --model "model-name"
   ```

3. **支持的服务**
   - ✅ Azure OpenAI
   - ✅ 通义千问（阿里云DashScope）
   - ✅ 文心一言（百度千帆）
   - ✅ 智谱AI（GLM）
   - ✅ Moonshot（月之暗面）
   - ✅ DeepSeek
   - ✅ 硅基流动（SiliconFlow）
   - ✅ 自部署模型（vLLM、FastChat等）

4. **新增文档**
   - `docs/CUSTOM_API.md` - 详细配置指南
   - 包含8种常见服务的配置示例
   - 常见问题解答

5. **新增示例**
   - `examples/custom_api_example.py` - 使用示例
   - 包含4种不同服务的代码示例

6. **测试覆盖**
   - `tests/test_custom_adapter.py` - 单元测试
   - 参数验证测试
   - JSON解析测试

### 修改的文件

1. **配置文件**
   - `config/default_config.yaml` - 添加custom提供商配置

2. **AI集成层**
   - `src/ai/__init__.py` - 导出CustomAPIAdapter
   - `src/ai/adapter_factory.py` - 添加custom适配器工厂方法

3. **CLI命令**
   - `src/cli/config_commands.py` - 支持custom提供商配置
   - 添加 `--base-url` 参数

4. **文档更新**
   - `README.md` - 添加自定义API说明
   - `QUICKSTART.md` - 添加方案D配置步骤

### 使用示例

#### 快速开始

```bash
# 1. 配置自定义API
smart-tidy config set-provider custom \
  --base-url "https://api.example.com/v1" \
  --api-key "your-key" \
  --model "your-model"

# 2. 测试连接
smart-tidy config test --provider custom

# 3. 开始使用
smart-tidy interactive ~/Downloads
```

#### 通义千问示例

```bash
smart-tidy config set-provider custom \
  --base-url "https://dashscope.aliyuncs.com/compatible-mode/v1" \
  --api-key "sk-xxx" \
  --model "qwen-plus"
```

#### DeepSeek示例

```bash
smart-tidy config set-provider custom \
  --base-url "https://api.deepseek.com/v1" \
  --api-key "sk-xxx" \
  --model "deepseek-chat"
```

### 技术细节

**实现原理：**

CustomAPIAdapter 通过配置自定义的 `base_url`，使用 OpenAI SDK 连接到任何兼容的API端点。只要服务提供商实现了标准的 `/v1/chat/completions` 接口，就可以无缝使用。

**兼容性要求：**

- 支持 `POST /v1/chat/completions` 端点
- 支持标准的请求参数（messages、model、max_tokens等）
- 返回标准的响应格式（choices、message、content等）

### 优势

1. **灵活性** - 不限于特定的AI服务商
2. **成本优化** - 可以选择性价比最高的服务
3. **隐私保护** - 支持使用自部署的模型
4. **国内友好** - 支持国内主流AI服务
5. **易于扩展** - 新服务只需配置，无需修改代码

### 向后兼容

- ✅ 完全兼容现有的claude、openai、local提供商
- ✅ 不影响现有配置和使用方式
- ✅ 仅增加新功能，无破坏性变更

### 下一步计划

- [ ] 添加更多预设配置模板
- [ ] 支持批量测试多个API配置
- [ ] 添加API响应时间统计
- [ ] 支持配置多个custom实例

---

**发布说明：**

此更新大幅提升了工具的灵活性和适用范围，现在可以使用几乎所有市面上的AI服务！

查看详细文档：[docs/CUSTOM_API.md](docs/CUSTOM_API.md)
