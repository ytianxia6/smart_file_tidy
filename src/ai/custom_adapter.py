"""自定义OpenAI兼容API适配器"""

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


class CustomAPIAdapter(BaseAIAdapter):
    """自定义OpenAI兼容API适配器
    
    支持任何兼容OpenAI API格式的第三方服务，例如：
    - Azure OpenAI
    - 通义千问（DashScope）
    - 文心一言（千帆）
    - 智谱AI（GLM）
    - Moonshot（月之暗面）
    - DeepSeek
    - 其他自部署的模型服务
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ):
        """
        初始化自定义API适配器
        
        Args:
            base_url: API基础地址（例如：https://api.example.com/v1）
            api_key: API密钥/Token
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("需要安装openai库: pip install openai")
        
        if not base_url:
            raise ValueError("自定义API地址不能为空")
        
        if not api_key:
            raise ValueError("API Key不能为空")
        
        if not model:
            raise ValueError("模型名称不能为空")
        
        # 使用OpenAI客户端，但指定自定义base_url
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
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
                messages=[
                    {"role": "system", "content": self.prompt_builder.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = response.choices[0].message.content
            
            # 尝试解析JSON
            result = self._parse_json_response(response_text)
            
            if not self._validate_response(result):
                raise ValueError("AI响应格式不正确")
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"自定义API调用失败: {str(e)}")
    
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
                messages=[
                    {"role": "system", "content": self.prompt_builder.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response_text = response.choices[0].message.content
            result = self._parse_json_response(response_text)
            
            if not self._validate_response(result):
                raise ValueError("AI响应格式不正确")
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"自定义API调用失败: {str(e)}")
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """解析JSON响应"""
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
