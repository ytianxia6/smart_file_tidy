"""配置命令"""

import typer
from rich.console import Console
from rich.table import Table

from ..utils import ConfigManager

config_app = typer.Typer(help="配置管理")
console = Console()


@config_app.command("show")
def show_config():
    """显示当前配置"""
    try:
        config = ConfigManager()
        
        console.print("\n[bold cyan]当前配置：[/bold cyan]\n")
        
        # AI提供商配置
        provider = config.get_default_provider()
        console.print(f"[green]默认AI提供商:[/green] {provider}")
        
        # 显示提供商详细配置
        ai_config = config.get_ai_config(provider)
        table = Table(title=f"{provider.upper()} 配置")
        table.add_column("配置项", style="cyan")
        table.add_column("值", style="yellow")
        
        for key, value in ai_config.items():
            if key == 'api_key' and value:
                # 隐藏API Key
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = str(value)
            table.add_row(key, display_value)
        
        console.print(table)
        
        # 文件操作配置
        console.print(f"\n[green]批次大小:[/green] {config.get('file_operations.batch_size')}")
        console.print(f"[green]最大文件大小:[/green] {config.get('file_operations.max_file_size_mb')} MB")
        console.print(f"[green]最大扫描深度:[/green] {config.get('file_operations.scan_max_depth')}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@config_app.command("set-provider")
def set_provider(
    provider: str = typer.Argument(..., help="提供商名称 (claude/openai/local/custom)"),
    api_key: str = typer.Option(None, "--api-key", help="API密钥"),
    model: str = typer.Option(None, "--model", help="模型名称"),
    base_url: str = typer.Option(None, "--base-url", help="API地址（custom/local提供商可选）"),
):
    """设置AI提供商（快捷配置工具，实际写入.env文件）
    
    💡 推荐方式：直接编辑 .env 文件
    
    此命令提供快捷方式，会自动将配置写入 .env 文件。
    
    示例：
      # Claude
      smart-tidy config set-provider claude --api-key sk-xxx
      
      # 自定义API（通义千问）
      smart-tidy config set-provider custom \\
        --base-url https://dashscope.aliyuncs.com/compatible-mode/v1 \\
        --api-key sk-xxx --model qwen-plus
    
    查看所有配置选项：cat .env.example
    """
    try:
        config = ConfigManager()
        
        # 验证提供商
        if provider not in ['claude', 'openai', 'local', 'custom']:
            console.print(f"[red]错误：不支持的提供商 '{provider}'[/red]")
            console.print("支持的提供商: claude, openai, local, custom")
            return
        
        # 设置默认提供商
        config.set('ai.default_provider', provider)
        
        # 处理custom提供商的特殊配置
        if provider == 'custom':
            if not base_url:
                console.print("[red]错误：custom提供商需要指定 --base-url[/red]")
                console.print("示例: smart-tidy config set-provider custom --base-url https://api.example.com/v1 --api-key xxx --model model-name")
                return
            
            if not api_key:
                console.print("[red]错误：custom提供商需要指定 --api-key[/red]")
                return
            
            if not model:
                console.print("[red]错误：custom提供商需要指定 --model[/red]")
                return
            
            # 保存自定义API配置到.env
            env_file = ".env"
            env_content = {}
            if os.path.exists(env_file):
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            k, v = line.strip().split('=', 1)
                            env_content[k] = v
            
            env_content['DEFAULT_AI_PROVIDER'] = 'custom'
            env_content['CUSTOM_API_BASE_URL'] = base_url
            env_content['CUSTOM_API_KEY'] = api_key
            env_content['CUSTOM_API_MODEL'] = model
            
            # 写回.env
            from datetime import datetime
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(f"# Smart File Tidy 配置\n")
                f.write(f"# 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for k, v in env_content.items():
                    f.write(f"{k}={v}\n")
            
            # 同时保存到配置文件
            config.set(f'ai.providers.custom.base_url', base_url)
            config.set(f'ai.providers.custom.api_key', api_key)
            config.set(f'ai.providers.custom.model', model)
            
            console.print(f"[green]✓[/green] 自定义API配置已保存到 .env")
            console.print(f"  地址: {base_url}")
            console.print(f"  模型: {model}")
            console.print(f"  API Key: {api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "")
        
        # 设置API Key（非custom提供商）
        elif api_key:
            # 保存到环境变量文件
            env_file = ".env"
            import os
            if provider == 'claude':
                key_name = 'ANTHROPIC_API_KEY'
            elif provider == 'openai':
                key_name = 'OPENAI_API_KEY'
            else:
                key_name = None
            
            if key_name:
                # 读取现有.env
                env_content = {}
                if os.path.exists(env_file):
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if '=' in line and not line.startswith('#'):
                                k, v = line.strip().split('=', 1)
                                env_content[k] = v
                
                # 更新API Key和提供商
                env_content['DEFAULT_AI_PROVIDER'] = provider
                env_content[key_name] = api_key
                
                # 写回.env
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Smart File Tidy 配置\n")
                    f.write(f"# 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    for k, v in env_content.items():
                        f.write(f"{k}={v}\n")
                
                console.print(f"[green]✓[/green] 配置已保存到 {env_file}")
                console.print(f"  提供商: {provider}")
                console.print(f"  API Key: {api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "")
        
        # 设置base_url（local提供商）
        if provider == 'local' and base_url:
            config.set(f'ai.providers.local.base_url', base_url)
        
        # 设置模型
        if model and provider != 'custom':  # custom已经在上面处理了
            config.set(f'ai.providers.{provider}.model', model)
        
        # 保存到配置文件（作为备份）
        config.save_config()
        
        console.print(f"\n[green]✓[/green] 默认AI提供商已设置为: {provider}")
        console.print(f"\n💡 提示: 配置已保存到 .env 文件")
        console.print(f"   您可以直接编辑 .env 文件来修改配置")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@config_app.command("test")
def test_connection(
    provider: str = typer.Option(None, "--provider", "-p", help="测试指定提供商")
):
    """测试AI提供商连接"""
    try:
        config = ConfigManager()
        provider = provider or config.get_default_provider()
        
        console.print(f"[cyan]测试 {provider} 连接...[/cyan]")
        
        ai_config = config.get_ai_config(provider)
        
        # 检查配置
        if provider in ['claude', 'openai']:
            if not ai_config.get('api_key'):
                console.print(f"[red]错误: API Key未配置[/red]")
                console.print(f"请运行: smart-tidy config set-provider {provider} --api-key YOUR_KEY")
                return
        
        # 尝试创建适配器
        from ..ai import AIAdapterFactory
        adapter = AIAdapterFactory.create_adapter(provider, ai_config)
        
        console.print(f"[green]✓[/green] {provider} 连接成功")
        console.print(f"模型: {ai_config.get('model')}")
    
    except Exception as e:
        console.print(f"[red]✗ 连接失败: {str(e)}[/red]")
