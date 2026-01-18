# 使用指南

## 安装

### 从源码安装

```bash
git clone https://github.com/yourusername/smart-file-tidy.git
cd smart-file-tidy
pip install -r requirements.txt
pip install -e .
```

### 使用pip安装（发布后）

```bash
pip install smart-file-tidy
```

## 配置

### 1. 配置AI提供商

#### 使用Claude

```bash
# 设置API Key
export ANTHROPIC_API_KEY="your-api-key"

# 或使用命令配置
smart-tidy config set-provider claude --api-key your-api-key
```

#### 使用OpenAI

```bash
export OPENAI_API_KEY="your-api-key"
smart-tidy config set-provider openai --api-key your-api-key
```

#### 使用本地模型（Ollama）

```bash
# 先启动Ollama服务
ollama serve

# 配置使用本地模型
smart-tidy config set-provider local
```

### 2. 测试连接

```bash
smart-tidy config test
```

## 基本使用

### 单次整理

```bash
# 基本用法
smart-tidy organize /path/to/directory --request "整理所有PDF文件"

# 递归扫描子目录
smart-tidy organize ~/Downloads --request "整理文档" --recursive

# 仅预览不执行
smart-tidy organize ~/Documents --request "分类图片" --dry-run

# 指定AI提供商
smart-tidy organize ~/Files --request "整理" --provider openai
```

### 交互式模式（推荐）

```bash
smart-tidy interactive ~/Downloads
```

交互式模式允许：
- 查看AI生成的方案
- 提供反馈进行迭代优化
- 逐步完成整理任务

#### 交互流程示例

```
$ smart-tidy interactive ~/Downloads

扫描目录: ~/Downloads
✓ 发现 150 个文件

请描述您的整理需求: 把所有PDF论文移动到论文文件夹

AI正在分析...

操作预览：
序号  操作    文件                          目标
1     move   research_paper_2023.pdf      ~/Documents/论文/...
2     move   machine_learning.pdf         ~/Documents/论文/...
...

是否执行以上操作？[y/N/edit]: y

✓ 完成！移动了 82 个文件

操作结果满意吗？有需要调整的吗？: 其中有些不是论文，数字文件名的PDF应该分开

AI正在重新分类...

操作预览：
序号  操作    文件              目标
1     move   12345.pdf        ~/Documents/其他文档/...
2     move   98765.pdf        ~/Documents/其他文档/...
...

是否执行以上操作？[y/N]: y

✓ 完成！处理了 15 个文件
```

## 高级功能

### 查看操作历史

```bash
smart-tidy history

# 显示最近20条
smart-tidy history --limit 20
```

### 撤销操作

```bash
# 撤销最后一次操作
smart-tidy undo

# 跳过确认直接撤销
smart-tidy undo --yes
```

### 查看配置

```bash
smart-tidy config show
```

## 使用场景

### 场景1：整理下载文件夹

```bash
smart-tidy interactive ~/Downloads
> 把图片都移动到Pictures文件夹，PDF文档移动到Documents
```

### 场景2：按类型整理文档

```bash
smart-tidy organize ~/Documents --request "按文件类型分类：论文、报告、书籍"
```

### 场景3：清理旧文件

```bash
smart-tidy organize ~/OldFiles --request "删除2020年之前的临时文件"
```

### 场景4：按项目整理代码

```bash
smart-tidy interactive ~/Projects
> 根据README和package.json把项目分类到不同语言的文件夹
```

## 常见问题

### Q: 如何避免覆盖已存在的文件？

A: 工具会自动处理文件名冲突，在目标文件已存在时自动重命名（添加序号）。

### Q: 操作失败后如何恢复？

A: 如果启用了自动备份（默认启用），可以使用 `smart-tidy undo` 撤销操作。

### Q: 如何提高分类准确度？

A: 
1. 使用交互式模式提供反馈
2. 提供更详细的需求描述
3. 开启元数据提取（默认开启）

### Q: 支持哪些文件类型？

A: 支持所有文件类型。对于PDF、图片、Office文档会提取元数据以提高分类准确度。

### Q: 如何处理大量文件？

A: 工具自动分批处理（默认每批50个），大量文件也能高效处理。

## 性能优化

### 提高扫描速度

```yaml
# 在 config/default_config.yaml 中调整
file_operations:
  scan_max_depth: 3  # 减少扫描深度
  max_file_size_mb: 50  # 跳过大文件的内容读取
```

### 提高分类速度

```yaml
ai:
  providers:
    claude:
      temperature: 0.5  # 降低温度提高速度
```

## 安全提示

1. **重要文件请备份**：虽然有撤销功能，但建议在整理前备份重要文件
2. **先使用预览模式**：使用 `--dry-run` 先查看操作结果
3. **逐步整理**：对于大量文件，建议分批次整理
4. **检查操作日志**：定期查看 `data/logs/` 中的操作日志

## 命令参考

完整的命令列表和参数说明：

```bash
# 主命令
smart-tidy --help

# 子命令帮助
smart-tidy organize --help
smart-tidy interactive --help
smart-tidy config --help
smart-tidy history --help
smart-tidy undo --help
```
