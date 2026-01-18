"""Claude AI适配器"""

import json
from typing import List, Dict, Any

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base_adapter import BaseAIAdapter
from .prompt_builder import PromptBuilder
from ..models import FileInfo


class ClaudeAdapter(BaseAIAdapter):
    """Claude AI适配器"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", 
                 max_tokens: int = 4096, temperature: float = 0.7):
        """
        初始化Claude适配器
        
        Args:
            api_key: Anthropic API密钥
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("需要安装anthropic库: pip install anthropic")
        
        if not api_key:
            raise ValueError("Claude API Key不能为空")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.prompt_builder = PromptBuilder()
    
    def generate_classification(
        self,
        files: List[FileInfo],
        user_request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成文件分类方案"""
        # 构建prompt
        user_prompt = self.prompt_builder.build_classification_prompt(
            files, user_request, context
        )
        
        try:
            # 调用Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.prompt_builder.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # 解析响应
            response_text = response.content[0].text
            result = self._parse_response(response_text)
            
            if not self._validate_response(result):
                raise ValueError("AI响应格式不正确")
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Claude API调用失败: {str(e)}")
    
    def refine_with_feedback(
        self,
        previous_result: Dict[str, Any],
        feedback: str,
        files: List[FileInfo]
    ) -> Dict[str, Any]:
        """根据用户反馈优化分类方案"""
        # 构建优化prompt
        user_prompt = self.prompt_builder.build_refinement_prompt(
            previous_result, feedback, files
        )
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.prompt_builder.SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = response.content[0].text
            result = self._parse_response(response_text)
            
            if not self._validate_response(result):
                raise ValueError("AI响应格式不正确")
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Claude API调用失败: {str(e)}")
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析AI响应"""
        # 尝试提取JSON
        try:
            # 直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 尝试从markdown代码块中提取
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # 尝试查找第一个{到最后一个}
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(response_text[start:end+1])
            
            raise ValueError(f"无法解析JSON响应: {response_text[:200]}")
