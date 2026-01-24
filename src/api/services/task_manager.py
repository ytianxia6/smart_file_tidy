"""
任务管理器 - 管理异步任务状态
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional, List, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from threading import Lock


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    status: TaskStatus
    progress: int = 0
    current_file: Optional[str] = None
    message: Optional[str] = None
    operations: Optional[List[Any]] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_file": self.current_file,
            "message": self.message,
            "operations": self.operations,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class TaskManager:
    """任务管理器单例"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._tasks: Dict[str, TaskInfo] = {}
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._initialized = True
    
    def create_task(self, operations: Optional[List[Any]] = None) -> str:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = TaskInfo(
            task_id=task_id,
            status=TaskStatus.PENDING,
            operations=operations
        )
        return task_id
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务信息"""
        return self._tasks.get(task_id)
    
    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        current_file: Optional[str] = None,
        message: Optional[str] = None,
        result: Optional[Any] = None,
        error: Optional[str] = None
    ):
        """更新任务状态"""
        task = self._tasks.get(task_id)
        if not task:
            return
        
        if status is not None:
            task.status = status
        if progress is not None:
            task.progress = progress
        if current_file is not None:
            task.current_file = current_file
        if message is not None:
            task.message = message
        if result is not None:
            task.result = result
        if error is not None:
            task.error = error
        
        task.updated_at = datetime.now()
        
        # 通知订阅者
        asyncio.create_task(self._notify_subscribers(task_id, task))
    
    async def _notify_subscribers(self, task_id: str, task: TaskInfo):
        """通知任务订阅者"""
        if task_id in self._subscribers:
            for queue in self._subscribers[task_id]:
                try:
                    await queue.put(task.to_dict())
                except Exception:
                    pass
    
    def subscribe(self, task_id: str) -> asyncio.Queue:
        """订阅任务更新"""
        if task_id not in self._subscribers:
            self._subscribers[task_id] = []
        queue = asyncio.Queue()
        self._subscribers[task_id].append(queue)
        return queue
    
    def unsubscribe(self, task_id: str, queue: asyncio.Queue):
        """取消订阅"""
        if task_id in self._subscribers:
            try:
                self._subscribers[task_id].remove(queue)
            except ValueError:
                pass
    
    def delete_task(self, task_id: str):
        """删除任务"""
        if task_id in self._tasks:
            del self._tasks[task_id]
        if task_id in self._subscribers:
            del self._subscribers[task_id]
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[TaskInfo]:
        """列出任务"""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        now = datetime.now()
        to_delete = []
        for task_id, task in self._tasks.items():
            age = (now - task.created_at).total_seconds() / 3600
            if age > max_age_hours and task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                to_delete.append(task_id)
        
        for task_id in to_delete:
            self.delete_task(task_id)


# 全局任务管理器实例
task_manager = TaskManager()


def get_task_manager() -> TaskManager:
    """获取任务管理器"""
    return task_manager
