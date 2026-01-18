"""文件元数据提取器"""

import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import PyPDF2


class FileMetadataExtractor:
    """文件元数据提取器"""
    
    @staticmethod
    def extract(file_path: str) -> Dict[str, Any]:
        """提取文件元数据"""
        path = Path(file_path)
        metadata = {
            'mime_type': mimetypes.guess_type(file_path)[0],
        }
        
        ext = path.suffix.lower()
        
        try:
            if ext == '.pdf':
                metadata.update(FileMetadataExtractor._extract_pdf_metadata(file_path))
            elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                metadata.update(FileMetadataExtractor._extract_image_metadata(file_path))
        except Exception as e:
            metadata['extraction_error'] = str(e)
        
        return metadata
    
    @staticmethod
    def _extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
        """提取PDF元数据"""
        metadata = {}
        
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                metadata['page_count'] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    info = pdf_reader.metadata
                    if info.title:
                        metadata['title'] = info.title
                    if info.author:
                        metadata['author'] = info.author
                    if info.subject:
                        metadata['subject'] = info.subject
                    if info.creator:
                        metadata['creator'] = info.creator
                    if info.producer:
                        metadata['producer'] = info.producer
        except Exception as e:
            metadata['error'] = f"PDF元数据提取失败: {str(e)}"
        
        return metadata
    
    @staticmethod
    def _extract_image_metadata(file_path: str) -> Dict[str, Any]:
        """提取图片元数据"""
        metadata = {}
        
        try:
            with Image.open(file_path) as img:
                metadata['width'] = img.width
                metadata['height'] = img.height
                metadata['format'] = img.format
                metadata['mode'] = img.mode
                
                # 提取EXIF信息
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    if exif:
                        metadata['exif'] = {k: v for k, v in exif.items() if isinstance(v, (str, int, float))}
        except Exception as e:
            metadata['error'] = f"图片元数据提取失败: {str(e)}"
        
        return metadata
