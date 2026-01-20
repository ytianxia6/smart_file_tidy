"""文件分析工具"""

import json
from typing import Type
from pathlib import Path
from pydantic import BaseModel, Field

# 尝试从不同位置导入 BaseTool
try:
    from langchain_core.tools import BaseTool
except ImportError:
    from langchain.tools import BaseTool

from ...utils.pdf_reader import PDFReader
from ...utils.file_metadata import FileMetadataExtractor


class FileAnalyzerInput(BaseModel):
    """文件分析工具的输入参数"""
    file_path: str = Field(..., description="要分析的文件路径")
    analyze_content: bool = Field(
        default=True,
        description="是否分析文件内容（提取文本、关键词等）"
    )
    check_if_paper: bool = Field(
        default=True,
        description="对于PDF文件，是否检查是否为学术论文"
    )


class FileAnalyzerTool(BaseTool):
    """文件分析工具 - 深度分析单个文件"""
    
    name: str = "file_analyzer"
    description: str = """深度分析指定文件的内容和特征。
    这个工具可以：
    - 识别文件类型（基于扩展名和内容）
    - 提取文件元数据（PDF标题、作者、页数等）
    - 读取和分析文件内容
    - 提取关键信息和模式
    
    使用场景：
    - 对扫描到的文件进行详细分析
    - 提取文件特征用于分类决策
    - 识别文件的实际类型和用途
    """
    args_schema: Type[BaseModel] = FileAnalyzerInput
    
    def _run(
        self,
        file_path: str,
        analyze_content: bool = True,
        check_if_paper: bool = True
    ) -> str:
        """执行文件分析"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return json.dumps({
                    'success': False,
                    'error': '文件不存在',
                    'file_path': file_path
                }, ensure_ascii=False)
            
            # 基本信息
            result = {
                'success': True,
                'file_path': file_path,
                'file_name': path.name,
                'extension': path.suffix.lower(),
                'size_mb': round(path.stat().st_size / 1024 / 1024, 2),
            }
            
            # 创建元数据提取器
            metadata_extractor = FileMetadataExtractor()
            
            # 提取元数据
            metadata = metadata_extractor.extract(file_path)
            result['metadata'] = metadata
            
            # 分析文件类型
            result['file_type_analysis'] = self._analyze_file_type(path)
            
            # 内容分析
            if analyze_content:
                result['content_analysis'] = self._analyze_content(file_path, path.suffix.lower())
            
            # 论文检测（仅针对PDF）
            if check_if_paper and path.suffix.lower() == '.pdf':
                result['paper_check'] = self._check_paper_indicators(file_path)
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e),
                'file_path': file_path
            }, ensure_ascii=False)
    
    def _analyze_file_type(self, path: Path) -> dict:
        """分析文件类型"""
        ext = path.suffix.lower()
        name = path.stem
        
        analysis = {
            'extension': ext,
            'category': self._categorize_by_extension(ext),
        }
        
        # 文件名模式分析
        if ext == '.pdf':
            analysis['filename_pattern'] = PDFReader.analyze_filename_pattern(path.name)
        
        return analysis
    
    def _categorize_by_extension(self, ext: str) -> str:
        """根据扩展名分类"""
        categories = {
            'document': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'],
            'spreadsheet': ['.xls', '.xlsx', '.csv'],
            'presentation': ['.ppt', '.pptx'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'video': ['.mp4', '.avi', '.mov', '.mkv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac'],
            'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs'],
        }
        
        for category, extensions in categories.items():
            if ext in extensions:
                return category
        
        return 'other'
    
    def _analyze_content(self, file_path: str, ext: str) -> dict:
        """分析文件内容"""
        analysis = {}
        
        try:
            if ext == '.pdf':
                # PDF内容分析
                text_sample = PDFReader.extract_text_sample(file_path, max_chars=1000)
                analysis['text_sample'] = text_sample
                analysis['has_chinese'] = self._contains_chinese(text_sample)
                analysis['has_english'] = self._contains_english(text_sample)
                
            elif ext in ['.txt', '.md']:
                # 文本文件分析
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_sample = f.read(1000)
                    analysis['text_sample'] = text_sample
                    analysis['has_chinese'] = self._contains_chinese(text_sample)
                    analysis['has_english'] = self._contains_english(text_sample)
        
        except Exception as e:
            analysis['error'] = f"内容分析失败: {str(e)}"
        
        return analysis
    
    def _contains_chinese(self, text: str) -> bool:
        """检查是否包含中文"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)
    
    def _contains_english(self, text: str) -> bool:
        """检查是否包含英文"""
        return any('a' <= char.lower() <= 'z' for char in text)
    
    def _check_paper_indicators(self, file_path: str) -> dict:
        """检查PDF是否包含学术论文的特征（基于规则）"""
        try:
            # 读取PDF内容
            pdf_reader = PDFReader()
            text_sample = pdf_reader.extract_text_sample(file_path, max_chars=2000)
            
            if not text_sample or len(text_sample) < 100:
                return {
                    'likely_paper': False,
                    'confidence': 0.0,
                    'reason': 'PDF内容为空或太短'
                }
            
            # 检查学术论文特征
            indicators = {
                'abstract': any(keyword in text_sample.lower() for keyword in ['abstract', '摘要']),
                'introduction': any(keyword in text_sample.lower() for keyword in ['introduction', '引言', '前言']),
                'references': any(keyword in text_sample.lower() for keyword in ['references', '参考文献']),
                'conclusion': any(keyword in text_sample.lower() for keyword in ['conclusion', '结论']),
                'keywords': any(keyword in text_sample.lower() for keyword in ['keywords', '关键词']),
                'doi': 'doi:' in text_sample.lower() or 'doi.org' in text_sample.lower(),
                'arxiv': 'arxiv' in text_sample.lower(),
                'journal': any(keyword in text_sample.lower() for keyword in ['journal', 'conference', 'proceedings', '期刊']),
            }
            
            # 计算得分
            indicator_count = sum(indicators.values())
            confidence = min(indicator_count / 5.0, 1.0)  # 最多5个指标，归一化到0-1
            
            # 判断是否为论文
            likely_paper = indicator_count >= 3  # 至少3个指标
            
            return {
                'likely_paper': likely_paper,
                'confidence': round(confidence, 2),
                'indicator_count': indicator_count,
                'indicators_found': indicators,
                'recommendation': '建议移动到论文文件夹' if likely_paper else '可能不是学术论文'
            }
            
        except Exception as e:
            return {
                'likely_paper': False,
                'confidence': 0.0,
                'error': f'论文检测失败: {str(e)}'
            }
    
    async def _arun(self, *args, **kwargs) -> str:
        """异步运行（暂不支持）"""
        raise NotImplementedError("异步分析暂不支持")
