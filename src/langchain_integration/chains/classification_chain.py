"""文件分类Chain"""

from typing import List, Dict, Any
from langchain_core.language_models.base import BaseLanguageModel

from ...models.file_info import FileInfo
from ..prompts import CLASSIFICATION_PROMPT


class ClassificationChain:
    """文件分类Chain - 使用LLM对文件进行智能分类"""
    
    def __init__(self, llm: BaseLanguageModel):
        """
        初始化分类Chain
        
        Args:
            llm: LangChain LLM实例
        """
        self.llm = llm
    
    def classify(
        self,
        files: List[FileInfo],
        user_request: str
    ) -> Dict[str, Any]:
        """
        对文件进行分类
        
        Args:
            files: 文件信息列表
            user_request: 用户需求
            
        Returns:
            分类结果字典
        """
        # 格式化文件信息
        file_info_text = self._format_file_info(files)
        
        # 执行分类
        try:
            # 直接构建 prompt
            prompt = CLASSIFICATION_PROMPT.format(
                file_info=file_info_text,
                user_request=user_request
            )
            
            # 直接调用 LLM
            response = self.llm.invoke(prompt)
            
            # 提取响应内容
            if hasattr(response, 'content'):
                result_text = response.content
            else:
                result_text = str(response)
            
            return {
                'success': True,
                'classification': result_text,
                'file_count': len(files)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_file_info(self, files: List[FileInfo]) -> str:
        """格式化文件信息为文本"""
        lines = []
        
        for i, file in enumerate(files, 1):
            info = [
                f"\n文件 {i}:",
                f"  路径: {file.path}",
                f"  名称: {file.name}",
                f"  类型: {file.extension}",
                f"  大小: {round(file.size / 1024 / 1024, 2)} MB",
            ]
            
            # 添加元数据
            if file.metadata:
                if 'title' in file.metadata:
                    info.append(f"  标题: {file.metadata['title']}")
                if 'author' in file.metadata:
                    info.append(f"  作者: {file.metadata['author']}")
                if 'page_count' in file.metadata:
                    info.append(f"  页数: {file.metadata['page_count']}")
            
            # 添加内容样本
            if file.content_sample:
                sample = file.content_sample[:200]
                info.append(f"  内容样本: {sample}...")
            
            lines.extend(info)
        
        return '\n'.join(lines)
    
    def suggest_categories(self, files: List[FileInfo]) -> List[str]:
        """
        基于文件特征建议分类类别
        
        Args:
            files: 文件信息列表
            
        Returns:
            建议的类别列表
        """
        try:
            file_info_text = self._format_file_info(files[:20])  # 限制数量
            
            prompt = f"""基于以下文件信息，建议3-5个合理的分类类别：

{file_info_text}

请直接输出类别名称，每行一个，不要其他内容。
"""
            
            response = self.llm.invoke(prompt)
            
            # 提取类别列表
            if hasattr(response, 'content'):
                categories_text = response.content
            else:
                categories_text = str(response)
            
            categories = [
                line.strip()
                for line in categories_text.split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            
            return categories[:5]  # 最多5个类别
            
        except Exception as e:
            print(f"建议类别失败: {e}")
            return ['文档', '图片', '其他']
