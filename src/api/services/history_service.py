"""
历史服务 - 封装操作历史和撤销功能
"""

from typing import List, Optional
from datetime import datetime

from ...safety.operation_log import OperationLogger
from ...safety.undo_manager import UndoManager
from ...safety.backup import BackupManager
from ..models.responses import (
    HistoryResponse,
    HistoryItemResponse,
    BackupResponse,
    BackupPointResponse,
)


class HistoryService:
    """历史服务"""
    
    def __init__(self):
        self._logger = OperationLogger()
        self._undo_manager = UndoManager()
        self._backup_manager = BackupManager()
    
    def get_operation_history(
        self,
        limit: int = 20,
        page: int = 1,
    ) -> HistoryResponse:
        """
        获取操作历史
        
        Args:
            limit: 每页数量
            page: 页码
        
        Returns:
            历史记录响应
        """
        # 获取最近的操作
        all_operations = self._logger.get_recent_operations(limit=limit * page)
        
        # 分页
        start = (page - 1) * limit
        end = start + limit
        page_operations = all_operations[start:end]
        
        # 转换为响应模型
        items = []
        for op in page_operations:
            items.append(HistoryItemResponse(
                id=op.get('operation_id', ''),
                type=op.get('type', ''),
                source=op.get('source', ''),
                target=op.get('target', ''),
                reason=op.get('reason', ''),
                status=op.get('status', 'unknown'),
                timestamp=datetime.fromisoformat(op.get('timestamp', datetime.now().isoformat())),
                error=op.get('error'),
            ))
        
        return HistoryResponse(
            operations=items,
            total=len(all_operations),
            page=page,
            page_size=limit,
            can_undo=self._undo_manager.can_undo(),
        )
    
    def undo_last_operation(self) -> bool:
        """
        撤销最后一次操作
        
        Returns:
            是否成功
        """
        return self._undo_manager.undo_last()
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return self._undo_manager.can_undo()
    
    def get_undo_history(self) -> List[dict]:
        """获取撤销历史"""
        return self._undo_manager.get_undo_history()
    
    def list_backups(self) -> BackupResponse:
        """
        列出备份点
        
        Returns:
            备份列表响应
        """
        backups = self._backup_manager.list_backups()
        
        items = []
        for backup in backups:
            items.append(BackupPointResponse(
                backup_id=backup.get('backup_id', ''),
                timestamp=datetime.fromisoformat(backup.get('timestamp', datetime.now().isoformat())),
                file_count=backup.get('file_count', 0),
                description=backup.get('description'),
            ))
        
        return BackupResponse(
            backups=items,
            total=len(items),
        )
    
    def create_backup(self, file_paths: List[str]) -> str:
        """
        创建备份点
        
        Args:
            file_paths: 要备份的文件路径列表
        
        Returns:
            备份ID
        """
        return self._backup_manager.create_backup_point(file_paths)
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        恢复备份
        
        Args:
            backup_id: 备份ID
        
        Returns:
            是否成功
        """
        return self._backup_manager.restore_backup(backup_id)
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        删除备份
        
        Args:
            backup_id: 备份ID
        
        Returns:
            是否成功
        """
        return self._backup_manager.delete_backup(backup_id)


# 全局服务实例
_history_service: Optional[HistoryService] = None


def get_history_service() -> HistoryService:
    """获取历史服务单例"""
    global _history_service
    if _history_service is None:
        _history_service = HistoryService()
    return _history_service
