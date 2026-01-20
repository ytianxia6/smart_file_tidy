"""快速测试 LangChain Agent 导入是否正常"""

import sys

print("=" * 60)
print("  LangChain Agent 导入测试")
print("=" * 60)

# 测试1: 基础导入
print("\n[1/5] 测试基础导入...")
try:
    from src.langchain_integration import FileOrganizerAgent
    print("✓ FileOrganizerAgent 导入成功")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试2: 工具导入
print("\n[2/5] 测试工具导入...")
try:
    from src.langchain_integration.tools import (
        FileScannerTool,
        FileAnalyzerTool,
        FileOperatorTool,
        ValidationTool
    )
    print("✓ 所有工具导入成功")
except ImportError as e:
    print(f"✗ 工具导入失败: {e}")
    sys.exit(1)

# 测试3: LLM 工厂
print("\n[3/5] 测试 LLM 工厂...")
try:
    from src.langchain_integration import LLMFactory
    print("✓ LLMFactory 导入成功")
except ImportError as e:
    print(f"✗ LLM工厂导入失败: {e}")
    sys.exit(1)

# 测试4: 配置管理器
print("\n[4/5] 测试配置管理器...")
try:
    from src.utils import ConfigManager
    config = ConfigManager()
    provider = config.get_default_provider()
    print(f"✓ ConfigManager 导入成功")
    print(f"  默认提供商: {provider}")
except Exception as e:
    print(f"✗ 配置管理器失败: {e}")
    sys.exit(1)

# 测试5: Agent 创建（如果有配置）
print("\n[5/5] 测试 Agent 创建...")
try:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # 检查是否有API密钥
    has_config = False
    provider = config.get_default_provider()
    
    if provider == 'claude' and os.getenv('ANTHROPIC_API_KEY'):
        has_config = True
    elif provider == 'openai' and os.getenv('OPENAI_API_KEY'):
        has_config = True
    elif provider == 'custom' and os.getenv('CUSTOM_API_KEY'):
        has_config = True
    elif provider == 'local':
        has_config = True
    
    if not has_config:
        print("⊘ 跳过 Agent 创建测试（未配置API密钥）")
        print("  请配置 .env 文件后再测试完整功能")
    else:
        ai_config = config.get_ai_config(provider)
        agent = FileOrganizerAgent(
            llm_provider=provider,
            config=ai_config,
            dry_run=True,
            verbose=False
        )
        print("✓ Agent 创建成功")
        print(f"  LLM 提供商: {provider}")
        print(f"  可用工具: {len(agent.tools)} 个")

except Exception as e:
    print(f"✗ Agent 创建失败: {e}")
    import traceback
    print(f"\n详细错误信息:")
    print(traceback.format_exc())
    sys.exit(1)

# 总结
print("\n" + "=" * 60)
print("  测试结果")
print("=" * 60)
print("\n✅ 所有导入测试通过！")
print("\n您现在可以使用以下命令：")
print("  uv run smart-tidy agent ./test_files --request \"测试\"")
print("  uv run smart-tidy chat")
print("  python examples/test_custom_api.py")
print("\n如果您已配置 .env 文件，Agent 功能应该可以正常工作。")
print("如未配置，请参考: CUSTOM_API_QUICKSTART.md")
print("=" * 60)
