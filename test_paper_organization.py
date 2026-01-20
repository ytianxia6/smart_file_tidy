"""测试论文自动整理功能"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.config import Config
from src.langchain_integration.agent import FileOrganizerAgent


def test_paper_organization():
    """测试论文自动整理"""
    print("="*60)
    print("论文自动整理功能测试")
    print("="*60)
    
    # 1. 加载配置
    print("\n[1/4] 加载配置...")
    config = Config()
    
    ai_provider = config.get('ai_provider', 'custom')
    ai_config = config.get_ai_config(ai_provider)
    
    print(f"  ✓ AI提供商: {ai_provider}")
    print(f"  ✓ 模型: {ai_config.get('model', 'unknown')}")
    
    # 2. 创建Agent
    print("\n[2/4] 创建Agent...")
    try:
        agent = FileOrganizerAgent(
            llm_provider=ai_provider,
            config=ai_config,
            dry_run=False,  # 真实执行
            verbose=True
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
    
    print(f"\n[3/4] 扫描测试目录: {test_dir}")
    pdf_files = list(Path(test_dir).glob("*.pdf"))
    print(f"  ✓ 找到 {len(pdf_files)} 个PDF文件")
    for pdf in pdf_files[:5]:  # 只显示前5个
        print(f"    - {pdf.name}")
    if len(pdf_files) > 5:
        print(f"    ... 还有 {len(pdf_files) - 5} 个文件")
    
    # 4. 执行论文整理
    print(f"\n[4/4] 执行论文自动整理...")
    print("="*60)
    
    try:
        # 默认请求会触发论文整理模式
        result = agent.organize_files(
            directory=test_dir,
            user_request="智能整理这些文件"  # 通用请求 -> 默认论文整理
        )
        
        print("\n" + "="*60)
        print("执行结果:")
        print("="*60)
        
        if result.get('success'):
            print("✓ 整理成功！")
            if 'message' in result:
                print(f"\n{result['message']}")
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


def test_paper_identification():
    """测试论文识别功能"""
    print("\n" + "="*60)
    print("论文识别功能测试")
    print("="*60)
    
    from src.utils.config import Config
    from src.langchain_integration.llm_factory import LLMFactory
    from src.langchain_integration.content_analyzer import ContentAnalyzer
    
    # 加载配置
    config = Config()
    ai_provider = config.get('ai_provider', 'custom')
    ai_config = config.get_ai_config(ai_provider)
    
    # 创建LLM和分析器
    print(f"\n创建ContentAnalyzer (使用 {ai_provider})...")
    llm = LLMFactory.create_llm(ai_provider, ai_config)
    analyzer = ContentAnalyzer(llm)
    print("  ✓ ContentAnalyzer创建成功")
    
    # 测试论文识别
    test_dir = Path("./test_files")
    pdf_files = list(test_dir.glob("*.pdf"))[:3]  # 只测试前3个
    
    print(f"\n测试论文识别（共 {len(pdf_files)} 个文件）:")
    print("-"*60)
    
    for pdf_file in pdf_files:
        print(f"\n文件: {pdf_file.name}")
        try:
            paper_info = analyzer.identify_paper(str(pdf_file))
            
            if paper_info.get('is_paper'):
                print("  ✓ 识别为学术论文")
                print(f"  置信度: {paper_info.get('confidence', 0):.2f}")
                if paper_info.get('title'):
                    print(f"  标题: {paper_info['title']}")
                if paper_info.get('authors'):
                    print(f"  作者: {', '.join(paper_info['authors'][:3])}")
                if paper_info.get('year'):
                    print(f"  年份: {paper_info['year']}")
            else:
                print("  ✗ 不是学术论文")
                print(f"  原因: {paper_info.get('reason', '未知')}")
                
        except Exception as e:
            print(f"  ✗ 识别失败: {e}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║          论文自动整理功能测试                              ║
║                                                          ║
║  本测试会：                                              ║
║  1. 扫描 test_files 目录中的 PDF 文件                    ║
║  2. 识别哪些是学术论文                                   ║
║  3. 自动创建 "Papers" 或 "学术论文" 文件夹                ║
║  4. 将论文移动到该文件夹                                 ║
║                                                          ║
║  ⚠️  注意：这会真实移动文件！                             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    # 询问确认
    response = input("是否继续测试？(y/N): ").strip().lower()
    if response != 'y':
        print("已取消测试")
        sys.exit(0)
    
    # 运行测试
    print("\n" + "="*60)
    print("开始测试...")
    print("="*60)
    
    # 先测试论文识别
    print("\n【测试1】论文识别功能")
    test_paper_identification()
    
    # 再测试完整的论文整理
    print("\n\n【测试2】论文自动整理")
    success = test_paper_organization()
    
    # 总结
    print("\n" + "="*60)
    if success:
        print("✓ 测试完成！")
        print("\n请检查 test_files 目录，论文应该已被移动到专门的文件夹")
    else:
        print("✗ 测试失败，请检查错误信息")
    print("="*60)
