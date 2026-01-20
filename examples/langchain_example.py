"""LangChain Agent使用示例"""

import os
from pathlib import Path
from src.utils import ConfigManager
from src.langchain_integration import FileOrganizerAgent


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=" * 60)
    print("示例1: Agent基本使用")
    print("=" * 60)
    
    # 配置
    config = {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': 'claude-3-5-sonnet-20241022'
    }
    
    # 创建Agent
    agent = FileOrganizerAgent(
        llm_provider='claude',
        config=config,
        dry_run=True,  # 仅模拟，不实际执行
        verbose=True
    )
    
    # 整理文件
    result = agent.organize_files(
        directory='./test_files',
        user_request='按文件类型分类到不同文件夹'
    )
    
    print(f"\n执行结果: {result.get('success')}")
    if result.get('output'):
        print(f"\nAgent输出:\n{result['output']}")


def example_2_analyze_file():
    """示例2: 分析单个文件"""
    print("\n" + "=" * 60)
    print("示例2: 分析文件")
    print("=" * 60)
    
    config = {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': 'claude-3-5-sonnet-20241022'
    }
    
    agent = FileOrganizerAgent(
        llm_provider='claude',
        config=config,
        dry_run=True,
        verbose=False
    )
    
    # 分析文件
    test_file = './test_files/FULLTEXT01.pdf'
    if Path(test_file).exists():
        result = agent.analyze_file(test_file)
        
        print(f"\n文件名: {result.get('file_name')}")
        print(f"类型: {result.get('extension')}")
        print(f"大小: {result.get('size_mb')} MB")
        
        if 'content_analysis' in result:
            analysis = result['content_analysis']
            if analysis.get('success'):
                print(f"\n内容分析:\n{analysis.get('analysis')}")
    else:
        print(f"文件不存在: {test_file}")


def example_3_suggest_organization():
    """示例3: 获取整理建议"""
    print("\n" + "=" * 60)
    print("示例3: 获取整理建议")
    print("=" * 60)
    
    config = {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': 'claude-3-5-sonnet-20241022'
    }
    
    agent = FileOrganizerAgent(
        llm_provider='claude',
        config=config,
        dry_run=True,
        verbose=False
    )
    
    # 获取建议
    result = agent.suggest_organization('./test_files')
    
    if result.get('success'):
        print(f"\n整理建议:\n{result['suggestions']}")
    else:
        print(f"获取建议失败: {result.get('error')}")


def example_4_classify_files():
    """示例4: 将文件分类到指定类别"""
    print("\n" + "=" * 60)
    print("示例4: 文件分类")
    print("=" * 60)
    
    config = {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': 'claude-3-5-sonnet-20241022'
    }
    
    agent = FileOrganizerAgent(
        llm_provider='claude',
        config=config,
        dry_run=True,
        verbose=True
    )
    
    # 定义类别
    categories = ['学术论文', '技术文档', '其他文档']
    
    # 分类文件
    result = agent.classify_files(
        directory='./test_files',
        categories=categories
    )
    
    if result.get('success'):
        print(f"\n分类完成:\n{result['output']}")
    else:
        print(f"分类失败: {result.get('error')}")


def example_5_chat_interaction():
    """示例5: 与Agent对话"""
    print("\n" + "=" * 60)
    print("示例5: 与Agent对话")
    print("=" * 60)
    
    config = {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': 'claude-3-5-sonnet-20241022'
    }
    
    agent = FileOrganizerAgent(
        llm_provider='claude',
        config=config,
        dry_run=True,
        verbose=False
    )
    
    # 模拟对话
    messages = [
        "你好，我想整理我的文件",
        "我的下载文件夹里有很多PDF文件，应该如何整理？",
        "能帮我分析一下test_files目录吗？"
    ]
    
    for msg in messages:
        print(f"\n用户: {msg}")
        response = agent.chat(msg)
        print(f"Agent: {response}")
    
    # 查看对话历史
    print("\n" + "=" * 60)
    print("对话历史:")
    history = agent.get_chat_history()
    for i, item in enumerate(history[-6:], 1):  # 显示最后6条
        print(f"{i}. [{item['type']}] {item['content'][:100]}...")


def example_6_custom_api():
    """示例6: 使用自定义API"""
    print("\n" + "=" * 60)
    print("示例6: 使用自定义API（如DeepSeek）")
    print("=" * 60)
    
    # 使用自定义API配置
    config = {
        'base_url': os.getenv('CUSTOM_API_BASE_URL', 'https://api.deepseek.com/v1'),
        'api_key': os.getenv('CUSTOM_API_KEY', 'your-key'),
        'model': os.getenv('CUSTOM_API_MODEL', 'deepseek-chat')
    }
    
    if config['api_key'] == 'your-key':
        print("\n请设置环境变量 CUSTOM_API_KEY 来运行此示例")
        return
    
    agent = FileOrganizerAgent(
        llm_provider='custom',
        config=config,
        dry_run=True,
        verbose=False
    )
    
    # 测试对话
    response = agent.chat("介绍一下你的功能")
    print(f"\nAgent回复: {response}")


def example_7_content_analyzer():
    """示例7: 使用内容分析器"""
    print("\n" + "=" * 60)
    print("示例7: 内容分析器")
    print("=" * 60)
    
    from src.langchain_integration import ContentAnalyzer, LLMFactory
    
    # 创建LLM
    config = {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': 'claude-3-5-sonnet-20241022'
    }
    llm = LLMFactory.create_llm('claude', config)
    
    # 创建分析器
    analyzer = ContentAnalyzer(llm)
    
    # 分类内容
    content = "这是一篇关于机器学习的技术文档，讨论了神经网络的训练方法。"
    categories = ['技术文档', '学术论文', '个人笔记', '工作报告']
    
    category = analyzer.classify_content(content, categories)
    print(f"\n分类结果: {category}")
    
    # 提取关键词
    keywords = analyzer.extract_keywords(content, max_keywords=5)
    print(f"关键词: {', '.join(keywords)}")
    
    # 生成摘要
    summary = analyzer.summarize_content(content, max_length=100)
    print(f"摘要: {summary}")


def main():
    """主函数"""
    # 检查API密钥
    if not os.getenv('ANTHROPIC_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("请设置环境变量 ANTHROPIC_API_KEY 或 OPENAI_API_KEY")
        print("\n方法1: 命令行设置")
        print("export ANTHROPIC_API_KEY=your-key")
        print("\n方法2: .env文件")
        print("在项目根目录创建 .env 文件，添加:")
        print("ANTHROPIC_API_KEY=your-key")
        return
    
    # 运行示例
    try:
        # 基础示例
        # example_1_basic_usage()
        
        # 文件分析
        # example_2_analyze_file()
        
        # 整理建议
        # example_3_suggest_organization()
        
        # 文件分类
        # example_4_classify_files()
        
        # 对话交互
        example_5_chat_interaction()
        
        # 自定义API
        # example_6_custom_api()
        
        # 内容分析器
        # example_7_content_analyzer()
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
