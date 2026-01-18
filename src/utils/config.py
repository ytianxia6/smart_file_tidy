"""配置管理器"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器"""
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self.load_config()
        load_dotenv()  # 加载.env文件
    
    @staticmethod
    def _get_default_config_path() -> str:
        """获取默认配置文件路径"""
        # 尝试多个位置
        possible_paths = [
            Path("config/default_config.yaml"),
            Path(__file__).parent.parent.parent / "config" / "default_config.yaml",
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        raise FileNotFoundError("找不到配置文件 config/default_config.yaml")
    
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项（支持点号分隔的多级键）"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, path: Optional[str] = None) -> None:
        """保存配置文件"""
        save_path = path or self.config_path
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
    
    def get_ai_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """获取AI提供商配置"""
        if provider is None:
            provider = self.get('ai.default_provider', 'claude')
        
        config = self.get(f'ai.providers.{provider}', {})
        
        # 从环境变量获取API Key和配置
        if provider == 'claude':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                config['api_key'] = api_key
        elif provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                config['api_key'] = api_key
        elif provider == 'local':
            base_url = os.getenv('LOCAL_LLM_BASE_URL')
            if base_url:
                config['base_url'] = base_url
            model = os.getenv('LOCAL_LLM_MODEL')
            if model:
                config['model'] = model
        elif provider == 'custom':
            # 自定义API的环境变量支持
            base_url = os.getenv('CUSTOM_API_BASE_URL')
            if base_url:
                config['base_url'] = base_url
            api_key = os.getenv('CUSTOM_API_KEY')
            if api_key:
                config['api_key'] = api_key
            model = os.getenv('CUSTOM_API_MODEL')
            if model:
                config['model'] = model
        
        return config
    
    def get_default_provider(self) -> str:
        """获取默认AI提供商"""
        return os.getenv('DEFAULT_AI_PROVIDER') or self.get('ai.default_provider', 'claude')
