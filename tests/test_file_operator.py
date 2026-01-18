"""测试文件操作器"""

import pytest
from pathlib import Path
from src.core.file_operator import FileOperator
from src.models import Operation, OperationType


def test_move_file(temp_dir):
    """测试文件移动"""
    # 创建源文件
    source = temp_dir / 'source.txt'
    source.write_text('test content')
    
    # 创建目标目录
    target_dir = temp_dir / 'target'
    target_dir.mkdir()
    target = target_dir / 'source.txt'
    
    # 执行移动
    operator = FileOperator()
    result = operator.move_file(str(source), str(target))
    
    assert result is True
    assert target.exists()
    assert not source.exists()
    assert target.read_text() == 'test content'


def test_rename_file(temp_dir):
    """测试文件重命名"""
    source = temp_dir / 'old_name.txt'
    source.write_text('content')
    
    new_name = 'new_name.txt'
    target = temp_dir / new_name
    
    operator = FileOperator()
    result = operator.rename_file(str(source), new_name)
    
    assert result is True
    assert target.exists()
    assert not source.exists()


def test_create_folder(temp_dir):
    """测试创建文件夹"""
    folder_path = temp_dir / 'new_folder' / 'nested'
    
    operator = FileOperator()
    result = operator.create_folder(str(folder_path))
    
    assert result is True
    assert folder_path.exists()
    assert folder_path.is_dir()


def test_conflict_resolution(temp_dir):
    """测试文件名冲突处理"""
    # 创建源文件
    source = temp_dir / 'source.txt'
    source.write_text('source content')
    
    # 创建已存在的目标文件
    target = temp_dir / 'target.txt'
    target.write_text('existing content')
    
    # 移动时应自动重命名
    operator = FileOperator()
    result = operator.move_file(str(source), str(target))
    
    assert result is True
    assert target.exists()
    assert target.read_text() == 'existing content'  # 原文件未被覆盖
    
    # 新文件应该被重命名
    target_1 = temp_dir / 'target_1.txt'
    assert target_1.exists()
    assert target_1.read_text() == 'source content'


def test_execute_batch(temp_dir):
    """测试批量执行操作"""
    # 创建多个文件
    files = []
    for i in range(5):
        file_path = temp_dir / f'file_{i}.txt'
        file_path.write_text(f'content {i}')
        files.append(file_path)
    
    # 创建操作列表
    target_dir = temp_dir / 'moved'
    operations = [
        Operation(
            type=OperationType.MOVE,
            source=str(f),
            target=str(target_dir / f.name),
            reason='batch move test'
        )
        for f in files
    ]
    
    # 执行
    operator = FileOperator()
    result = operator.execute_batch(operations)
    
    assert result.success_count == 5
    assert result.failed_count == 0
    assert target_dir.exists()
    assert len(list(target_dir.iterdir())) == 5


def test_dry_run_mode(temp_dir):
    """测试预览模式"""
    source = temp_dir / 'source.txt'
    source.write_text('content')
    
    target = temp_dir / 'target.txt'
    
    # 预览模式
    operator = FileOperator(dry_run=True)
    result = operator.move_file(str(source), str(target))
    
    assert result is True
    assert source.exists()  # 文件应该还在
    assert not target.exists()  # 目标不应该存在


def test_validate_operations(temp_dir):
    """测试操作验证"""
    existing = temp_dir / 'existing.txt'
    existing.write_text('content')
    
    operations = [
        # 有效操作
        Operation(
            type=OperationType.MOVE,
            source=str(existing),
            target=str(temp_dir / 'target.txt'),
            reason='valid'
        ),
        # 无效操作（源文件不存在）
        Operation(
            type=OperationType.MOVE,
            source=str(temp_dir / 'nonexistent.txt'),
            target=str(temp_dir / 'target2.txt'),
            reason='invalid'
        )
    ]
    
    operator = FileOperator()
    validation = operator.validate_operations(operations)
    
    assert validation['valid'] is False
    assert len(validation['issues']) > 0
