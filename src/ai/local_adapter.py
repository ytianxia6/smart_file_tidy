"""本地模型适配器（Ollama）"""

import json
import requests
from typing import List, Dict, Any

from .base_adapter import BaseAIAdapter
from .prompt_builder import PromptBuilder
from ..models import FileInfo


class LocalLLMAdapter(BaseAIAdapter):
    """本地大模型适配器（支持Ollama等）"""
    
    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "llama3.1", timeout: int = 120):
        """
        初始化本地模型适配器
        
        Args:
            base_url: Ollama服务地址
            model: 模型名称
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.prompt_builder = PromptBuilder()
        
        # 测试连接
        self._test_connection()
    
    def _test_connection(self):
        """测试与本地模型的连接"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
        except Exception as e:
            raise ConnectionError(
                f"无法连接到本地模型服务 {self.base_url}: {str(e)}\n"
                f"请确保Ollama正在运行: ollama serve"
            )
    
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
        
        full_prompt = f"{self.prompt_builder.SYSTEM_PROMPT}\n\n{user_prompt}"
        
        try:
            result = self._call_ollama(full_prompt)
            
            if not self._validate_response(result):
                raise ValueError("AI响应格式不正确")
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"本地模型调用失败: {str(e)}")
    
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
        
        full_prompt = f"{self.prompt_builder.SYSTEM_PROMPT}\n\n{user_prompt}"
        
        try:
            result = self._call_ollama(full_prompt)
            
            if not self._validate_response(result):
                raise ValueError("AI响应格式不正确")
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"本地模型调用失败: {str(e)}")
    
    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """调用Ollama API"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.7,
                }
            },
            timeout=self.timeout
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 解析响应
        response_text = result.get('response', '')
        return self._parse_response(response_text)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """解析响应"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            raise ValueError(f"无法解析JSON响应: {response_text[:200]}")
