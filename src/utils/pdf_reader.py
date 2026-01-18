"""PDF内容读取器"""

import re
from pathlib import Path
from typing import Optional
import PyPDF2
import pdfplumber


class PDFReader:
    """PDF内容读取器"""
    
    @staticmethod
    def extract_text_sample(file_path: str, max_pages: int = 2, max_chars: int = 1000) -> Optional[str]:
        """提取PDF文本样本"""
        try:
            # 优先使用pdfplumber（文本提取效果更好）
            return PDFReader._extract_with_pdfplumber(file_path, max_pages, max_chars)
        except Exception:
            # 降级使用PyPDF2
            try:
                return PDFReader._extract_with_pypdf2(file_path, max_pages, max_chars)
            except Exception as e:
                return f"[无法提取文本: {str(e)}]"
    
    @staticmethod
    def _extract_with_pdfplumber(file_path: str, max_pages: int, max_chars: int) -> str:
        """使用pdfplumber提取文本"""
        text_parts = []
        total_chars = 0
        
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages[:max_pages]):
                page_text = page.extract_text()
                if page_text:
                    # 清理文本
                    page_text = PDFReader._clean_text(page_text)
                    remaining = max_chars - total_chars
                    if remaining <= 0:
                        break
                    
                    text_parts.append(page_text[:remaining])
                    total_chars += len(page_text)
        
        return '\n'.join(text_parts)
    
    @staticmethod
    def _extract_with_pypdf2(file_path: str, max_pages: int, max_chars: int) -> str:
        """使用PyPDF2提取文本"""
        text_parts = []
        total_chars = 0
        
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            for i in range(min(max_pages, len(pdf_reader.pages))):
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                
                if page_text:
                    page_text = PDFReader._clean_text(page_text)
                    remaining = max_chars - total_chars
                    if remaining <= 0:
                        break
                    
                    text_parts.append(page_text[:remaining])
                    total_chars += len(page_text)
        
        return '\n'.join(text_parts)
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """清理提取的文本"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊控制字符
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
        return text.strip()
    
    @staticmethod
    def analyze_filename_pattern(filename: str) -> dict:
        """分析PDF文件名模式"""
        stem = Path(filename).stem
        
        return {
            'is_numeric': stem.replace('_', '').replace('-', '').isdigit(),
            'has_year': bool(re.search(r'20\d{2}', stem)),
            'has_chinese': bool(re.search(r'[\u4e00-\u9fff]', stem)),
            'has_english': bool(re.search(r'[a-zA-Z]', stem)),
            'has_keywords': PDFReader._check_document_keywords(stem),
            'length': len(stem),
        }
    
    @staticmethod
    def _check_document_keywords(filename: str) -> dict:
        """检查文件名中的关键词"""
        filename_lower = filename.lower()
        
        keyword_categories = {
            'paper': ['paper', 'article', 'journal', 'conference', '论文', '期刊'],
            'resume': ['resume', 'cv', '简历', '履历'],
            'invoice': ['invoice', 'receipt', '发票', '收据', '报销'],
            'manual': ['manual', 'guide', 'handbook', '手册', '指南'],
            'report': ['report', 'summary', '报告', '总结'],
            'certificate': ['certificate', 'diploma', '证书', '文凭'],
        }
        
        found = {}
        for category, keywords in keyword_categories.items():
            found[category] = any(kw in filename_lower for kw in keywords)
        
        return found
