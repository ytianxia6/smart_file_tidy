"""集成测试"""

import pytest
from pathlib import Path
from src.utils import ConfigManager
from src.core import Controller


def test_full_workflow(temp_dir, mock_ai_adapter, monkeypatch):
    """测试完整工作流程"""
    # 创建测试文件
    for i in range(5):
        (temp_dir / f'file_{i}.txt').write_text(f'content {i}')
    
    # 创建配置
    config_dir = temp_dir / 'config'
    config_dir.mkdir()
    config_file = config_dir / 'test_config.yaml'
    config_file.write_text("""
ai:
  default_provider: claude
  providers:
    claude:
      model: test-model
      max_tokens: 4096
      temperature: 0.7
file_operations:
  batch_size: 50
  max_file_size_mb: 100
  scan_max_depth: 5
safety:
  require_confirmation: false
  auto_backup: true
  max_undo_history: 10
logging:
  level: INFO
  log_dir: data/logs
  retention_days: 30
    """)
    
    # 初始化控制器（使用mock适配器）
    config = ConfigManager(str(config_file))
    controller = Controller(config)
    controller.ai_adapter = mock_ai_adapter
    
    # 1. 扫描目录
    files = controller.scan_directory(str(temp_dir))
    assert len(files) == 5
    
    # 2. 生成方案
    operations = controller.generate_plan(files, "整理所有文件")
    assert len(operations) > 0
    
    # 3. 预览操作
    preview = controller.preview_operations(operations)
    assert 'total_operations' in preview
    
    # 4. 执行操作（dry run）
    controller.file_operator.dry_run = True
    result = controller.execute_operations(operations, create_backup=False)
    
    assert result.success_count > 0


def test_interactive_refinement(temp_dir, mock_ai_adapter):
    """测试交互式优化"""
    # 创建测试文件
    (temp_dir / 'paper.pdf').write_bytes(b'PDF content')
    (temp_dir / '12345.pdf').write_bytes(b'PDF content')
    (temp_dir / 'invoice.pdf').write_bytes(b'PDF content')
    
    config = ConfigManager()
    controller = Controller(config)
    controller.ai_adapter = mock_ai_adapter
    
    # 扫描
    files = controller.scan_directory(str(temp_dir))
    
    # 初始分类
    operations = controller.generate_plan(files, "整理PDF")
    
    # 用户反馈
    feedback = "数字文件名的不是论文"
    refined_operations = controller.refine_plan(operations, feedback)
    
    # 检查是否学到规则
    assert len(controller.classifier.learned_rules) > 0
