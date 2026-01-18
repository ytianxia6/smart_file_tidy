"""Pytest配置和fixtures"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """创建临时测试目录"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_files(temp_dir):
    """创建示例测试文件"""
    files = {
        'test.pdf': b'PDF content',
        'document.docx': b'DOCX content',
        'image.jpg': b'JPG content',
        'data.txt': b'Text content',
        'report.pdf': b'Another PDF',
    }
    
    created_files = []
    for filename, content in files.items():
        file_path = temp_dir / filename
        file_path.write_bytes(content)
        created_files.append(str(file_path))
    
    return created_files


@pytest.fixture
def mock_ai_adapter():
    """模拟AI适配器"""
    from src.ai.base_adapter import BaseAIAdapter
    from typing import List, Dict, Any
    from src.models import FileInfo
    
    class MockAIAdapter(BaseAIAdapter):
        def generate_classification(
            self,
            files: List[FileInfo],
            user_request: str,
            context: Dict[str, Any]
        ) -> Dict[str, Any]:
            # 返回简单的移动操作
            operations = []
            for file in files:
                operations.append({
                    'type': 'move',
                    'file': file.path,
                    'target': str(Path(file.path).parent / 'organized' / file.name),
                    'reason': 'Test classification',
                    'confidence': 0.9
                })
            
            return {
                'operations': operations,
                'summary': f'Classified {len(files)} files'
            }
        
        def refine_with_feedback(
            self,
            previous_result: Dict[str, Any],
            feedback: str,
            files: List[FileInfo]
        ) -> Dict[str, Any]:
            return self.generate_classification(files, feedback, {})
    
    return MockAIAdapter()
