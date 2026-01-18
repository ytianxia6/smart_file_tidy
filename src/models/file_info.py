"""文件信息模型"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """文件信息数据模型"""
    
    path: str = Field(description="文件完整路径")
    name: str = Field(description="文件名（含扩展名）")
    extension: str = Field(description="文件扩展名")
    size: int = Field(description="文件大小（字节）")
    created_time: datetime = Field(description="创建时间")
    modified_time: datetime = Field(description="修改时间")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="文件元数据")
    content_sample: Optional[str] = Field(default=None, description="内容样本")
    
    @property
    def size_human(self) -> str:
        """人类可读的文件大小"""
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    @classmethod
    def from_path(cls, file_path: str) -> "FileInfo":
        """从文件路径创建FileInfo对象"""
        path = Path(file_path)
        stat = path.stat()
        
        return cls(
            path=str(path.absolute()),
            name=path.name,
            extension=path.suffix.lower(),
            size=stat.st_size,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime)
        )
    
    def __str__(self) -> str:
        return f"FileInfo(name={self.name}, size={self.size_human}, ext={self.extension})"
