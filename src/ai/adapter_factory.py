"""AI适配器工厂"""

from typing import Dict, Any
from .base_adapter import BaseAIAdapter
from .claude_adapter import ClaudeAdapter
from .openai_adapter import OpenAIAdapter
from .local_adapter import LocalLLMAdapter
from .custom_adapter import CustomAPIAdapter


class AIAdapterFactory:
    """AI适配器工厂 - 根据配置创建相应的适配器"""
    
    @staticmethod
    def create_adapter(provider: str, config: Dict[str, Any]) -> BaseAIAdapter:
        """
        创建AI适配器
        
        Args:
            provider: 提供商名称（claude/openai/local/custom）
            config: 配置字典
            
        Returns:
            AI适配器实例
        """
        provider = provider.lower()
        
        if provider == 'claude':
            return AIAdapterFactory._create_claude_adapter(config)
        elif provider == 'openai':
            return AIAdapterFactory._create_openai_adapter(config)
        elif provider == 'local':
            return AIAdapterFactory._create_local_adapter(config)
        elif provider == 'custom':
            return AIAdapterFactory._create_custom_adapter(config)
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")
    
    @staticmethod
    def _create_claude_adapter(config: Dict[str, Any]) -> ClaudeAdapter:
        """创建Claude适配器"""
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("Claude API Key未配置，请设置ANTHROPIC_API_KEY环境变量")
        
        return ClaudeAdapter(
            api_key=api_key,
            model=config.get('model', 'claude-3-5-sonnet-20241022'),
            max_tokens=config.get('max_tokens', 4096),
            temperature=config.get('temperature', 0.7)
        )
    
    @staticmethod
    def _create_openai_adapter(config: Dict[str, Any]) -> OpenAIAdapter:
        """创建OpenAI适配器"""
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API Key未配置，请设置OPENAI_API_KEY环境变量")
        
        return OpenAIAdapter(
            api_key=api_key,
            model=config.get('model', 'gpt-4-turbo-preview'),
            max_tokens=config.get('max_tokens', 4096),
            temperature=config.get('temperature', 0.7)
        )
    
    @staticmethod
    def _create_local_adapter(config: Dict[str, Any]) -> LocalLLMAdapter:
        """创建本地模型适配器"""
        return LocalLLMAdapter(
            base_url=config.get('base_url', 'http://localhost:11434'),
            model=config.get('model', 'llama3.1'),
            timeout=config.get('timeout', 120)
        )
    
    @staticmethod
    def _create_custom_adapter(config: Dict[str, Any]) -> CustomAPIAdapter:
        """创建自定义API适配器"""
        base_url = config.get('base_url')
        api_key = config.get('api_key')
        model = config.get('model')
        
        if not base_url:
            raise ValueError("自定义API地址未配置，请设置 base_url")
        
        if not api_key:
            raise ValueError("自定义API密钥未配置，请设置 api_key")
        
        if not model:
            raise ValueError("自定义模型名称未配置，请设置 model")
        
        return CustomAPIAdapter(
            base_url=base_url,
            api_key=api_key,
            model=model,
            max_tokens=config.get('max_tokens', 4096),
            temperature=config.get('temperature', 0.7)
        )