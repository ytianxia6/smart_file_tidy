"""AI适配器基类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..models import FileInfo


class BaseAIAdapter(ABC):
    """AI适配器基类 - 定义统一接口"""
    
    @abstractmethod
    def generate_classification(
        self,
        files: List[FileInfo],
        user_request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成文件分类方案
        
        Args:
            files: 文件信息列表
            user_request: 用户需求描述
            context: 上下文信息（历史对话、已知规则等）
            
        Returns:
            包含操作列表的字典
        """
        pass
    
    @abstractmethod
    def refine_with_feedback(
        self,
        previous_result: Dict[str, Any],
        feedback: str,
        files: List[FileInfo]
    ) -> Dict[str, Any]:
        """
        根据用户反馈优化分类方案
        
        Args:
            previous_result: 之前的分类结果
            feedback: 用户反馈
            files: 文件信息列表
            
        Returns:
            优化后的操作列表
        """
        pass
    
    def _validate_response(self, response: Dict[str, Any]) -> bool:
        """验证AI响应格式"""
        if not isinstance(response, dict):
            return False
        
        if 'operations' not in response:
            return False
        
        if not isinstance(response['operations'], list):
            return False
        
        # 验证每个操作的必需字段
        for op in response['operations']:
            required_fields = ['type', 'file', 'target']
            if not all(field in op for field in required_fields):
                return False
        
        return True
