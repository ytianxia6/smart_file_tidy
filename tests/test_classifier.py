"""测试智能分类器"""

import pytest
from src.core.classifier import SmartClassifier, ConversationManager
from src.models import FileInfo


def test_classify_batch(mock_ai_adapter, temp_dir, sample_files):
    """测试批量分类"""
    classifier = SmartClassifier(mock_ai_adapter)
    
    # 创建文件信息列表
    files = [FileInfo.from_path(f) for f in sample_files]
    
    # 执行分类
    operations = classifier.classify_batch(
        files,
        "整理所有文件",
        {}
    )
    
    assert len(operations) > 0
    assert all(hasattr(op, 'source') for op in operations)
    assert all(hasattr(op, 'target') for op in operations)


def test_learn_from_feedback(mock_ai_adapter):
    """测试从反馈中学习"""
    classifier = SmartClassifier(mock_ai_adapter)
    
    # 添加反馈
    classifier._learn_from_feedback("数字文件名的文件不是论文")
    
    # 检查是否学到规则
    assert len(classifier.learned_rules) > 0
    assert any('数字' in rule for rule in classifier.learned_rules)


def test_conversation_manager():
    """测试对话管理器"""
    manager = ConversationManager()
    
    # 添加交互
    manager.add_interaction(
        user_input="整理文件",
        ai_response={'operations': []},
        user_feedback="很好"
    )
    
    assert len(manager.history) == 1
    assert manager.history[0]['user_input'] == "整理文件"
    assert manager.history[0]['feedback'] == "很好"
    
    # 获取上下文
    context = manager.get_context()
    assert 'history' in context
    assert len(context['history']) == 1
