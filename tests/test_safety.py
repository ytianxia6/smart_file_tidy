"""测试安全机制"""

import pytest
from pathlib import Path
from datetime import date
from src.safety import OperationLogger, BackupManager, UndoManager
from src.models import Operation, OperationType


def test_operation_logger(temp_dir):
    """测试操作日志"""
    log_dir = temp_dir / 'logs'
    logger = OperationLogger(str(log_dir))
    
    # 记录操作
    op = Operation(
        type=OperationType.MOVE,
        source='/source/file.txt',
        target='/target/file.txt',
        reason='test'
    )
    
    logger.log_operation(op, 'success')
    
    # 检查日志文件是否创建
    log_file = log_dir / f"{date.today()}.jsonl"
    assert log_file.exists()
    
    # 读取日志
    recent_ops = logger.get_recent_operations(limit=5)
    assert len(recent_ops) >= 1
    assert recent_ops[0]['status'] == 'success'


def test_backup_manager(temp_dir):
    """测试备份管理"""
    backup_dir = temp_dir / 'backups'
    manager = BackupManager(str(backup_dir))
    
    # 创建测试文件
    test_file = temp_dir / 'test.txt'
    test_file.write_text('test content')
    
    # 创建备份
    backup_id = manager.create_backup_point([str(test_file)])
    
    assert backup_id is not None
    assert (backup_dir / backup_id).exists()
    assert (backup_dir / backup_id / 'manifest.json').exists()
    
    # 列出备份
    backups = manager.list_backups()
    assert len(backups) >= 1
    assert backups[0]['backup_id'] == backup_id


def test_undo_manager(temp_dir):
    """测试撤销管理"""
    manager = UndoManager()
    
    # 创建测试文件
    source = temp_dir / 'source.txt'
    source.write_text('content')
    target = temp_dir / 'target.txt'
    
    # 模拟移动操作
    source.rename(target)
    
    # 记录操作
    op = Operation(
        type=OperationType.MOVE,
        source=str(source),
        target=str(target),
        reason='test'
    )
    manager.record_operations([op])
    
    assert manager.can_undo()
    
    # 执行撤销
    success = manager.undo_last()
    
    assert success
    assert source.exists()
    assert not target.exists()


def test_undo_history(temp_dir):
    """测试撤销历史"""
    manager = UndoManager(max_history=3)
    
    # 添加多个操作
    for i in range(5):
        op = Operation(
            type=OperationType.MOVE,
            source=f'/source_{i}.txt',
            target=f'/target_{i}.txt',
            reason=f'test {i}'
        )
        manager.record_operations([op])
    
    # 检查历史限制
    history = manager.get_undo_history()
    assert len(history) <= 3
