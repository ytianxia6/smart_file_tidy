"""内容分析器 - 基于LLM的文件内容深度分析"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import re
from langchain_core.language_models.base import BaseLanguageModel

from ..utils.pdf_reader import PDFReader
from ..utils.file_metadata import FileMetadataExtractor
from .prompts import CONTENT_ANALYSIS_PROMPT, PAPER_IDENTIFICATION_PROMPT


class ContentAnalyzer:
    """基于LLM的文件内容分析器"""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        初始化内容分析器
        
        Args:
            llm: LangChain LLM实例
        """
        self.llm = llm
        self.metadata_extractor = FileMetadataExtractor()
        self.pdf_reader = PDFReader()
    
    def analyze_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        分析文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析结果字典
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                'success': False,
                'error': '文件不存在'
            }
        
        # 提取基本信息
        result = {
            'file_path': file_path,
            'file_name': path.name,
            'extension': path.suffix.lower(),
            'size_mb': round(path.stat().st_size / 1024 / 1024, 2),
        }
        
        # 提取元数据
        result['metadata'] = self.metadata_extractor.extract(file_path)
        
        # 读取内容
        content = self._read_file_content(file_path, path.suffix.lower())
        
        if content and len(content) > 50:
            # 使用LLM分析内容
            result['content_analysis'] = self._analyze_with_llm(
                filename=path.name,
                file_type=path.suffix.lower(),
                content=content
            )
        else:
            result['content_analysis'] = {
                'note': '内容太少或无法读取，跳过LLM分析'
            }
        
        return result
    
    def _read_file_content(self, file_path: str, ext: str, max_chars: int = 2000) -> Optional[str]:
        """读取文件内容"""
        try:
            if ext == '.pdf':
                return self.pdf_reader.extract_text_sample(file_path, max_chars=max_chars)
            elif ext in ['.txt', '.md', '.py', '.js', '.java', '.cpp', '.c', '.go', '.rs']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(max_chars)
            else:
                # 尝试作为文本读取
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(max_chars)
        except Exception as e:
            return f"[无法读取内容: {str(e)}]"
    
    def _analyze_with_llm(self, filename: str, file_type: str, content: str) -> Dict[str, Any]:
        """使用LLM分析内容"""
        try:
            # 直接构建 prompt
            prompt = CONTENT_ANALYSIS_PROMPT.format(
                filename=filename,
                file_type=file_type,
                content=content[:1500]  # 限制内容长度
            )
            
            # 直接调用 LLM
            response = self.llm.invoke(prompt)
            
            # 提取响应内容
            if hasattr(response, 'content'):
                analysis_text = response.content
            else:
                analysis_text = str(response)
            
            return {
                'success': True,
                'analysis': analysis_text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"LLM分析失败: {str(e)}"
            }
    
    def classify_content(self, content: str, categories: List[str]) -> str:
        """
        将内容分类到指定类别
        
        Args:
            content: 文件内容
            categories: 候选类别列表
            
        Returns:
            最匹配的类别
        """
        try:
            prompt = f"""请将以下内容分类到最合适的类别中。

内容：
{content[:1000]}

候选类别：
{', '.join(categories)}

请直接输出最合适的类别名称（只输出类别名，不要其他内容）。
"""
            
            response = self.llm.invoke(prompt)
            
            # 提取响应内容
            if hasattr(response, 'content'):
                category = response.content.strip()
            else:
                category = str(response).strip()
            
            # 验证类别是否在候选列表中
            if category in categories:
                return category
            
            # 尝试模糊匹配
            for cat in categories:
                if cat.lower() in category.lower() or category.lower() in cat.lower():
                    return cat
            
            # 默认返回第一个类别
            return categories[0] if categories else "未分类"
            
        except Exception as e:
            print(f"内容分类失败: {e}")
            return categories[0] if categories else "未分类"
    
    def extract_keywords(self, content: str, max_keywords: int = 5) -> List[str]:
        """
        提取内容关键词
        
        Args:
            content: 文件内容
            max_keywords: 最多提取的关键词数量
            
        Returns:
            关键词列表
        """
        try:
            prompt = f"""请从以下内容中提取 {max_keywords} 个最重要的关键词。

内容：
{content[:1000]}

请直接输出关键词，用逗号分隔，不要其他内容。
"""
            
            response = self.llm.invoke(prompt)
            
            # 提取响应内容
            if hasattr(response, 'content'):
                keywords_str = response.content.strip()
            else:
                keywords_str = str(response).strip()
            
            # 分割关键词
            keywords = [kw.strip() for kw in keywords_str.split(',')]
            return keywords[:max_keywords]
            
        except Exception as e:
            print(f"关键词提取失败: {e}")
            return []
    
    def summarize_content(self, content: str, max_length: int = 200) -> str:
        """
        生成内容摘要
        
        Args:
            content: 文件内容
            max_length: 摘要最大长度
            
        Returns:
            摘要文本
        """
        try:
            prompt = f"""请为以下内容生成一个简短摘要（不超过{max_length}字）。

内容：
{content[:2000]}

摘要：
"""
            
            response = self.llm.invoke(prompt)
            
            # 提取响应内容
            if hasattr(response, 'content'):
                summary = response.content.strip()
            else:
                summary = str(response).strip()
            
            return summary[:max_length]
            
        except Exception as e:
            print(f"内容摘要失败: {e}")
            return ""
    
    def identify_paper(self, file_path: str) -> Dict[str, Any]:
        """
        识别PDF文件是否为学术论文并提取元信息
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            论文信息字典，包含 is_paper, title, authors, year 等字段
        """
        path = Path(file_path)
        
        # 只处理PDF文件
        if path.suffix.lower() != '.pdf':
            return {
                'is_paper': False,
                'reason': '不是PDF文件',
                'file_type': path.suffix
            }
        
        if not path.exists():
            return {
                'is_paper': False,
                'error': '文件不存在'
            }
        
        try:
            # 读取PDF内容
            content = self.pdf_reader.extract_text_sample(file_path, max_chars=2000)
            
            if not content or len(content) < 100:
                return {
                    'is_paper': False,
                    'reason': 'PDF内容为空或太短',
                    'confidence': 0.0
                }
            
            # 简单规则检测（快速预判）
            paper_indicators = [
                'abstract', 'introduction', 'references', 'conclusion',
                '摘要', '引言', '参考文献', '结论',
                'doi:', 'arxiv:', 'published', 'journal', 'conference'
            ]
            
            content_lower = content.lower()
            indicator_count = sum(1 for ind in paper_indicators if ind in content_lower)
            
            # 如果明显不是论文，直接返回
            if indicator_count < 2:
                return {
                    'is_paper': False,
                    'reason': '缺少学术论文特征',
                    'confidence': 0.2,
                    'indicators_found': indicator_count
                }
            
            # 使用LLM进行深度分析
            prompt = PAPER_IDENTIFICATION_PROMPT.format(
                filename=path.name,
                content=content[:2000]
            )
            
            response = self.llm.invoke(prompt)
            
            # 提取响应内容
            if hasattr(response, 'content'):
                response_text = response.content.strip()
            else:
                response_text = str(response).strip()
            
            # 尝试解析JSON
            paper_info = self._parse_paper_info(response_text, path.name)
            
            # 如果是论文，添加原始文件名
            if paper_info.get('is_paper'):
                paper_info['original_filename'] = path.name
                paper_info['file_path'] = file_path
            
            return paper_info
            
        except Exception as e:
            return {
                'is_paper': False,
                'error': f'论文识别失败: {str(e)}',
                'confidence': 0.0
            }
    
    def _parse_paper_info(self, response_text: str, filename: str) -> Dict[str, Any]:
        """解析LLM返回的论文信息"""
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                paper_info = json.loads(json_str)
                return paper_info
        except Exception as e:
            print(f"JSON解析失败: {e}")
        
        # 如果JSON解析失败，尝试从文本中提取信息
        result = {
            'is_paper': False,
            'title': None,
            'authors': [],
            'year': None,
            'venue': None,
            'field': None,
            'doi': None,
            'suggested_filename': filename,
            'confidence': 0.5
        }
        
        # 简单的文本解析
        if any(keyword in response_text.lower() for keyword in ['是学术论文', 'is_paper: true', 'is a paper']):
            result['is_paper'] = True
            result['confidence'] = 0.7
        
        return result
    
    def generate_paper_filename(self, paper_info: Dict[str, Any]) -> str:
        """
        根据论文信息生成规范的文件名
        
        Args:
            paper_info: 论文信息字典
            
        Returns:
            建议的文件名
        """
        if not paper_info.get('is_paper'):
            return paper_info.get('original_filename', 'unknown.pdf')
        
        # 如果LLM已经建议了文件名
        if paper_info.get('suggested_filename'):
            return paper_info['suggested_filename']
        
        # 否则自己构建
        parts = []
        
        # 添加第一作者
        if paper_info.get('authors') and len(paper_info['authors']) > 0:
            first_author = paper_info['authors'][0]
            # 提取姓氏
            author_parts = first_author.split()
            if author_parts:
                parts.append(author_parts[-1])
        
        # 添加年份
        if paper_info.get('year'):
            parts.append(str(paper_info['year']))
        
        # 添加标题（简化版）
        if paper_info.get('title'):
            title = paper_info['title']
            # 移除特殊字符，保留前5个单词
            title_words = re.findall(r'\w+', title)[:5]
            if title_words:
                parts.append('_'.join(title_words))
        
        if parts:
            filename = '_'.join(parts) + '.pdf'
            # 确保文件名不超过200字符
            if len(filename) > 200:
                filename = filename[:197] + '.pdf'
            return filename
        
        # 如果信息不足，返回原文件名
        return paper_info.get('original_filename', 'paper.pdf')