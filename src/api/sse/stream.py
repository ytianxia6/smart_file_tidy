"""
SSE 流式响应工具
"""

import asyncio
import json
from typing import AsyncGenerator, Any, Dict, Optional
from datetime import datetime


async def create_sse_message(
    data: Dict[str, Any],
    event: Optional[str] = None,
    retry: Optional[int] = None,
) -> str:
    """
    创建 SSE 消息
    
    Args:
        data: 消息数据
        event: 事件类型
        retry: 重试间隔（毫秒）
    
    Returns:
        格式化的 SSE 消息字符串
    """
    message = ""
    
    if event:
        message += f"event: {event}\n"
    
    if retry:
        message += f"retry: {retry}\n"
    
    # 确保 JSON 是单行的
    json_data = json.dumps(data, ensure_ascii=False, default=str)
    message += f"data: {json_data}\n\n"
    
    return message


async def heartbeat_generator(
    interval: float = 30.0,
) -> AsyncGenerator[str, None]:
    """
    心跳生成器
    
    Args:
        interval: 心跳间隔（秒）
    
    Yields:
        心跳消息
    """
    while True:
        await asyncio.sleep(interval)
        yield ": heartbeat\n\n"


class SSEManager:
    """SSE 连接管理器"""
    
    def __init__(self):
        self._connections: Dict[str, asyncio.Queue] = {}
    
    def create_connection(self, connection_id: str) -> asyncio.Queue:
        """创建新连接"""
        queue = asyncio.Queue()
        self._connections[connection_id] = queue
        return queue
    
    def get_connection(self, connection_id: str) -> Optional[asyncio.Queue]:
        """获取连接"""
        return self._connections.get(connection_id)
    
    def remove_connection(self, connection_id: str):
        """移除连接"""
        if connection_id in self._connections:
            del self._connections[connection_id]
    
    async def send(self, connection_id: str, data: Dict[str, Any]):
        """发送消息到指定连接"""
        queue = self._connections.get(connection_id)
        if queue:
            await queue.put(data)
    
    async def broadcast(self, data: Dict[str, Any]):
        """广播消息到所有连接"""
        for queue in self._connections.values():
            try:
                await queue.put(data)
            except Exception:
                pass


class ProgressReporter:
    """进度报告器"""
    
    def __init__(self, total: int, queue: asyncio.Queue):
        self.total = total
        self.current = 0
        self.queue = queue
        self.start_time = datetime.now()
    
    async def report(
        self,
        current: Optional[int] = None,
        message: Optional[str] = None,
        current_item: Optional[str] = None,
    ):
        """报告进度"""
        if current is not None:
            self.current = current
        else:
            self.current += 1
        
        progress = int((self.current / self.total) * 100) if self.total > 0 else 0
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        data = {
            "type": "progress",
            "progress": progress,
            "current": self.current,
            "total": self.total,
            "elapsed": elapsed,
        }
        
        if message:
            data["message"] = message
        
        if current_item:
            data["current_item"] = current_item
        
        await self.queue.put(data)
    
    async def complete(self, result: Any = None):
        """报告完成"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        data = {
            "type": "complete",
            "progress": 100,
            "current": self.total,
            "total": self.total,
            "elapsed": elapsed,
        }
        
        if result is not None:
            data["result"] = result
        
        await self.queue.put(data)
    
    async def error(self, error: str):
        """报告错误"""
        data = {
            "type": "error",
            "error": error,
            "current": self.current,
            "total": self.total,
        }
        
        await self.queue.put(data)


# 全局 SSE 管理器
sse_manager = SSEManager()


def get_sse_manager() -> SSEManager:
    """获取 SSE 管理器"""
    return sse_manager
