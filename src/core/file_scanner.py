"""文件扫描器"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from ..models import FileInfo
from ..utils import FileMetadataExtractor, PDFReader


class FileScanner:
    """文件扫描器 - 扫描目录并收集文件信息"""
    
    def __init__(self, max_file_size_mb: int = 100, max_depth: int = 5):
        """
        初始化文件扫描器
        
        Args:
            max_file_size_mb: 最大文件大小（MB），超过此大小不读取内容
            max_depth: 最大扫描深度
        """
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.max_depth = max_depth
        self.metadata_extractor = FileMetadataExtractor()
    
    def scan_directory(
        self,
        directory: str,
        recursive: bool = False,
        extensions: Optional[Set[str]] = None,
        include_metadata: bool = True,
        include_content: bool = False
    ) -> List[FileInfo]:
        """
        扫描目录并返回文件信息列表
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描子目录
            extensions: 文件扩展名过滤（如 {'.pdf', '.docx'}）
            include_metadata: 是否提取元数据
            include_content: 是否提取内容样本
            
        Returns:
            文件信息列表
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        if not directory_path.is_dir():
            raise NotADirectoryError(f"不是目录: {directory}")
        
        # 收集所有文件路径
        file_paths = self._collect_file_paths(directory_path, recursive, extensions)
        
        # 并行处理文件信息提取
        files_info = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(
                    self._process_single_file,
                    file_path,
                    include_metadata,
                    include_content
                ): file_path
                for file_path in file_paths
            }
            
            with tqdm(total=len(file_paths), desc="扫描文件") as pbar:
                for future in as_completed(futures):
                    try:
                        file_info = future.result()
                        if file_info:
                            files_info.append(file_info)
                    except Exception as e:
                        file_path = futures[future]
                        print(f"处理文件失败 {file_path}: {e}")
                    finally:
                        pbar.update(1)
        
        return files_info
    
    def _collect_file_paths(
        self,
        directory: Path,
        recursive: bool,
        extensions: Optional[Set[str]]
    ) -> List[str]:
        """收集文件路径"""
        file_paths = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                # 检查深度
                depth = len(Path(root).relative_to(directory).parts)
                if depth > self.max_depth:
                    continue
                
                for file in files:
                    file_path = Path(root) / file
                    if self._should_include_file(file_path, extensions):
                        file_paths.append(str(file_path))
        else:
            for item in directory.iterdir():
                if item.is_file() and self._should_include_file(item, extensions):
                    file_paths.append(str(item))
        
        return file_paths
    
    def _should_include_file(self, file_path: Path, extensions: Optional[Set[str]]) -> bool:
        """判断是否应包含此文件"""
        # 跳过隐藏文件
        if file_path.name.startswith('.'):
            return False
        
        # 扩展名过滤
        if extensions and file_path.suffix.lower() not in extensions:
            return False
        
        return True
    
    def _process_single_file(
        self,
        file_path: str,
        include_metadata: bool,
        include_content: bool
    ) -> Optional[FileInfo]:
        """处理单个文件"""
        try:
            # 创建基础FileInfo
            file_info = FileInfo.from_path(file_path)
            
            # 提取元数据
            if include_metadata:
                file_info.metadata = self.extract_metadata(file_path)
            
            # 提取内容样本
            if include_content and file_info.size < self.max_file_size:
                file_info.content_sample = self.sample_content(file_path)
            
            return file_info
            
        except Exception as e:
            print(f"处理文件失败 {file_path}: {e}")
            return None
    
    def extract_metadata(self, file_path: str) -> Dict:
        """提取文件元数据"""
        return self.metadata_extractor.extract(file_path)
    
    def sample_content(self, file_path: str, max_chars: int = 1000) -> Optional[str]:
        """安全地读取文件内容样本"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        try:
            if ext == '.pdf':
                return PDFReader.extract_text_sample(file_path, max_chars=max_chars)
            elif ext == '.txt':
                return self._read_text_file(file_path, max_chars)
            else:
                # 对于其他文件类型，尝试作为文本读取
                return self._read_text_file(file_path, max_chars)
        except Exception as e:
            return f"[无法读取内容: {str(e)}]"
    
    def _read_text_file(self, file_path: str, max_chars: int) -> str:
        """读取文本文件"""
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read(max_chars)
                    return content
            except UnicodeDecodeError:
                continue
            except Exception:
                break
        
        return "[二进制文件或编码不支持]"
    
    def group_by_extension(self, files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """按扩展名分组文件"""
        groups = {}
        for file in files:
            ext = file.extension or 'no_extension'
            if ext not in groups:
                groups[ext] = []
            groups[ext].append(file)
        return groups
