"""测试 ReAct 模式工具调用"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.config import Config
from src.langchain_integration.agent import FileOrganizerAgent


def test_react_parsing():
    """测试 ReAct 输出解析"""
    print("="*60)
    print("测试 ReAct 输出解析")
    print("="*60)
    
    # 创建一个简单的 Agent 实例来测试解析
    config = Config()
    ai_provider = config.get('ai_provider', 'custom')
    ai_config = config.get_ai_config(ai_provider)
    
    agent = FileOrganizerAgent(
        llm_provider=ai_provider,
        config=ai_config,
        dry_run=True,
        verbose=False
    )
    
    # 测试用例
    test_cases = [
        {
            "name": "正常的工具调用",
            "text": """
Thought: 我需要扫描目录
Action: file_scanner
Action Input: {"directory": "./test_files"}
""",
            "expected_action": "file_scanner"
        },
        {
            "name": "最终答案",
            "text": """
Thought: 所有任务已完成
Final Answer: 成功整理了7个论文
""",
            "expected_action": "Final Answer"
        },
        {
            "name": "复杂的 JSON",
            "text": """
Thought: 移动文件
Action: file_operator
Action Input: {"operation_type": "move", "source": "./test_files/paper.pdf", "target": "./test_files/Papers/paper.pdf", "reason": "移动论文"}
""",
            "expected_action": "file_operator"
        }
    ]
    
    print("\n测试解析功能:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        action, action_input, thought = agent._parse_react_output(test_case['text'])
        
        if action == test_case['expected_action']:
            print(f"  ✓ Action 正确: {action}")
        else:
            print(f"  ✗ Action 错误: 期望 {test_case['expected_action']}, 得到 {action}")
        
        if action_input:
            print(f"  ✓ Action Input: {action_input}")
        
        if thought:
            print(f"  ✓ Thought: {thought[:50]}...")


def test_paper_organization():
    """测试完整的论文整理流程"""
    print("\n" + "="*60)
    print("测试完整的论文整理流程")
    print("="*60)
    
    # 1. 加载配置
    print("\n[1/4] 加载配置...")
    config = Config()
    
    ai_provider = config.get('ai_provider', 'custom')
    ai_config = config.get_ai_config(ai_provider)
    
    print(f"  ✓ AI提供商: {ai_provider}")
    print(f"  ✓ 模型: {ai_config.get('model', 'unknown')}")
    
    # 2. 创建Agent
    print("\n[2/4] 创建Agent (使用 ReAct 模式)...")
    try:
        agent = FileOrganizerAgent(
            llm_provider=ai_provider,
            config=ai_config,
            dry_run=False,  # 真实执行
            verbose=True     # 显示详细信息
        )
        print("  ✓ Agent创建成功")
    except Exception as e:
        print(f"  ✗ Agent创建失败: {e}")
        return False
    
    # 3. 测试目录
    test_dir = "./test_files"
    if not Path(test_dir).exists():
        print(f"\n  ✗ 测试目录不存在: {test_dir}")
        print("  请先创建测试目录并放入一些PDF文件")
        return False
    
    print(f"\n[3/4] 检查测试目录: {test_dir}")
    pdf_files = list(Path(test_dir).glob("*.pdf"))
    print(f"  ✓ 找到 {len(pdf_files)} 个PDF文件")
    
    # 4. 执行论文整理
    print(f"\n[4/4] 执行论文整理 (ReAct 模式)...")
    print("="*60)
    
    try:
        result = agent.organize_files(
            directory=test_dir,
            user_request="智能整理这些文件"
        )
        
        print("\n" + "="*60)
        print("执行结果:")
        print("="*60)
        
        if result.get('success'):
            print("✓ 整理成功！")
            if 'output' in result:
                print(f"\n{result['output']}")
        else:
            print("✗ 整理失败")
            if 'error' in result:
                print(f"错误: {result['error']}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║          ReAct 模式测试                                   ║
║                                                          ║
║  本测试会验证：                                          ║
║  1. ReAct 输出解析功能                                   ║
║  2. 工具调用是否真正执行                                 ║
║  3. 完整的论文整理流程                                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 测试1: 解析功能
    print("\n【测试1】ReAct 解析功能")
    test_react_parsing()
    
    # 询问是否继续完整测试
    print("\n" + "="*60)
    response = input("\n是否继续完整的论文整理测试？(会真实移动文件) (y/N): ").strip().lower()
    if response != 'y':
        print("已取消完整测试")
        sys.exit(0)
    
    # 测试2: 完整流程
    print("\n【测试2】完整的论文整理流程")
    success = test_paper_organization()
    
    # 总结
    print("\n" + "="*60)
    if success:
        print("✓ 所有测试通过！ReAct 模式工作正常")
        print("\n请检查 test_files 目录，论文应该已被移动到专门的文件夹")
    else:
        print("✗ 测试失败，请检查错误信息")
    print("="*60)
