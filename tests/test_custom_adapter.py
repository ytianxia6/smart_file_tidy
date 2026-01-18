"""测试自定义API适配器"""

import pytest
from src.ai.custom_adapter import CustomAPIAdapter
from src.models import FileInfo


def test_custom_adapter_initialization():
    """测试自定义适配器初始化"""
    # 正常初始化
    adapter = CustomAPIAdapter(
        base_url="https://api.example.com/v1",
        api_key="test-key",
        model="test-model"
    )
    
    assert adapter.model == "test-model"
    assert adapter.max_tokens == 4096
    assert adapter.temperature == 0.7


def test_custom_adapter_missing_params():
    """测试缺少必需参数"""
    # 缺少base_url
    with pytest.raises(ValueError, match="API地址不能为空"):
        CustomAPIAdapter(
            base_url="",
            api_key="test-key",
            model="test-model"
        )
    
    # 缺少api_key
    with pytest.raises(ValueError, match="API Key不能为空"):
        CustomAPIAdapter(
            base_url="https://api.example.com/v1",
            api_key="",
            model="test-model"
        )
    
    # 缺少model
    with pytest.raises(ValueError, match="模型名称不能为空"):
        CustomAPIAdapter(
            base_url="https://api.example.com/v1",
            api_key="test-key",
            model=""
        )


def test_custom_adapter_with_custom_params():
    """测试自定义参数"""
    adapter = CustomAPIAdapter(
        base_url="https://api.example.com/v1",
        api_key="test-key",
        model="test-model",
        max_tokens=8192,
        temperature=0.5
    )
    
    assert adapter.max_tokens == 8192
    assert adapter.temperature == 0.5


def test_json_parsing():
    """测试JSON解析"""
    adapter = CustomAPIAdapter(
        base_url="https://api.example.com/v1",
        api_key="test-key",
        model="test-model"
    )
    
    # 测试标准JSON
    json_str = '{"operations": [], "summary": "test"}'
    result = adapter._parse_json_response(json_str)
    assert result["operations"] == []
    
    # 测试带markdown代码块的JSON
    markdown_json = '```json\n{"operations": [], "summary": "test"}\n```'
    result = adapter._parse_json_response(markdown_json)
    assert result["operations"] == []
    
    # 测试混合文本中的JSON
    mixed_text = 'Some text\n{"operations": [], "summary": "test"}\nMore text'
    result = adapter._parse_json_response(mixed_text)
    assert result["operations"] == []
