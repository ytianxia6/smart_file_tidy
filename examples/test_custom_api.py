"""测试自定义API与LangChain集成"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def print_header(title: str):
    """打印标题"""
    console.print(f"\n{'='*60}")
    console.print(f"  {title}")
    console.print('='*60 + "\n")


def test_1_check_env_vars():
    """测试1: 检查环境变量"""
    print_header("测试1: 检查环境变量配置")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'DEFAULT_AI_PROVIDER': os.getenv('DEFAULT_AI_PROVIDER'),
        'CUSTOM_API_BASE_URL': os.getenv('CUSTOM_API_BASE_URL'),
        'CUSTOM_API_KEY': os.getenv('CUSTOM_API_KEY'),
        'CUSTOM_API_MODEL': os.getenv('CUSTOM_API_MODEL'),
    }
    
    table = Table(title="环境变量检查")
    table.add_column("变量名", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("值", style="yellow")
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            status = "✓ 已设置"
            # 隐藏API密钥
            if 'KEY' in var_name and len(var_value) > 10:
                display_value = var_value[:8] + '...' + var_value[-4:]
            else:
                display_value = var_value
        else:
            status = "✗ 未设置"
            display_value = "N/A"
            all_set = False
        
        table.add_row(var_name, status, display_value)
    
    console.print(table)
    
    if not all_set:
        console.print("\n[red]❌ 环境变量未完全配置！[/red]")
        console.print("\n请在项目根目录创建或编辑 .env 文件，添加以下内容：\n")
        console.print(Panel(
            """DEFAULT_AI_PROVIDER=custom
CUSTOM_API_BASE_URL=https://api.example.com/v1
CUSTOM_API_KEY=sk-your-api-key
CUSTOM_API_MODEL=your-model-name

# 示例：使用DeepSeek
# CUSTOM_API_BASE_URL=https://api.deepseek.com/v1
# CUSTOM_API_KEY=sk-your-deepseek-key
# CUSTOM_API_MODEL=deepseek-chat

# 示例：使用通义千问
# CUSTOM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# CUSTOM_API_KEY=sk-your-qwen-key
# CUSTOM_API_MODEL=qwen-plus""",
            title="示例配置",
            border_style="yellow"
        ))
        return False
    
    console.print("\n[green]✓ 所有环境变量已正确配置！[/green]")
    return True


def test_2_config_manager():
    """测试2: ConfigManager加载配置"""
    print_header("测试2: ConfigManager配置加载")
    
    try:
        from src.utils import ConfigManager
        
        config = ConfigManager()
        provider = config.get_default_provider()
        ai_config = config.get_ai_config(provider)
        
        console.print(f"[cyan]默认提供商:[/cyan] {provider}")
        console.print(f"[cyan]API地址:[/cyan] {ai_config.get('base_url')}")
        console.print(f"[cyan]模型:[/cyan] {ai_config.get('model')}")
        console.print(f"[cyan]API密钥:[/cyan] {'已设置' if ai_config.get('api_key') else '未设置'}")
        
        if provider != 'custom':
            console.print(f"\n[yellow]⚠ 警告: DEFAULT_AI_PROVIDER={provider}，应该是'custom'[/yellow]")
            return False
        
        if not ai_config.get('base_url'):
            console.print("\n[red]❌ API地址未配置！[/red]")
            return False
        
        if not ai_config.get('api_key'):
            console.print("\n[red]❌ API密钥未配置！[/red]")
            return False
        
        if not ai_config.get('model'):
            console.print("\n[red]❌ 模型名称未配置！[/red]")
            return False
        
        console.print("\n[green]✓ ConfigManager配置加载成功！[/green]")
        return True
        
    except Exception as e:
        console.print(f"\n[red]❌ 配置加载失败: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def test_3_llm_creation():
    """测试3: LLM创建"""
    print_header("测试3: LLM实例创建")
    
    try:
        from src.utils import ConfigManager
        from src.langchain_integration import LLMFactory
        
        config_manager = ConfigManager()
        provider = config_manager.get_default_provider()
        ai_config = config_manager.get_ai_config(provider)
        
        console.print(f"[cyan]正在创建LLM实例...[/cyan]")
        llm = LLMFactory.create_llm(provider, ai_config)
        
        console.print(f"[cyan]LLM类型:[/cyan] {type(llm).__name__}")
        console.print(f"[cyan]模型:[/cyan] {llm.model_name if hasattr(llm, 'model_name') else 'N/A'}")
        
        console.print("\n[green]✓ LLM实例创建成功！[/green]")
        return llm
        
    except ValueError as e:
        console.print(f"\n[red]❌ 配置错误: {e}[/red]")
        console.print("\n请检查 .env 文件中的配置是否正确")
        return None
    except Exception as e:
        console.print(f"\n[red]❌ LLM创建失败: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return None


def test_4_llm_connection(llm):
    """测试4: LLM连接测试"""
    print_header("测试4: LLM连接测试")
    
    if not llm:
        console.print("[red]❌ 跳过测试（LLM未创建）[/red]")
        return False
    
    try:
        console.print("[cyan]正在发送测试消息...[/cyan]")
        
        response = llm.invoke("你好，请回复'连接成功'")
        
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
        
        console.print(f"\n[cyan]LLM响应:[/cyan]")
        console.print(Panel(content, border_style="green"))
        
        console.print("\n[green]✓ LLM连接测试成功！[/green]")
        return True
        
    except Exception as e:
        console.print(f"\n[red]❌ 连接测试失败: {e}[/red]")
        console.print("\n可能的原因：")
        console.print("  1. API密钥无效或已过期")
        console.print("  2. API地址不正确")
        console.print("  3. 网络连接问题")
        console.print("  4. API余额不足")
        console.print("  5. 模型名称错误")
        return False


def test_5_agent_creation():
    """测试5: Agent创建"""
    print_header("测试5: FileOrganizerAgent创建")
    
    try:
        from src.utils import ConfigManager
        from src.langchain_integration import FileOrganizerAgent
        
        config_manager = ConfigManager()
        provider = config_manager.get_default_provider()
        ai_config = config_manager.get_ai_config(provider)
        
        console.print("[cyan]正在创建Agent...[/cyan]")
        
        agent = FileOrganizerAgent(
            llm_provider=provider,
            config=ai_config,
            dry_run=True,  # 仅模拟
            verbose=False
        )
        
        console.print(f"[cyan]Agent工具数量:[/cyan] {len(agent.tools)}")
        console.print(f"[cyan]工具列表:[/cyan]")
        for tool in agent.tools:
            console.print(f"  • {tool.name}: {tool.description[:50]}...")
        
        console.print("\n[green]✓ Agent创建成功！[/green]")
        return agent
        
    except Exception as e:
        console.print(f"\n[red]❌ Agent创建失败: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return None


def test_6_agent_chat(agent):
    """测试6: Agent对话测试"""
    print_header("测试6: Agent对话测试")
    
    if not agent:
        console.print("[red]❌ 跳过测试（Agent未创建）[/red]")
        return False
    
    try:
        console.print("[cyan]正在与Agent对话...[/cyan]")
        
        test_message = "你好，请简单介绍一下你的功能"
        console.print(f"\n[yellow]用户:[/yellow] {test_message}")
        
        response = agent.chat(test_message)
        
        console.print(f"\n[green]Agent:[/green]")
        console.print(Panel(response, border_style="cyan"))
        
        console.print("\n[green]✓ Agent对话测试成功！[/green]")
        return True
        
    except Exception as e:
        console.print(f"\n[red]❌ 对话测试失败: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def test_7_file_analysis(agent):
    """测试7: 文件分析测试"""
    print_header("测试7: 文件分析测试（可选）")
    
    if not agent:
        console.print("[red]❌ 跳过测试（Agent未创建）[/red]")
        return False
    
    # 查找测试文件
    test_files = list(Path('test_files').glob('*.pdf')) if Path('test_files').exists() else []
    
    if not test_files:
        console.print("[yellow]⚠ 未找到测试文件，跳过此测试[/yellow]")
        console.print("（可在 test_files 目录放置PDF文件进行测试）")
        return True
    
    try:
        test_file = str(test_files[0])
        console.print(f"[cyan]正在分析文件:[/cyan] {test_file}")
        
        result = agent.analyze_file(test_file)
        
        console.print(f"\n[cyan]文件信息:[/cyan]")
        console.print(f"  文件名: {result.get('file_name')}")
        console.print(f"  类型: {result.get('extension')}")
        console.print(f"  大小: {result.get('size_mb')} MB")
        
        if 'content_analysis' in result:
            analysis = result['content_analysis']
            if analysis.get('success'):
                console.print(f"\n[cyan]内容分析:[/cyan]")
                console.print(Panel(str(analysis.get('analysis', ''))[:200] + "...", border_style="green"))
        
        console.print("\n[green]✓ 文件分析测试成功！[/green]")
        return True
        
    except Exception as e:
        console.print(f"\n[red]❌ 文件分析失败: {e}[/red]")
        return False


def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold cyan]自定义API与LangChain集成测试[/bold cyan]\n\n"
        "本脚本将验证您的自定义API配置是否正确，\n"
        "并测试与LangChain Agent的集成。",
        border_style="cyan"
    ))
    
    results = {
        '环境变量检查': False,
        'ConfigManager': False,
        'LLM创建': False,
        'LLM连接': False,
        'Agent创建': False,
        'Agent对话': False,
        '文件分析': False,
    }
    
    # 运行测试
    results['环境变量检查'] = test_1_check_env_vars()
    if not results['环境变量检查']:
        print_summary(results)
        return
    
    results['ConfigManager'] = test_2_config_manager()
    if not results['ConfigManager']:
        print_summary(results)
        return
    
    llm = test_3_llm_creation()
    results['LLM创建'] = llm is not None
    
    if llm:
        results['LLM连接'] = test_4_llm_connection(llm)
    
    agent = test_5_agent_creation()
    results['Agent创建'] = agent is not None
    
    if agent:
        results['Agent对话'] = test_6_agent_chat(agent)
        results['文件分析'] = test_7_file_analysis(agent)
    
    # 打印总结
    print_summary(results)


def print_summary(results: dict):
    """打印测试总结"""
    print_header("测试总结")
    
    table = Table(title="测试结果")
    table.add_column("测试项", style="cyan")
    table.add_column("结果", style="bold")
    
    for test_name, passed in results.items():
        if passed:
            status = "[green]✓ 通过[/green]"
        elif passed is None:
            status = "[yellow]⊘ 跳过[/yellow]"
        else:
            status = "[red]✗ 失败[/red]"
        table.add_row(test_name, status)
    
    console.print(table)
    
    # 统计
    passed_count = sum(1 for v in results.values() if v is True)
    total_count = len(results)
    
    console.print(f"\n[cyan]通过:[/cyan] {passed_count}/{total_count}")
    
    if passed_count == total_count:
        console.print("\n[bold green]🎉 所有测试通过！您的配置完全正确！[/bold green]")
        console.print("\n现在可以使用以下命令：")
        console.print("  smart-tidy agent ./test_files --request '按类型分类'")
        console.print("  smart-tidy chat")
        console.print("  smart-tidy suggest ./test_files")
    elif passed_count >= 5:
        console.print("\n[yellow]⚠ 大部分测试通过，基本功能可用[/yellow]")
    else:
        console.print("\n[red]❌ 配置存在问题，请检查并修复[/red]")
        console.print("\n请参考文档: docs/CUSTOM_API_LANGCHAIN.md")


if __name__ == "__main__":
    main()
