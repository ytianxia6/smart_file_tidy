"""
API 依赖注入
"""

from functools import lru_cache
from typing import Optional

from ..utils.config import ConfigManager
from ..core.controller import Controller
from ..core.file_scanner import FileScanner
from ..core.file_operator import FileOperator
from ..safety.operation_log import OperationLogger
from ..safety.backup import BackupManager
from ..safety.undo_manager import UndoManager


@lru_cache()
def get_config() -> ConfigManager:
    """获取配置管理器单例"""
    return ConfigManager()


def get_file_scanner(
    max_file_size_mb: int = 100,
    max_depth: int = 5
) -> FileScanner:
    """获取文件扫描器"""
    return FileScanner(
        max_file_size_mb=max_file_size_mb,
        max_depth=max_depth
    )


def get_file_operator(dry_run: bool = False) -> FileOperator:
    """获取文件操作器"""
    return FileOperator(dry_run=dry_run)


def get_operation_logger() -> OperationLogger:
    """获取操作日志器"""
    return OperationLogger()


def get_backup_manager() -> BackupManager:
    """获取备份管理器"""
    return BackupManager()


def get_undo_manager() -> UndoManager:
    """获取撤销管理器"""
    return UndoManager()


def get_controller(
    ai_provider: Optional[str] = None,
    use_agent: bool = True
) -> Controller:
    """获取主控制器"""
    config = get_config()
    return Controller(
        config=config,
        ai_provider=ai_provider,
        use_agent=use_agent
    )
