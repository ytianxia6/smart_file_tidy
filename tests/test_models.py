"""测试数据模型"""

import pytest
from pathlib import Path
from src.models import FileInfo, Operation, OperationType, OperationResult


def test_file_info_from_path(temp_dir):
    """测试从路径创建FileInfo"""
    test_file = temp_dir / 'test.txt'
    test_file.write_text('test content')
    
    file_info = FileInfo.from_path(str(test_file))
    
    assert file_info.name == 'test.txt'
    assert file_info.extension == '.txt'
    assert file_info.size > 0
    assert file_info.path == str(test_file.absolute())


def test_file_info_size_human():
    """测试人类可读的文件大小"""
    file_info = FileInfo(
        path='/test/file.txt',
        name='file.txt',
        extension='.txt',
        size=1024 * 1024 * 2.5,  # 2.5 MB
        created_time='2024-01-01T00:00:00',
        modified_time='2024-01-01T00:00:00'
    )
    
    assert 'MB' in file_info.size_human
    assert '2.5' in file_info.size_human


def test_operation_creation():
    """测试操作对象创建"""
    op = Operation(
        type=OperationType.MOVE,
        source='/source/file.txt',
        target='/target/file.txt',
        reason='test move',
        confidence=0.95
    )
    
    assert op.type == OperationType.MOVE
    assert op.source == '/source/file.txt'
    assert op.confidence == 0.95
    assert op.id is not None  # 应该自动生成ID


def test_operation_result():
    """测试操作结果"""
    result = OperationResult(
        total=10,
        success_count=8,
        failed_count=2
    )
    
    assert result.total == 10
    assert result.success_rate == 0.8
    assert str(result).startswith('OperationResult')
