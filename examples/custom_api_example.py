"""使用自定义API的示例"""

from src.utils import ConfigManager
from src.core import Controller


def use_azure_openai():
    """使用Azure OpenAI示例"""
    config = ConfigManager()
    
    # 设置Azure OpenAI配置
    config.set('ai.default_provider', 'custom')
    config.set('ai.providers.custom.base_url', 
               'https://your-resource.openai.azure.com/openai/deployments/your-deployment')
    config.set('ai.providers.custom.api_key', 'your-azure-api-key')
    config.set('ai.providers.custom.model', 'gpt-4')
    
    # 使用控制器
    controller = Controller(config, ai_provider='custom')
    
    # 扫描和整理
    files = controller.scan_directory('./test_files')
    operations = controller.generate_plan(files, "整理所有PDF文件")
    
    print(f"生成了 {len(operations)} 个操作")


def use_tongyi_qwen():
    """使用通义千问示例"""
    config = ConfigManager()
    
    # 设置通义千问配置
    config.set('ai.default_provider', 'custom')
    config.set('ai.providers.custom.base_url', 
               'https://dashscope.aliyuncs.com/compatible-mode/v1')
    config.set('ai.providers.custom.api_key', 'your-dashscope-api-key')
    config.set('ai.providers.custom.model', 'qwen-plus')
    
    controller = Controller(config, ai_provider='custom')
    
    files = controller.scan_directory('./test_files')
    operations = controller.generate_plan(files, "把图片整理到相册文件夹")
    
    print(f"生成了 {len(operations)} 个操作")


def use_deepseek():
    """使用DeepSeek示例"""
    config = ConfigManager()
    
    # 设置DeepSeek配置
    config.set('ai.default_provider', 'custom')
    config.set('ai.providers.custom.base_url', 'https://api.deepseek.com/v1')
    config.set('ai.providers.custom.api_key', 'your-deepseek-api-key')
    config.set('ai.providers.custom.model', 'deepseek-chat')
    
    controller = Controller(config, ai_provider='custom')
    
    files = controller.scan_directory('./test_files')
    operations = controller.generate_plan(files, "整理文档")
    
    print(f"生成了 {len(operations)} 个操作")


def use_self_hosted_model():
    """使用自部署模型示例（如vLLM）"""
    config = ConfigManager()
    
    # 设置自部署模型配置
    config.set('ai.default_provider', 'custom')
    config.set('ai.providers.custom.base_url', 'http://localhost:8000/v1')
    config.set('ai.providers.custom.api_key', 'dummy')  # 自部署通常不需要真实key
    config.set('ai.providers.custom.model', 'your-model-name')
    
    controller = Controller(config, ai_provider='custom')
    
    files = controller.scan_directory('./test_files')
    operations = controller.generate_plan(files, "整理文件")
    
    print(f"生成了 {len(operations)} 个操作")


if __name__ == '__main__':
    print("自定义API使用示例\n")
    print("=" * 50)
    
    print("\n1. Azure OpenAI")
    print("2. 通义千问")
    print("3. DeepSeek")
    print("4. 自部署模型")
    
    print("\n取消注释对应函数以运行示例")
    
    # 取消注释以运行
    # use_azure_openai()
    # use_tongyi_qwen()
    # use_deepseek()
    # use_self_hosted_model()
