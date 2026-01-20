"""CLI主入口"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

from ..utils import ConfigManager
from ..core import Controller
from .commands import (
    organize_command,
    interactive_command,
    undo_command,
    history_command,
    organize_agent_command,
    suggest_command,
    analyze_file_command,
    chat_command
)
from .config_commands import config_app

# 创建主应用
app = typer.Typer(
    name="smart-tidy",
    help="智能文件整理助手 - 基于AI的文件分类和整理工具",
    add_completion=False
)

# 添加config子命令
app.add_typer(config_app, name="config", help="配置管理")

console = Console()


@app.command("organize")
def organize(
    directory: str = typer.Argument(..., help="要整理的目录路径"),
    request: str = typer.Option(..., "--request", "-r", help="整理需求描述"),
    recursive: bool = typer.Option(False, "--recursive", help="递归扫描子目录"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅预览，不实际执行"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI提供商 (claude/openai/local)"),
    batch_size: int = typer.Option(50, "--batch-size", help="批次大小"),
    no_backup: bool = typer.Option(False, "--no-backup", help="不创建备份"),
):
    """整理文件（单次执行）"""
    organize_command(
        directory=directory,
        request=request,
        recursive=recursive,
        dry_run=dry_run,
        provider=provider,
        batch_size=batch_size,
        create_backup=not no_backup
    )


@app.command("interactive")
def interactive(
    directory: str = typer.Argument(..., help="要整理的目录路径"),
    recursive: bool = typer.Option(False, "--recursive", help="递归扫描子目录"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI提供商 (claude/openai/local)"),
):
    """交互式整理模式"""
    interactive_command(
        directory=directory,
        recursive=recursive,
        provider=provider
    )


@app.command("undo")
def undo(
    confirm: bool = typer.Option(False, "--yes", "-y", help="跳过确认")
):
    """撤销最后一次操作"""
    undo_command(confirm=confirm)


@app.command("history")
def history(
    limit: int = typer.Option(10, "--limit", "-n", help="显示的记录数量")
):
    """查看操作历史"""
    history_command(limit=limit)


@app.command("agent")
def agent_organize(
    directory: str = typer.Argument(..., help="要整理的目录路径"),
    request: str = typer.Option(..., "--request", "-r", help="整理需求描述"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI提供商 (claude/openai/custom/local)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅模拟，不实际执行"),
):
    """使用Agent模式智能整理文件（推荐）"""
    organize_agent_command(
        directory=directory,
        request=request,
        provider=provider,
        dry_run=dry_run
    )


@app.command("suggest")
def suggest(
    directory: str = typer.Argument(..., help="要分析的目录路径"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI提供商"),
):
    """分析目录并提供整理建议"""
    suggest_command(directory=directory, provider=provider)


@app.command("analyze")
def analyze(
    file_path: str = typer.Argument(..., help="要分析的文件路径"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI提供商"),
):
    """深度分析单个文件"""
    analyze_file_command(file_path=file_path, provider=provider)


@app.command("chat")
def chat(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="AI提供商"),
):
    """与AI助手交互式对话"""
    chat_command(provider=provider)


@app.command("version")
def version():
    """显示版本信息"""
    from .. import __version__
    console.print(f"[bold green]smart-tidy[/bold green] version {__version__}")


if __name__ == "__main__":
    app()
