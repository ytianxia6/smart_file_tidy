"""基本使用示例"""

from src.utils import ConfigManager
from src.core import Controller


def basic_organize_example():
    """基本整理示例"""
    # 初始化配置和控制器
    config = ConfigManager()
    controller = Controller(config, ai_provider='claude')
    
    # 扫描目录
    print("扫描目录...")
    files = controller.scan_directory(
        directory='./test_files',
        recursive=False
    )
    print(f"发现 {len(files)} 个文件")
    
    # 生成整理方案
    print("\n生成整理方案...")
    operations = controller.generate_plan(
        files=files,
        user_request="把所有PDF文件移动到documents文件夹"
    )
    
    # 预览操作
    print(f"\n将执行 {len(operations)} 个操作：")
    for op in operations[:5]:  # 只显示前5个
        print(f"  {op.type.value}: {op.source} -> {op.target}")
    
    # 执行操作（实际使用时需要用户确认）
    # result = controller.execute_operations(operations)
    # print(f"\n完成！成功: {result.success_count}, 失败: {result.failed_count}")


def interactive_example():
    """交互式示例"""
    config = ConfigManager()
    controller = Controller(config)
    
    # 扫描目录
    files = controller.scan_directory('./test_files')
    
    # 第一轮：初始整理
    operations = controller.generate_plan(
        files=files,
        user_request="整理所有文件"
    )
    
    # 假设用户提供反馈
    feedback = "数字文件名的PDF不是论文，请单独分类"
    
    # 第二轮：根据反馈优化
    refined_operations = controller.refine_plan(
        previous_operations=operations,
        feedback=feedback
    )
    
    print(f"优化后的方案包含 {len(refined_operations)} 个操作")


def undo_example():
    """撤销示例"""
    config = ConfigManager()
    controller = Controller(config)
    
    # 执行一些操作...
    # result = controller.execute_operations(operations)
    
    # 撤销最后一次操作
    if controller.undo_manager.can_undo():
        success = controller.undo_last_operation()
        if success:
            print("撤销成功！")


if __name__ == '__main__':
    print("Smart File Tidy 使用示例\n")
    print("=" * 50)
    
    # 取消注释以运行示例
    # basic_organize_example()
    # interactive_example()
    # undo_example()
    
    print("\n请根据需要修改示例代码并运行")
