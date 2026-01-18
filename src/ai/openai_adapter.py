"""OpenAI适配器"""

import json
from typing import List, Dict, Any

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base_adapter import BaseAIAdapter
from .prompt_builder import PromptBuilder
from ..models import FileInfo


class OpenAIAdapter(BaseAIAdapter):
    """OpenAI适配器"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview",
                 max_tokens: int = 4096, temperature: float = 0.7):
        """
        初始化OpenAI适配器
        
        Args:
            api_key: OpenAI API密钥
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("需要安装openai库: pip install openai")
        
        if not api_key:
            raise ValueError("OpenAI API Key不能为空")
        
        self.client = openai.OpenAI(api_key=api_key)
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
        user_prompt = self.prompt_builder.build_classification_prompt(
            files, user_request, context
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.prompt_builder.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            
            if not self._validate_response(result):
                raise ValueError("AI响应格式不正确")
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")
    
    def refine_with_feedback(
        self,
        previous_result: Dict[str, Any],
        feedback: str,
        files: List[FileInfo]
    ) -> Dict[str, Any]:
        """根据用户反馈优化分类方案"""
        user_prompt = self.prompt_builder.build_refinement_prompt(
            previous_result, feedback, files
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.prompt_builder.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = response.choices[0].message.content
            result = json.loads(response_text)
            
            if not self._validate_response(result):
                raise ValueError("AI响应格式不正确")
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")
