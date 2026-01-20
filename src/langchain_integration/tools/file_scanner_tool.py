"""文件扫描工具"""

import json
from typing import Type, Optional
from pathlib import Path
from pydantic import BaseModel, Field

# 尝试从不同位置导入 BaseTool
try:
    from langchain_core.tools import BaseTool
except ImportError:
    from langchain.tools import BaseTool

from ...core.file_scanner import FileScanner


class FileScannerInput(BaseModel):
    """文件扫描工具的输入参数"""
    directory: str = Field(..., description="要扫描的目录路径")
    recursive: bool = Field(default=False, description="是否递归扫描子目录")
    extensions: Optional[str] = Field(
        default=None,
        description="文件扩展名过滤，用逗号分隔，如 '.pdf,.docx'"
    )
    include_content: bool = Field(
        default=True,
        description="是否包含文件内容样本"
    )


class FileScannerTool(BaseTool):
    """文件扫描工具 - 扫描目录并获取文件列表"""
    
    name: str = "file_scanner"
    description: str = """扫描指定目录并获取文件信息列表。
    这个工具可以：
    - 列出目录中的所有文件
    - 提取文件的基本信息（名称、大小、类型、修改时间等）
    - 读取文件内容样本（用于分析）
    - 提取文件元数据
    
    使用场景：
    - 开始文件整理任务时，首先使用此工具扫描目标目录
    - 获取文件列表后，再使用其他工具进行分析和操作
    """
    args_schema: Type[BaseModel] = FileScannerInput
    
    def _run(
        self,
        directory: str,
        recursive: bool = False,
        extensions: Optional[str] = None,
        include_content: bool = True
    ) -> str:
        """执行文件扫描"""
        try:
            # 创建扫描器
            scanner = FileScanner()
            
            # 解析扩展名
            ext_set = None
            if extensions:
                ext_set = {ext.strip() for ext in extensions.split(',')}
            
            # 扫描文件
            files = scanner.scan_directory(
                directory=directory,
                recursive=recursive,
                extensions=ext_set,
                include_metadata=True,
                include_content=include_content
            )
            
            # 转换为简化的字典格式
            files_data = []
            for file in files:
                file_info = {
                    'path': file.path,
                    'name': file.name,
                    'extension': file.extension,
                    'size': file.size,
                    'size_mb': round(file.size / 1024 / 1024, 2),
                    'modified_time': file.modified_time.isoformat() if file.modified_time else None,
                    'metadata': file.metadata,
                }
                
                # 包含内容样本
                if include_content and file.content_sample:
                    file_info['content_sample'] = file.content_sample[:500]  # 限制长度
                
                files_data.append(file_info)
            
            result = {
                'success': True,
                'directory': directory,
                'file_count': len(files_data),
                'files': files_data[:100],  # 限制返回数量，避免token过多
            }
            
            if len(files_data) > 100:
                result['note'] = f"共找到 {len(files_data)} 个文件，仅返回前100个。"
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e),
                'directory': directory
            }, ensure_ascii=False)
    
    async def _arun(self, *args, **kwargs) -> str:
        """异步运行（暂不支持）"""
        raise NotImplementedError("异步扫描暂不支持")
