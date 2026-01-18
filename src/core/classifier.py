"""智能分类器"""

import re
from pathlib import Path
from typing import List, Dict, Any
from ..models import FileInfo, Operation, OperationType
from ..ai import BaseAIAdapter
from ..utils import PDFReader


class SmartClassifier:
    """智能分类器 - 使用AI进行文件分类"""
    
    def __init__(self, ai_adapter: BaseAIAdapter):
        """
        初始化智能分类器
        
        Args:
            ai_adapter: AI适配器实例
        """
        self.ai_adapter = ai_adapter
        self.learned_rules = []  # 学习到的规则
    
    def classify_batch(
        self,
        files: List[FileInfo],
        user_request: str,
        context: Dict[str, Any] = None
    ) -> List[Operation]:
        """
        批量分类文件
        
        Args:
            files: 文件列表
            user_request: 用户需求
            context: 上下文信息
            
        Returns:
            操作列表
        """
        if context is None:
            context = {}
        
        # 添加学习到的规则到上下文
        context['learned_rules'] = self.learned_rules
        
        # 1. 快速预分类（基于扩展名和已知规则）
        quick_classified, uncertain = self._quick_classify(files, user_request)
        
        # 2. 对不确定的文件使用AI分类
        ai_operations = []
        if uncertain:
            try:
                ai_result = self.ai_adapter.generate_classification(
                    uncertain, user_request, context
                )
                ai_operations = self._parse_ai_result(ai_result)
            except Exception as e:
                print(f"AI分类失败: {e}")
                # 降级处理：使用简单规则
                ai_operations = self._fallback_classify(uncertain, user_request)
        
        # 3. 合并结果
        all_operations = quick_classified + ai_operations
        
        return all_operations
    
    def refine_with_feedback(
        self,
        previous_operations: List[Operation],
        feedback: str,
        files: List[FileInfo]
    ) -> List[Operation]:
        """
        根据用户反馈优化分类
        
        Args:
            previous_operations: 之前的操作列表
            feedback: 用户反馈
            files: 当前文件列表
            
        Returns:
            优化后的操作列表
        """
        # 从反馈中学习规则
        self._learn_from_feedback(feedback)
        
        # 构建之前的结果
        previous_result = {
            'operations': [
                {
                    'type': op.type.value,
                    'file': op.source,
                    'target': op.target,
                    'reason': op.reason
                }
                for op in previous_operations
            ],
            'summary': f"共{len(previous_operations)}个操作"
        }
        
        try:
            # 使用AI优化
            refined_result = self.ai_adapter.refine_with_feedback(
                previous_result, feedback, files
            )
            return self._parse_ai_result(refined_result)
        except Exception as e:
            print(f"AI优化失败: {e}")
            # 返回原操作
            return previous_operations
    
    def _quick_classify(
        self,
        files: List[FileInfo],
        user_request: str
    ) -> tuple[List[Operation], List[FileInfo]]:
        """快速预分类（基于规则）"""
        operations = []
        uncertain = []
        
        for file in files:
            # 应用已知规则
            op = self._apply_rules(file, user_request)
            if op:
                operations.append(op)
            else:
                uncertain.append(file)
        
        return operations, uncertain
    
    def _apply_rules(self, file: FileInfo, user_request: str) -> Operation:
        """应用已知规则"""
        # 这里可以实现基于规则的分类
        # 例如：特定扩展名、文件名模式等
        return None
    
    def _learn_from_feedback(self, feedback: str):
        """从用户反馈中学习规则"""
        feedback_lower = feedback.lower()
        
        # 提取规则模式
        # 例如："数字文件名不是论文"
        if '数字' in feedback_lower and '文件名' in feedback_lower:
            rule = "纯数字文件名的PDF通常不是学术论文"
            if rule not in self.learned_rules:
                self.learned_rules.append(rule)
        
        # "简历"、"发票"等关键词
        keywords = ['简历', '发票', '收据', '报销', '证书', '手册']
        for keyword in keywords:
            if keyword in feedback:
                rule = f"文件名包含'{keyword}'的文件应单独分类"
                if rule not in self.learned_rules:
                    self.learned_rules.append(rule)
    
    def _parse_ai_result(self, ai_result: Dict[str, Any]) -> List[Operation]:
        """解析AI返回的结果"""
        operations = []
        
        for op_data in ai_result.get('operations', []):
            try:
                # 确定操作类型
                op_type = OperationType(op_data['type'])
                
                operation = Operation(
                    type=op_type,
                    source=op_data['file'],
                    target=op_data['target'],
                    reason=op_data.get('reason', ''),
                    confidence=op_data.get('confidence', 1.0)
                )
                operations.append(operation)
            except Exception as e:
                print(f"解析操作失败: {e}, 数据: {op_data}")
                continue
        
        return operations
    
    def _fallback_classify(
        self,
        files: List[FileInfo],
        user_request: str
    ) -> List[Operation]:
        """降级分类（当AI不可用时）"""
        operations = []
        request_lower = user_request.lower()
        
        # 从用户请求中提取目标文件夹
        target_folder = self._extract_target_folder(user_request)
        if not target_folder:
            target_folder = "整理后的文件"
        
        # 简单地按文件类型分类
        for file in files:
            file_path = Path(file.path)
            target_path = Path(file_path.parent) / target_folder / file.name
            
            operation = Operation(
                type=OperationType.MOVE,
                source=file.path,
                target=str(target_path),
                reason="简单分类（AI不可用）",
                confidence=0.5
            )
            operations.append(operation)
        
        return operations
    
    def _extract_target_folder(self, user_request: str) -> str:
        """从用户请求中提取目标文件夹名"""
        # 使用正则提取引号中的内容
        match = re.search(r'[\'\"](.*?)[\'\"]', user_request)
        if match:
            return match.group(1)
        
        # 提取常见模式
        patterns = [
            r'到\s*([^\s，。！？]+)\s*文件夹',
            r'移到\s*([^\s，。！？]+)',
            r'整理到\s*([^\s，。！？]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_request)
            if match:
                return match.group(1)
        
        return None


class ConversationManager:
    """对话管理器 - 管理多轮对话历史"""
    
    def __init__(self):
        self.history = []
        self.context = {}
    
    def add_interaction(
        self,
        user_input: str,
        ai_response: Dict[str, Any],
        user_feedback: str = None
    ):
        """记录交互历史"""
        from datetime import datetime
        
        self.history.append({
            'user_input': user_input,
            'ai_response': ai_response,
            'feedback': user_feedback,
            'timestamp': datetime.now()
        })
    
    def get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return {
            'history': self.history,
            **self.context
        }
    
    def update_context(self, key: str, value: Any):
        """更新上下文"""
        self.context[key] = value
