"""Prompt构建器"""

from typing import List, Dict, Any
from ..models import FileInfo


class PromptBuilder:
    """Prompt构建器 - 构建发送给AI的提示"""
    
    # 系统提示
    SYSTEM_PROMPT = """你是一个专业的文件整理助手。你的任务是：
1. 分析文件信息（文件名、类型、元数据、内容样本）
2. 根据用户需求进行智能分类
3. 生成具体的文件操作方案（移动、重命名、分类）

输出格式要求：返回JSON格式的操作方案
{
  "operations": [
    {
      "type": "move|rename|create_folder",
      "file": "文件完整路径",
      "target": "目标路径或新名称",
      "reason": "分类依据说明",
      "confidence": 0.95
    }
  ],
  "summary": "操作概述和统计"
}

重要规则：
- type必须是move、rename或create_folder之一
- file必须是原始文件的完整路径
- target必须是完整的目标路径（对于move）或新文件名（对于rename）
- reason简要说明为什么这样分类
- confidence是0-1之间的数字，表示分类的置信度
- 对于不确定的文件，可以将confidence设置为较低值
"""
    
    @staticmethod
    def build_classification_prompt(
        files: List[FileInfo],
        user_request: str,
        context: Dict[str, Any]
    ) -> str:
        """
        构建分类任务的Prompt
        
        Args:
            files: 文件列表
            user_request: 用户需求
            context: 上下文信息
            
        Returns:
            完整的用户Prompt
        """
        prompt_parts = []
        
        # 1. 用户需求
        prompt_parts.append(f"## 用户需求\n{user_request}\n")
        
        # 2. 已知规则（如果有）
        if context.get('learned_rules'):
            prompt_parts.append("## 已知规则")
            for rule in context['learned_rules']:
                prompt_parts.append(f"- {rule}")
            prompt_parts.append("")
        
        # 3. 历史反馈（如果有）
        if context.get('history'):
            prompt_parts.append("## 历史反馈")
            for h in context['history'][-3:]:  # 最近3次
                if h.get('feedback'):
                    prompt_parts.append(f"- {h['feedback']}")
            prompt_parts.append("")
        
        # 4. 文件列表
        prompt_parts.append("## 待整理文件")
        prompt_parts.append(PromptBuilder._format_file_list(files))
        
        # 5. 任务说明
        prompt_parts.append("\n## 任务")
        prompt_parts.append("请根据以上信息生成文件操作方案，以JSON格式返回。")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def build_refinement_prompt(
        previous_result: Dict[str, Any],
        feedback: str,
        files: List[FileInfo]
    ) -> str:
        """
        构建优化任务的Prompt
        
        Args:
            previous_result: 之前的结果
            feedback: 用户反馈
            files: 文件列表
            
        Returns:
            优化任务Prompt
        """
        prompt_parts = []
        
        # 1. 说明这是优化任务
        prompt_parts.append("## 任务：根据用户反馈优化分类方案\n")
        
        # 2. 之前的结果
        prompt_parts.append("### 之前的操作方案")
        if previous_result.get('summary'):
            prompt_parts.append(previous_result['summary'])
        prompt_parts.append(f"共 {len(previous_result.get('operations', []))} 个操作\n")
        
        # 3. 用户反馈
        prompt_parts.append(f"### 用户反馈\n{feedback}\n")
        
        # 4. 文件列表
        prompt_parts.append("### 当前文件列表")
        prompt_parts.append(PromptBuilder._format_file_list(files))
        
        # 5. 任务说明
        prompt_parts.append("\n### 任务")
        prompt_parts.append("请根据用户反馈，重新生成优化后的文件操作方案，以JSON格式返回。")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def _format_file_list(files: List[FileInfo], max_files: int = 100) -> str:
        """格式化文件列表"""
        lines = []
        
        # 如果文件太多，只显示部分
        display_files = files[:max_files]
        
        for i, file in enumerate(display_files, 1):
            lines.append(f"{i}. 文件名: {file.name}")
            lines.append(f"   路径: {file.path}")
            lines.append(f"   类型: {file.extension}")
            lines.append(f"   大小: {file.size_human}")
            
            # 添加元数据信息
            if file.metadata:
                metadata_str = PromptBuilder._format_metadata(file.metadata)
                if metadata_str:
                    lines.append(f"   元数据: {metadata_str}")
            
            # 添加内容样本
            if file.content_sample and not file.content_sample.startswith('['):
                sample = file.content_sample[:150]
                if len(file.content_sample) > 150:
                    sample += "..."
                lines.append(f"   内容摘要: {sample}")
            
            lines.append("")
        
        if len(files) > max_files:
            lines.append(f"... 还有 {len(files) - max_files} 个文件未显示")
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_metadata(metadata: Dict) -> str:
        """格式化元数据"""
        important_keys = ['title', 'author', 'subject', 'page_count', 'width', 'height']
        parts = []
        
        for key in important_keys:
            if key in metadata and metadata[key]:
                parts.append(f"{key}={metadata[key]}")
        
        return ", ".join(parts) if parts else ""
