# 贡献指南

感谢您对 Smart File Tidy 项目的关注！

## 开发环境设置

1. Fork 并克隆仓库：
```bash
git clone https://github.com/yourusername/smart-file-tidy.git
cd smart-file-tidy
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
pip install -e .
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_file_scanner.py

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 代码风格

我们使用以下工具保持代码质量：

- **Black**: 代码格式化
- **Flake8**: 代码检查
- **MyPy**: 类型检查

```bash
# 格式化代码
black src/ tests/

# 检查代码
flake8 src/ tests/

# 类型检查
mypy src/
```

## 提交规范

提交信息应遵循以下格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链更新

示例：
```
feat(classifier): 添加基于元数据的分类规则

增加了PDF元数据（标题、作者）的提取和分析功能，
提高了学术论文的识别准确率。

Closes #123
```

## Pull Request 流程

1. 创建新分支：`git checkout -b feature/your-feature`
2. 进行修改并commit
3. 确保测试通过：`pytest`
4. 推送到您的fork：`git push origin feature/your-feature`
5. 在GitHub上创建Pull Request

## 开发建议

### 添加新功能

1. 首先编写测试用例
2. 实现功能
3. 确保测试通过
4. 更新文档

### 修复Bug

1. 添加能够重现bug的测试用例
2. 修复bug
3. 确保测试通过
4. 在commit信息中引用issue编号

## 问题报告

报告bug时，请包含：

- 操作系统和Python版本
- 完整的错误信息和堆栈追踪
- 重现步骤
- 预期行为和实际行为

## 功能建议

提出新功能时，请说明：

- 功能的使用场景
- 为什么这个功能有用
- 可能的实现方案

## 代码审查

所有Pull Request都需要经过代码审查。审查要点：

- 代码质量和可读性
- 测试覆盖率
- 文档完整性
- 性能影响

## 许可证

贡献的代码将遵循项目的MIT许可证。
