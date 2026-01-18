"""操作记录模型"""

from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


class OperationType(str, Enum):
    """操作类型枚举"""
    MOVE = "move"
    RENAME = "rename"
    CREATE_FOLDER = "create_folder"
    DELETE = "delete"


class Operation(BaseModel):
    """单个文件操作"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="操作ID")
    type: OperationType = Field(description="操作类型")
    source: str = Field(description="源路径")
    target: str = Field(description="目标路径")
    reason: str = Field(default="", description="操作原因")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="置信度")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    
    def __str__(self) -> str:
        return f"Operation({self.type.value}: {self.source} -> {self.target})"


class OperationResult(BaseModel):
    """批量操作结果"""
    
    total: int = Field(description="总操作数")
    success_count: int = Field(default=0, description="成功数量")
    failed_count: int = Field(default=0, description="失败数量")
    skipped_count: int = Field(default=0, description="跳过数量")
    operations: List[Operation] = Field(default_factory=list, description="操作列表")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    duration: float = Field(default=0.0, description="执行时长（秒）")
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total == 0:
            return 0.0
        return self.success_count / self.total
    
    def __str__(self) -> str:
        return (f"OperationResult(total={self.total}, success={self.success_count}, "
                f"failed={self.failed_count}, rate={self.success_rate:.1%})")
