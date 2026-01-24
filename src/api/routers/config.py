"""
配置路由
"""

from fastapi import APIRouter, HTTPException
import os

from ..models.requests import AIConfigRequest
from ..models.responses import ConfigResponse, AIProviderConfig, ErrorResponse
from ..dependencies import get_config

router = APIRouter()


@router.get(
    "",
    response_model=ConfigResponse,
    summary="获取配置",
    description="获取当前系统配置",
)
async def get_configuration():
    """获取配置"""
    try:
        config = get_config()
        
        # 获取默认提供商
        default_provider = config.get_default_provider()
        
        # 构建提供商配置列表
        providers = []
        
        # Claude
        claude_key = os.getenv('ANTHROPIC_API_KEY', '')
        providers.append(AIProviderConfig(
            provider="claude",
            model=config.get('ai.providers.claude.model', 'claude-3-5-sonnet-20241022'),
            is_configured=bool(claude_key),
            is_default=default_provider == 'claude',
        ))
        
        # OpenAI
        openai_key = os.getenv('OPENAI_API_KEY', '')
        providers.append(AIProviderConfig(
            provider="openai",
            model=config.get('ai.providers.openai.model', 'gpt-4-turbo-preview'),
            is_configured=bool(openai_key),
            is_default=default_provider == 'openai',
        ))
        
        # Local
        local_url = os.getenv('LOCAL_LLM_BASE_URL', config.get('ai.providers.local.base_url', ''))
        providers.append(AIProviderConfig(
            provider="local",
            model=config.get('ai.providers.local.model', 'llama3.1'),
            is_configured=bool(local_url),
            is_default=default_provider == 'local',
        ))
        
        # Custom
        custom_url = os.getenv('CUSTOM_API_BASE_URL', config.get('ai.providers.custom.base_url', ''))
        providers.append(AIProviderConfig(
            provider="custom",
            model=config.get('ai.providers.custom.model', ''),
            is_configured=bool(custom_url),
            is_default=default_provider == 'custom',
        ))
        
        # 文件操作配置
        file_operations = {
            "batch_size": config.get('file_operations.batch_size', 50),
            "max_file_size_mb": config.get('file_operations.max_file_size_mb', 100),
            "scan_max_depth": config.get('file_operations.scan_max_depth', 5),
        }
        
        return ConfigResponse(
            default_provider=default_provider,
            providers=providers,
            file_operations=file_operations,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.put(
    "/ai",
    summary="更新AI配置",
    description="更新AI提供商配置",
)
async def update_ai_config(request: AIConfigRequest):
    """更新AI配置"""
    try:
        config = get_config()
        
        provider = request.provider
        
        # 更新配置
        if request.model:
            config.set(f'ai.providers.{provider}.model', request.model)
        
        if request.max_tokens:
            config.set(f'ai.providers.{provider}.max_tokens', request.max_tokens)
        
        if request.temperature is not None:
            config.set(f'ai.providers.{provider}.temperature', request.temperature)
        
        if request.base_url:
            config.set(f'ai.providers.{provider}.base_url', request.base_url)
        
        # 注意：API Key 应该通过环境变量设置，不直接存储在配置文件中
        # 这里只是返回成功消息
        if request.api_key:
            return {
                "message": f"配置已更新。请注意：API Key 建议通过环境变量设置",
                "provider": provider,
                "warning": "API Key 未保存到配置文件，请设置相应的环境变量",
            }
        
        return {
            "message": "配置更新成功",
            "provider": provider,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.post(
    "/validate",
    summary="验证配置",
    description="验证AI提供商配置是否可用",
)
async def validate_config(provider: str = "claude"):
    """验证配置"""
    try:
        config = get_config()
        ai_config = config.get_ai_config(provider)
        
        # 检查必要配置
        issues = []
        
        if provider == "claude":
            if not os.getenv('ANTHROPIC_API_KEY'):
                issues.append("未设置 ANTHROPIC_API_KEY 环境变量")
        
        elif provider == "openai":
            if not os.getenv('OPENAI_API_KEY'):
                issues.append("未设置 OPENAI_API_KEY 环境变量")
        
        elif provider == "local":
            base_url = os.getenv('LOCAL_LLM_BASE_URL', ai_config.get('base_url', ''))
            if not base_url:
                issues.append("未设置本地模型地址 (LOCAL_LLM_BASE_URL)")
        
        elif provider == "custom":
            base_url = os.getenv('CUSTOM_API_BASE_URL', ai_config.get('base_url', ''))
            if not base_url:
                issues.append("未设置自定义API地址 (CUSTOM_API_BASE_URL)")
        
        if issues:
            return {
                "valid": False,
                "provider": provider,
                "issues": issues,
            }
        
        return {
            "valid": True,
            "provider": provider,
            "config": {
                "model": ai_config.get('model', ''),
            },
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证配置失败: {str(e)}")


@router.post(
    "/set-default",
    summary="设置默认提供商",
    description="设置默认的AI提供商",
)
async def set_default_provider(provider: str):
    """设置默认提供商"""
    try:
        valid_providers = ["claude", "openai", "local", "custom"]
        if provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"无效的提供商: {provider}。有效值: {valid_providers}"
            )
        
        config = get_config()
        config.set('ai.default_provider', provider)
        
        return {
            "message": "默认提供商设置成功",
            "default_provider": provider,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置默认提供商失败: {str(e)}")
