"""快速测试文件操作"""
import sys
from pathlib import Path

sys.path.insert(0, 'src')

print("="*60)
print("快速文件操作测试")
print("="*60)

# 测试1：创建测试文件
print("\n[1] 创建测试文件...")
test_dir = Path("test_quick")
test_dir.mkdir(exist_ok=True)
test_file = test_dir / "test.txt"
test_file.write_text("测试内容")
print(f"✓ 创建: {test_file}")

# 测试2：核心 FileOperator
print("\n[2] 测试核心 FileOperator...")
from src.core.file_operator import FileOperator

operator = FileOperator(dry_run=False)

# 创建文件夹
print("  创建文件夹...")
operator.create_folder("test_quick/MyFolder")
if Path("test_quick/MyFolder").exists():
    print("  ✓ 文件夹创建成功!")
else:
    print("  ✗ 文件夹创建失败!")

# 移动文件
print("  移动文件...")
operator.move_file("test_quick/test.txt", "test_quick/MyFolder/test.txt")
if Path("test_quick/MyFolder/test.txt").exists():
    print("  ✓ 文件移动成功!")
else:
    print("  ✗ 文件移动失败!")

# 测试3：LangChain Tool
print("\n[3] 测试 LangChain FileOperatorTool...")
from src.langchain_integration.tools.file_operator_tool import FileOperatorTool

tool = FileOperatorTool(dry_run=False)

# 创建另一个文件夹
print("  使用工具创建文件夹...")
result = tool._run(
    operation_type="create_folder",
    source="",
    target="test_quick/ToolFolder",
    reason="测试"
)
if Path("test_quick/ToolFolder").exists():
    print("  ✓ 工具创建文件夹成功!")
else:
    print("  ✗ 工具创建文件夹失败!")

print("\n" + "="*60)
print("测试完成！请检查 test_quick 目录")
print("="*60)

# 显示目录结构
print("\n目录结构:")
for item in sorted(test_dir.rglob("*")):
    indent = "  " * (len(item.relative_to(test_dir).parts))
    if item.is_file():
        print(f"{indent}📄 {item.name}")
    else:
        print(f"{indent}📁 {item.name}/")

print("\n提示：测试目录 'test_quick' 已创建，请手动删除")
