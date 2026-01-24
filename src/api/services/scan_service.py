"""
扫描服务 - 封装文件扫描功能
"""

import uuid
from typing import Dict, List, Optional, Set
from datetime import datetime

from ...core.file_scanner import FileScanner
from ...models import FileInfo
from ..models.responses import (
    ScanResponse,
    FileInfoResponse,
    ScanStatsResponse,
)


class ScanService:
    """扫描服务"""
    
    def __init__(self):
        self._scan_cache: Dict[str, Dict] = {}
    
    def _file_info_to_response(self, file_info: FileInfo) -> FileInfoResponse:
        """转换 FileInfo 为响应模型"""
        return FileInfoResponse(
            path=file_info.path,
            name=file_info.name,
            extension=file_info.extension,
            size=file_info.size,
            size_human=file_info.size_human,
            created_time=file_info.created_time,
            modified_time=file_info.modified_time,
            metadata=file_info.metadata,
            content_sample=file_info.content_sample,
        )
    
    def _calculate_stats(self, files: List[FileInfo]) -> ScanStatsResponse:
        """计算扫描统计信息"""
        total_size = sum(f.size for f in files)
        
        # 按扩展名统计
        by_extension: Dict[str, int] = {}
        for f in files:
            ext = f.extension.lower() if f.extension else "(无扩展名)"
            by_extension[ext] = by_extension.get(ext, 0) + 1
        
        # 按类型统计
        categories = {
            'document': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt'],
            'spreadsheet': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentation': ['.ppt', '.pptx', '.odp'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            'archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb'],
        }
        
        by_category: Dict[str, int] = {}
        for f in files:
            ext = f.extension.lower()
            categorized = False
            for cat, exts in categories.items():
                if ext in exts:
                    by_category[cat] = by_category.get(cat, 0) + 1
                    categorized = True
                    break
            if not categorized:
                by_category['other'] = by_category.get('other', 0) + 1
        
        # 计算人类可读的总大小
        size = total_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                total_size_human = f"{size:.2f} {unit}"
                break
            size /= 1024.0
        else:
            total_size_human = f"{size:.2f} TB"
        
        return ScanStatsResponse(
            total_size=total_size,
            total_size_human=total_size_human,
            by_extension=by_extension,
            by_category=by_category,
        )
    
    def scan_directory(
        self,
        directory: str,
        recursive: bool = False,
        extensions: Optional[List[str]] = None,
        include_metadata: bool = True,
        include_content: bool = False,
        max_file_size_mb: int = 100,
        max_depth: int = 5,
    ) -> ScanResponse:
        """
        扫描目录
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描
            extensions: 扩展名过滤
            include_metadata: 是否包含元数据
            include_content: 是否包含内容样本
            max_file_size_mb: 最大文件大小限制
            max_depth: 最大扫描深度
        
        Returns:
            扫描响应
        """
        # 创建扫描器
        scanner = FileScanner(
            max_file_size_mb=max_file_size_mb,
            max_depth=max_depth
        )
        
        # 转换扩展名为集合
        ext_set: Optional[Set[str]] = None
        if extensions:
            ext_set = set(ext if ext.startswith('.') else f'.{ext}' for ext in extensions)
        
        # 执行扫描
        files = scanner.scan_directory(
            directory=directory,
            recursive=recursive,
            extensions=ext_set,
            include_metadata=include_metadata,
            include_content=include_content
        )
        
        # 生成扫描ID
        scan_id = str(uuid.uuid4())
        
        # 转换为响应模型
        file_responses = [self._file_info_to_response(f) for f in files]
        stats = self._calculate_stats(files)
        
        # 缓存扫描结果
        self._scan_cache[scan_id] = {
            "directory": directory,
            "files": files,
            "timestamp": datetime.now(),
        }
        
        return ScanResponse(
            scan_id=scan_id,
            directory=directory,
            total_files=len(files),
            files=file_responses,
            stats=stats,
            timestamp=datetime.now(),
        )
    
    def get_scan_result(self, scan_id: str) -> Optional[Dict]:
        """获取缓存的扫描结果"""
        return self._scan_cache.get(scan_id)
    
    def get_scan_files(self, scan_id: str) -> Optional[List[FileInfo]]:
        """获取扫描结果中的文件列表"""
        result = self._scan_cache.get(scan_id)
        if result:
            return result.get("files")
        return None
    
    def delete_scan_result(self, scan_id: str):
        """删除扫描结果缓存"""
        if scan_id in self._scan_cache:
            del self._scan_cache[scan_id]
    
    def cleanup_old_scans(self, max_age_hours: int = 1):
        """清理旧的扫描缓存"""
        now = datetime.now()
        to_delete = []
        for scan_id, data in self._scan_cache.items():
            age = (now - data["timestamp"]).total_seconds() / 3600
            if age > max_age_hours:
                to_delete.append(scan_id)
        
        for scan_id in to_delete:
            self.delete_scan_result(scan_id)


# 全局扫描服务实例
_scan_service: Optional[ScanService] = None


def get_scan_service() -> ScanService:
    """获取扫描服务单例"""
    global _scan_service
    if _scan_service is None:
        _scan_service = ScanService()
    return _scan_service
