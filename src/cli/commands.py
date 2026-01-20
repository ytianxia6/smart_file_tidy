"""CLI命令实现"""

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.markdown import Markdown

from ..utils import ConfigManager
from ..core import Controller
from ..models import Operation

console = Console()


def organize_command(
    directory: str,
    request: str,
    recursive: bool,
    dry_run: bool,
    provider: Optional[str],
    batch_size: int,
    create_backup: bool
):
    """整理文件命令"""
    try:
        # 验证目录
        dir_path = Path(directory)
        if not dir_path.exists():
            console.print(f"[red]错误：目录不存在 {directory}[/red]")
            return
        
        # 初始化
        config = ConfigManager()
        if batch_size:
            config.set('file_operations.batch_size', batch_size)
        
        controller = Controller(config, ai_provider=provider)
        
        if dry_run:
            controller.file_operator.dry_run = True
        
        # 扫描文件
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("扫描目录...", total=None)
            files = controller.scan_directory(directory, recursive=recursive)
        
        console.print(f"[green]✓[/green] 扫描完成，发现 [bold]{len(files)}[/bold] 个文件\n")
        
        if len(files) == 0:
            console.print("[yellow]没有找到文件[/yellow]")
            return
        
        # 生成方案
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("AI正在分析...", total=None)
            operations = controller.generate_plan(files, request)
        
        if len(operations) == 0:
            console.print("[yellow]没有需要执行的操作[/yellow]")
            return
        
        # 显示预览
        console.print(f"\n[bold cyan]操作预览：[/bold cyan]")
        display_operations_table(operations)
        
        # 验证操作
        preview = controller.preview_operations(operations)
        if preview.get('warnings'):
            console.print("\n[yellow]警告：[/yellow]")
            for warning in preview['warnings']:
                console.print(f"  • {warning}")
        
        if preview.get('has_errors'):
            console.print("\n[red]错误：[/red]")
            for error in preview['errors']:
                console.print(f"  • {error}")
            return
        
        # 确认执行
        if not dry_run:
            if not Confirm.ask("\n是否执行以上操作？"):
                console.print("[yellow]已取消[/yellow]")
                return
            
            # 执行操作
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task("执行操作...", total=None)
                result = controller.execute_operations(operations, create_backup)
            
            # 显示结果
            console.print(f"\n[green]✓ 完成！[/green]")
            console.print(f"  成功: {result.success_count}")
            console.print(f"  失败: {result.failed_count}")
            console.print(f"  跳过: {result.skipped_count}")
            console.print(f"  用时: {result.duration:.2f}秒")
            
            if result.errors:
                console.print("\n[red]错误信息：[/red]")
                for error in result.errors:
                    console.print(f"  • {error}")
        else:
            console.print("\n[yellow]预览模式 - 未实际执行[/yellow]")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


def interactive_command(
    directory: str,
    recursive: bool,
    provider: Optional[str]
):
    """交互式整理模式"""
    try:
        # 验证目录
        dir_path = Path(directory)
        if not dir_path.exists():
            console.print(f"[red]错误：目录不存在 {directory}[/red]")
            return
        
        # 初始化
        config = ConfigManager()
        controller = Controller(config, ai_provider=provider)
        
        # 扫描文件
        console.print(f"[cyan]开始扫描目录:[/cyan] {directory}\n")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("扫描中...", total=None)
            files = controller.scan_directory(directory, recursive=recursive)
        
        console.print(f"[green]✓[/green] 发现 [bold]{len(files)}[/bold] 个文件\n")
        
        if len(files) == 0:
            console.print("[yellow]没有找到文件[/yellow]")
            return
        
        # 交互式循环
        console.print("[bold cyan]交互式整理模式[/bold cyan]")
        console.print("输入整理需求，输入 'q' 或 'quit' 退出\n")
        
        while True:
            # 获取用户需求
            request = Prompt.ask("[bold]请描述您的整理需求[/bold]")
            
            if request.lower() in ['q', 'quit', 'exit']:
                console.print("[yellow]退出[/yellow]")
                break
            
            if not request.strip():
                continue
            
            try:
                # 生成方案
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    progress.add_task("AI正在分析...", total=None)
                    operations = controller.generate_plan(files, request)
                
                if len(operations) == 0:
                    console.print("[yellow]没有需要执行的操作[/yellow]\n")
                    continue
                
                # 显示预览
                console.print(f"\n[bold cyan]操作预览：[/bold cyan]")
                display_operations_table(operations[:20])  # 最多显示20条
                
                if len(operations) > 20:
                    console.print(f"... 还有 {len(operations) - 20} 个操作未显示")
                
                # 询问操作
                action = Prompt.ask(
                    "\n选择操作",
                    choices=["y", "n", "edit", "q"],
                    default="n"
                )
                
                if action == 'y':
                    # 执行操作
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        progress.add_task("执行中...", total=None)
                        result = controller.execute_operations(operations)
                    
                    console.print(f"\n[green]✓ 完成！[/green] 移动了 {result.success_count} 个文件")
                    
                    # 更新文件列表
                    files = controller.scan_directory(directory, recursive=recursive)
                    
                    # 收集反馈
                    feedback = Prompt.ask(
                        "\n操作结果满意吗？有需要调整的吗？",
                        default=""
                    )
                    
                    if feedback:
                        controller.add_feedback(feedback)
                        # 继续下一轮，使用反馈优化
                        console.print("[cyan]正在根据反馈优化...[/cyan]\n")
                
                elif action == 'q':
                    break
                else:
                    console.print("[yellow]已取消[/yellow]\n")
            
            except Exception as e:
                console.print(f"[red]错误: {str(e)}[/red]\n")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


def undo_command(confirm: bool):
    """撤销命令"""
    try:
        config = ConfigManager()
        controller = Controller(config)
        
        if not controller.undo_manager.can_undo():
            console.print("[yellow]没有可撤销的操作[/yellow]")
            return
        
        # 显示可撤销的操作
        history = controller.undo_manager.get_undo_history()
        if history:
            last_op = history[-1]
            console.print(f"最后一次操作: {last_op['timestamp']}")
            console.print(f"操作数量: {last_op['operation_count']}")
        
        # 确认
        if not confirm:
            if not Confirm.ask("\n确定要撤销最后一次操作吗？"):
                console.print("[yellow]已取消[/yellow]")
                return
        
        # 执行撤销
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("撤销中...", total=None)
            success = controller.undo_last_operation()
        
        if success:
            console.print("[green]✓ 撤销成功[/green]")
        else:
            console.print("[red]✗ 撤销失败[/red]")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


def history_command(limit: int):
    """历史命令"""
    try:
        config = ConfigManager()
        controller = Controller(config)
        
        operations = controller.get_operation_history(limit)
        
        if not operations:
            console.print("[yellow]没有操作历史[/yellow]")
            return
        
        # 显示历史记录
        table = Table(title=f"最近 {len(operations)} 条操作记录")
        table.add_column("时间", style="cyan")
        table.add_column("类型", style="magenta")
        table.add_column("源文件", style="green")
        table.add_column("目标", style="yellow")
        table.add_column("状态", style="blue")
        
        for op in operations:
            status_color = {
                'success': '[green]成功[/green]',
                'failed': '[red]失败[/red]',
                'pending': '[yellow]待执行[/yellow]',
            }.get(op['status'], op['status'])
            
            table.add_row(
                op['timestamp'][:19],
                op['type'],
                Path(op['source']).name if op['source'] else '-',
                Path(op['target']).name if op['target'] else '-',
                status_color
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


def display_operations_table(operations: list):
    """显示操作表格"""
    table = Table()
    table.add_column("序号", style="cyan", width=6)
    table.add_column("操作", style="magenta", width=10)
    table.add_column("文件", style="green")
    table.add_column("目标", style="yellow")
    table.add_column("原因", style="blue", max_width=40)
    
    for i, op in enumerate(operations, 1):
        source_name = Path(op.source).name if hasattr(op, 'source') else str(op.get('file', ''))
        target_name = Path(op.target).name if hasattr(op, 'target') else str(op.get('target', ''))
        reason = (op.reason if hasattr(op, 'reason') else op.get('reason', ''))[:40]
        op_type = op.type.value if hasattr(op.type, 'value') else str(op.get('type', ''))
        
        table.add_row(
            str(i),
            op_type,
            source_name,
            target_name,
            reason
        )
    
    console.print(table)


def organize_agent_command(
    directory: str,
    request: str,
    provider: Optional[str],
    dry_run: bool
):
    """使用Agent模式整理文件"""
    try:
        # 验证目录
        dir_path = Path(directory)
        if not dir_path.exists():
            console.print(f"[red]错误：目录不存在 {directory}[/red]")
            return
        
        # 初始化Controller（使用Agent模式）
        config = ConfigManager()
        
        # 如果是dry_run模式，设置配置
        if dry_run:
            config.set('langchain.tools.file_operator.dry_run', True)
        
        controller = Controller(config, ai_provider=provider, use_agent=True)
        
        if not controller.use_agent:
            console.print("[red]错误：Agent模式初始化失败，请检查LangChain依赖是否已安装[/red]")
            return
        
        console.print(f"[cyan]使用AI Provider: {provider or config.get_default_provider()}[/cyan]")
        console.print(f"[cyan]目标目录: {directory}[/cyan]")
        console.print(f"[cyan]用户需求: {request}[/cyan]\n")
        
        if dry_run:
            console.print("[yellow]⚠ DRY RUN 模式：仅模拟操作，不会实际修改文件[/yellow]\n")
        
        # 确认执行
        if not Confirm.ask("是否开始执行？"):
            console.print("[yellow]已取消[/yellow]")
            return
        
        # 执行整理
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Agent正在工作中...", total=None)
            result = controller.organize_with_agent(directory, request)
        
        # 显示结果
        if result.get('success'):
            console.print("\n[green]✓ 整理完成！[/green]\n")
            
            # 显示Agent的输出
            output = result.get('output', '')
            if output:
                console.print("[bold cyan]Agent报告：[/bold cyan]")
                console.print(Markdown(output))
            
            # 显示中间步骤（如果有）
            if result.get('intermediate_steps'):
                console.print("\n[dim]执行步骤数：{}[/dim]".format(len(result['intermediate_steps'])))
        else:
            console.print(f"\n[red]✗ 整理失败：{result.get('error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]错误：{e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def suggest_command(directory: str, provider: Optional[str]):
    """分析目录并提供整理建议"""
    try:
        # 验证目录
        dir_path = Path(directory)
        if not dir_path.exists():
            console.print(f"[red]错误：目录不存在 {directory}[/red]")
            return
        
        # 初始化Controller（使用Agent模式）
        config = ConfigManager()
        controller = Controller(config, ai_provider=provider, use_agent=True)
        
        if not controller.use_agent:
            console.print("[red]错误：Agent模式未启用[/red]")
            return
        
        console.print(f"[cyan]正在分析目录: {directory}[/cyan]\n")
        
        # 获取建议
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("AI正在分析...", total=None)
            result = controller.suggest_organization_with_agent(directory)
        
        # 显示建议
        if result.get('success'):
            console.print("\n[green]✓ 分析完成！[/green]\n")
            console.print("[bold cyan]整理建议：[/bold cyan]")
            console.print(Markdown(result.get('suggestions', '')))
        else:
            console.print(f"\n[red]✗ 分析失败：{result.get('error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]错误：{e}[/red]")


def analyze_file_command(file_path: str, provider: Optional[str]):
    """分析单个文件"""
    try:
        # 验证文件
        path = Path(file_path)
        if not path.exists():
            console.print(f"[red]错误：文件不存在 {file_path}[/red]")
            return
        
        # 初始化Controller（使用Agent模式）
        config = ConfigManager()
        controller = Controller(config, ai_provider=provider, use_agent=True)
        
        if not controller.use_agent:
            console.print("[red]错误：Agent模式未启用[/red]")
            return
        
        console.print(f"[cyan]正在分析文件: {file_path}[/cyan]\n")
        
        # 分析文件
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("AI正在分析...", total=None)
            result = controller.analyze_file_with_agent(file_path)
        
        # 显示结果
        if result.get('success', True):
            console.print("\n[green]✓ 分析完成！[/green]\n")
            
            # 基本信息
            table = Table(title="文件信息")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            table.add_row("文件名", result.get('file_name', ''))
            table.add_row("类型", result.get('extension', ''))
            table.add_row("大小", f"{result.get('size_mb', 0)} MB")
            
            console.print(table)
            
            # 内容分析
            if 'content_analysis' in result and result['content_analysis'].get('success'):
                console.print("\n[bold cyan]内容分析：[/bold cyan]")
                console.print(result['content_analysis'].get('analysis', ''))
        else:
            console.print(f"\n[red]✗ 分析失败：{result.get('error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]错误：{e}[/red]")


def chat_command(provider: Optional[str]):
    """与Agent交互式对话"""
    try:
        # 初始化Controller（使用Agent模式）
        config = ConfigManager()
        controller = Controller(config, ai_provider=provider, use_agent=True)
        
        if not controller.use_agent:
            console.print("[red]错误：Agent模式未启用[/red]")
            return
        
        console.print("[bold cyan]文件整理助手 - 交互模式[/bold cyan]")
        console.print("输入您的需求，Agent将帮助您整理文件。")
        console.print("输入 'quit' 或 'exit' 退出。\n")
        
        while True:
            try:
                message = Prompt.ask("[cyan]您[/cyan]")
                
                if message.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]再见！[/yellow]")
                    break
                
                if not message.strip():
                    continue
                
                # 与Agent对话
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    progress.add_task("Agent正在思考...", total=None)
                    response = controller.chat_with_agent(message)
                
                console.print(f"\n[green]Agent[/green]: {response}\n")
            
            except KeyboardInterrupt:
                console.print("\n[yellow]再见！[/yellow]")
                break
    
    except Exception as e:
        console.print(f"[red]错误：{e}[/red]")
