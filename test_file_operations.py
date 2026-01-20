"""测试文件操作功能是否真正执行"""

import sys
import os
import shutil
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.file_scanner import FileScanner
from src.core.file_operator import FileOperator
from src.langchain_integration.tools import (
    FileScannerTool,
    FileOperatorTool,
    FileAnalyzerTool
)


def setup_test_environment():
    """创建测试环境"""
    print("="*60)
    print("设置测试环境")
    print("="*60)
    
    # 创建测试目录
    test_dir = Path("./test_operations")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # 创建测试文件
    test_files = [
        "test_paper1.pdf",
        "test_paper2.pdf",
        "test_document.txt",
        "test_image.jpg"
    ]
    
    for filename in test_files:
        file_path = test_dir / filename
        file_path.write_text(f"这是测试文件: {filename}\n测试内容。")
    
    print(f"✓ 创建测试目录: {test_dir}")
    print(f"✓ 创建 {len(test_files)} 个测试文件")
    
    return test_dir


def test_core_scanner():
    """测试核心扫描器"""
    print("\n" + "="*60)
    print("测试 1: 核心文件扫描器")
    print("="*60)
    
    scanner = FileScanner()
    
    try:
        files = scanner.scan_directory("./test_operations")
        print(f"✓ 扫描成功")
        print(f"✓ 找到 {len(files)} 个文件")
        for file in files:
            print(f"  - {file.name} ({file.size} bytes)")
        return True
    except Exception as e:
        print(f"✗ 扫描失败: {e}")
        return False


def test_core_operator():
    """测试核心文件操作器"""
    print("\n" + "="*60)
    print("测试 2: 核心文件操作器")
    print("="*60)
    
    operator = FileOperator(dry_run=False)  # 确保不是 dry_run
    
    try:
        # 测试创建文件夹
        print("\n[2.1] 创建文件夹...")
        papers_dir = "./test_operations/Papers"
        result = operator.create_folder(papers_dir)
        if Path(papers_dir).exists():
            print(f"✓ 文件夹创建成功: {papers_dir}")
        else:
            print(f"✗ 文件夹创建失败")
            return False
        
        # 测试移动文件
        print("\n[2.2] 移动文件...")
        source = "./test_operations/test_paper1.pdf"
        target = "./test_operations/Papers/test_paper1.pdf"
        
        if Path(source).exists():
            result = operator.move_file(source, target)
            if Path(target).exists() and not Path(source).exists():
                print(f"✓ 文件移动成功: {source} -> {target}")
            else:
                print(f"✗ 文件移动失败")
                print(f"  源文件存在: {Path(source).exists()}")
                print(f"  目标文件存在: {Path(target).exists()}")
                return False
        else:
            print(f"✗ 源文件不存在: {source}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_langchain_tools():
    """测试 LangChain 工具"""
    print("\n" + "="*60)
    print("测试 3: LangChain 工具")
    print("="*60)
    
    try:
        # 测试扫描工具
        print("\n[3.1] 测试 FileScannerTool...")
        scanner_tool = FileScannerTool()
        result = scanner_tool._run(directory="./test_operations")
        print(f"✓ 扫描工具返回: {result[:200]}...")
        
        # 测试操作工具
        print("\n[3.2] 测试 FileOperatorTool（创建文件夹）...")
        operator_tool = FileOperatorTool(dry_run=False)
        
        # 创建另一个文件夹
        result = operator_tool._run(
            operation_type="create_folder",
            source="",
            target="./test_operations/Documents",
            reason="测试创建文件夹"
        )
        print(f"✓ 操作工具返回: {result[:200]}...")
        
        if Path("./test_operations/Documents").exists():
            print(f"✓ Documents 文件夹创建成功")
        else:
            print(f"✗ Documents 文件夹创建失败")
            return False
        
        # 移动另一个文件
        print("\n[3.3] 测试 FileOperatorTool（移动文件）...")
        result = operator_tool._run(
            operation_type="move",
            source="./test_operations/test_document.txt",
            target="./test_operations/Documents/test_document.txt",
            reason="测试移动文件"
        )
        print(f"✓ 操作工具返回: {result[:200]}...")
        
        if Path("./test_operations/Documents/test_document.txt").exists():
            print(f"✓ 文件移动成功")
        else:
            print(f"✗ 文件移动失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_results():
    """验证最终结果"""
    print("\n" + "="*60)
    print("验证最终结果")
    print("="*60)
    
    test_dir = Path("./test_operations")
    
    # 列出所有文件和文件夹
    print("\n目录结构:")
    for item in sorted(test_dir.rglob("*")):
        indent = "  " * (len(item.relative_to(test_dir).parts) - 1)
        if item.is_file():
            print(f"{indent}📄 {item.name}")
        else:
            print(f"{indent}📁 {item.name}/")
    
    # 验证预期结果
    checks = [
        ("Papers 文件夹存在", (test_dir / "Papers").exists()),
        ("Documents 文件夹存在", (test_dir / "Documents").exists()),
        ("test_paper1.pdf 在 Papers 中", (test_dir / "Papers" / "test_paper1.pdf").exists()),
        ("test_document.txt 在 Documents 中", (test_dir / "Documents" / "test_document.txt").exists()),
        ("test_paper1.pdf 不在根目录", not (test_dir / "test_paper1.pdf").exists()),
        ("test_document.txt 不在根目录", not (test_dir / "test_document.txt").exists()),
    ]
    
    print("\n验证检查:")
    all_passed = True
    for desc, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {desc}")
        if not passed:
            all_passed = False
    
    return all_passed


def cleanup():
    """清理测试环境"""
    print("\n" + "="*60)
    print("清理测试环境")
    print("="*60)
    
    response = input("是否删除测试目录 ./test_operations？(y/N): ").strip().lower()
    if response == 'y':
        shutil.rmtree("./test_operations")
        print("✓ 测试目录已删除")
    else:
        print("✓ 保留测试目录供查看")


def main():
    """主测试流程"""
    print("""
╔══════════════════════════════════════════════════════════╗
║          文件操作功能测试                                 ║
║                                                          ║
║  本测试将验证：                                          ║
║  1. FileScanner 是否真正扫描文件                         ║
║  2. FileOperator 是否真正创建文件夹                      ║
║  3. FileOperator 是否真正移动文件                        ║
║  4. LangChain 工具是否正确调用核心功能                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    try:
        # 设置测试环境
        test_dir = setup_test_environment()
        
        # 运行测试
        results = []
        results.append(("核心扫描器", test_core_scanner()))
        results.append(("核心操作器", test_core_operator()))
        results.append(("LangChain 工具", test_langchain_tools()))
        results.append(("结果验证", verify_results()))
        
        # 总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        for name, passed in results:
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"{status}: {name}")
        
        all_passed = all(result for _, result in results)
        
        if all_passed:
            print("\n" + "🎉 "*10)
            print("所有测试通过！文件操作功能正常工作！")
            print("🎉 "*10)
        else:
            print("\n" + "❌ "*10)
            print("部分测试失败，请检查错误信息")
            print("❌ "*10)
        
        # 清理
        cleanup()
        
        return all_passed
        
    except Exception as e:
        print(f"\n✗ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
