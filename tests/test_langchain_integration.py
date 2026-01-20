"""LangChain集成测试"""

import pytest
from pathlib import Path
import os

# 测试前检查是否有必要的环境变量
pytestmark = pytest.mark.skipif(
    not os.getenv('ANTHROPIC_API_KEY') and not os.getenv('OPENAI_API_KEY'),
    reason="需要AI API密钥才能运行LangChain测试"
)


class TestLLMFactory:
    """测试LLM工厂"""
    
    def test_create_claude_llm(self):
        """测试创建Claude LLM"""
        from src.langchain_integration.llm_factory import LLMFactory
        
        if not os.getenv('ANTHROPIC_API_KEY'):
            pytest.skip("需要ANTHROPIC_API_KEY环境变量")
        
        config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'model': 'claude-3-5-sonnet-20241022'
        }
        
        llm = LLMFactory.create_llm('claude', config)
        assert llm is not None
    
    def test_create_openai_llm(self):
        """测试创建OpenAI LLM"""
        from src.langchain_integration.llm_factory import LLMFactory
        
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("需要OPENAI_API_KEY环境变量")
        
        config = {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'gpt-4-turbo-preview'
        }
        
        llm = LLMFactory.create_llm('openai', config)
        assert llm is not None


class TestTools:
    """测试LangChain工具"""
    
    def test_file_scanner_tool(self, tmp_path):
        """测试文件扫描工具"""
        from src.langchain_integration.tools.file_scanner_tool import FileScannerTool
        
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("测试内容")
        
        tool = FileScannerTool()
        result = tool._run(
            directory=str(tmp_path),
            recursive=False,
            include_content=True
        )
        
        assert result is not None
        assert 'test.txt' in result or str(tmp_path) in result
    
    def test_file_analyzer_tool(self, tmp_path):
        """测试文件分析工具"""
        from src.langchain_integration.tools.file_analyzer_tool import FileAnalyzerTool
        
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("这是一个测试文件，包含一些中文内容。")
        
        tool = FileAnalyzerTool()
        result = tool._run(
            file_path=str(test_file),
            analyze_content=True
        )
        
        assert result is not None
        assert 'success' in result
    
    def test_validation_tool(self, tmp_path):
        """测试验证工具"""
        from src.langchain_integration.tools.validation_tool import ValidationTool
        
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("测试")
        
        tool = ValidationTool()
        result = tool._run(
            validation_type='file_exists',
            paths=str(test_file)
        )
        
        assert result is not None
        assert 'all_exist' in result


class TestFileOrganizerAgent:
    """测试文件整理Agent"""
    
    @pytest.mark.skipif(
        not os.getenv('ANTHROPIC_API_KEY'),
        reason="需要ANTHROPIC_API_KEY"
    )
    def test_agent_initialization(self):
        """测试Agent初始化"""
        from src.langchain_integration.agent import FileOrganizerAgent
        
        config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'model': 'claude-3-5-sonnet-20241022'
        }
        
        agent = FileOrganizerAgent(
            llm_provider='claude',
            config=config,
            dry_run=True,
            verbose=False
        )
        
        assert agent is not None
        assert agent.llm is not None
        assert len(agent.tools) > 0
    
    @pytest.mark.skipif(
        not os.getenv('ANTHROPIC_API_KEY'),
        reason="需要ANTHROPIC_API_KEY"
    )
    def test_agent_suggest_organization(self, tmp_path):
        """测试Agent提供建议"""
        from src.langchain_integration.agent import FileOrganizerAgent
        
        # 创建测试文件
        (tmp_path / "doc1.pdf").write_bytes(b"PDF content")
        (tmp_path / "image1.jpg").write_bytes(b"JPG content")
        (tmp_path / "code.py").write_text("print('hello')")
        
        config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'model': 'claude-3-5-sonnet-20241022'
        }
        
        agent = FileOrganizerAgent(
            llm_provider='claude',
            config=config,
            dry_run=True,
            verbose=False
        )
        
        result = agent.suggest_organization(str(tmp_path))
        
        assert result is not None
        assert 'success' in result


class TestContentAnalyzer:
    """测试内容分析器"""
    
    @pytest.mark.skipif(
        not os.getenv('ANTHROPIC_API_KEY'),
        reason="需要ANTHROPIC_API_KEY"
    )
    def test_analyze_file_content(self, tmp_path):
        """测试文件内容分析"""
        from src.langchain_integration.content_analyzer import ContentAnalyzer
        from src.langchain_integration.llm_factory import LLMFactory
        
        # 创建LLM
        config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'model': 'claude-3-5-sonnet-20241022'
        }
        llm = LLMFactory.create_llm('claude', config)
        
        # 创建测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("这是一篇关于人工智能的技术文档。主要讨论了机器学习和深度学习的应用。")
        
        analyzer = ContentAnalyzer(llm)
        result = analyzer.analyze_file_content(str(test_file))
        
        assert result is not None
        assert 'file_path' in result
    
    @pytest.mark.skipif(
        not os.getenv('ANTHROPIC_API_KEY'),
        reason="需要ANTHROPIC_API_KEY"
    )
    def test_classify_content(self):
        """测试内容分类"""
        from src.langchain_integration.content_analyzer import ContentAnalyzer
        from src.langchain_integration.llm_factory import LLMFactory
        
        # 创建LLM
        config = {
            'api_key': os.getenv('ANTHROPIC_API_KEY'),
            'model': 'claude-3-5-sonnet-20241022'
        }
        llm = LLMFactory.create_llm('claude', config)
        
        analyzer = ContentAnalyzer(llm)
        
        content = "这是一篇技术文档，讨论Python编程语言的最佳实践。"
        categories = ['技术文档', '个人笔记', '工作报告']
        
        category = analyzer.classify_content(content, categories)
        
        assert category in categories


class TestController:
    """测试Controller的Agent模式"""
    
    def test_controller_with_agent_mode(self):
        """测试Controller的Agent模式初始化"""
        from src.utils import ConfigManager
        from src.core import Controller
        
        config = ConfigManager()
        
        # 测试Agent模式（如果没有API密钥会回退到传统模式）
        controller = Controller(config, use_agent=True)
        
        assert controller is not None
    
    def test_controller_traditional_mode(self):
        """测试Controller的传统模式"""
        from src.utils import ConfigManager
        from src.core import Controller
        
        config = ConfigManager()
        
        # 明确使用传统模式
        controller = Controller(config, use_agent=False)
        
        assert controller is not None
        assert not controller.use_agent
        assert controller.ai_adapter is not None
