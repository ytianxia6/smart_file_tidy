"""LLM工厂 - 创建不同提供商的LLM实例"""

from typing import Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.language_models.base import BaseLanguageModel


class LLMFactory:
    """LLM工厂类 - 根据配置创建对应的LLM实例"""
    
    @staticmethod
    def create_llm(provider: str, config: Dict[str, Any]) -> BaseLanguageModel:
        """
        创建LLM实例
        
        Args:
            provider: 提供商名称（claude, openai, custom, local）
            config: 配置字典
            
        Returns:
            LLM实例
        """
        if provider == 'claude':
            return LLMFactory._create_claude_llm(config)
        elif provider == 'openai':
            return LLMFactory._create_openai_llm(config)
        elif provider == 'custom':
            return LLMFactory._create_custom_llm(config)
        elif provider == 'local':
            return LLMFactory._create_local_llm(config)
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
    
    @staticmethod
    def _create_claude_llm(config: Dict[str, Any]) -> ChatAnthropic:
        """创建Claude LLM"""
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("Claude API密钥未配置")
        
        return ChatAnthropic(
            anthropic_api_key=api_key,
            model=config.get('model', 'claude-3-5-sonnet-20241022'),
            max_tokens=config.get('max_tokens', 4096),
            temperature=config.get('temperature', 0.7),
        )
    
    @staticmethod
    def _create_openai_llm(config: Dict[str, Any]) -> ChatOpenAI:
        """创建OpenAI LLM"""
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API密钥未配置")
        
        return ChatOpenAI(
            openai_api_key=api_key,
            model=config.get('model', 'gpt-4-turbo-preview'),
            max_tokens=config.get('max_tokens', 4096),
            temperature=config.get('temperature', 0.7),
        )
    
    @staticmethod
    def _create_custom_llm(config: Dict[str, Any]) -> ChatOpenAI:
        """创建自定义OpenAI兼容API的LLM"""
        api_key = config.get('api_key')
        base_url = config.get('base_url')
        model = config.get('model')
        
        if not base_url:
            raise ValueError("自定义API地址未配置")
        if not api_key:
            raise ValueError("自定义API密钥未配置")
        if not model:
            raise ValueError("自定义模型名称未配置")
        
        return ChatOpenAI(
            openai_api_key=api_key,
            base_url=base_url,
            model=model,
            max_tokens=config.get('max_tokens', 4096),
            temperature=config.get('temperature', 0.7),
        )
    
    @staticmethod
    def _create_local_llm(config: Dict[str, Any]) -> Ollama:
        """创建本地LLM（Ollama）"""
        base_url = config.get('base_url', 'http://localhost:11434')
        model = config.get('model', 'llama3.1')
        
        return Ollama(
            base_url=base_url,
            model=model,
            temperature=config.get('temperature', 0.7),
        )
    
    @staticmethod
    def test_connection(llm: BaseLanguageModel) -> bool:
        """
        测试LLM连接
        
        Args:
            llm: LLM实例
            
        Returns:
            是否连接成功
        """
        try:
            # 发送简单的测试消息
            response = llm.invoke("Hello")
            return bool(response)
        except Exception as e:
            print(f"LLM连接测试失败: {e}")
            return False
