"""主控制器"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models import FileInfo, Operation, OperationResult
from ..ai import BaseAIAdapter, AIAdapterFactory
from ..utils import ConfigManager
from .file_scanner import FileScanner
from .file_operator import FileOperator
from .classifier import SmartClassifier, ConversationManager
from ..safety import OperationLogger, BackupManager, UndoManager


class Controller:
    """主控制器 - 协调各个模块"""
    
    def __init__(self, config: ConfigManager, ai_provider: Optional[str] = None):
        """
        初始化控制器
        
        Args:
            config: 配置管理器
            ai_provider: AI提供商（如不指定则使用配置中的默认值）
        """
        self.config = config
        
        # 初始化AI适配器
        provider = ai_provider or config.get_default_provider()
        ai_config = config.get_ai_config(provider)
        self.ai_adapter = AIAdapterFactory.create_adapter(provider, ai_config)
        
        # 初始化各个组件
        self.file_scanner = FileScanner(
            max_file_size_mb=config.get('file_operations.max_file_size_mb', 100),
            max_depth=config.get('file_operations.scan_max_depth', 5)
        )
        
        self.file_operator = FileOperator(dry_run=False)
        self.classifier = SmartClassifier(self.ai_adapter)
        self.conversation_manager = ConversationManager()
        
        # 安全组件
        self.logger = OperationLogger()
        self.backup_manager = BackupManager()
        self.undo_manager = UndoManager()
        
        # 当前扫描的文件列表
        self.current_files: List[FileInfo] = []
    
    def scan_directory(
        self,
        directory: str,
        recursive: bool = False,
        extensions: Optional[set] = None
    ) -> List[FileInfo]:
        """
        扫描目录
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描
            extensions: 文件扩展名过滤
            
        Returns:
            文件信息列表
        """
        self.current_files = self.file_scanner.scan_directory(
            directory=directory,
            recursive=recursive,
            extensions=extensions,
            include_metadata=True,
            include_content=False  # 默认不读取内容，需要时再读取
        )
        return self.current_files
    
    def generate_plan(
        self,
        files: List[FileInfo],
        user_request: str
    ) -> List[Operation]:
        """
        生成整理方案
        
        Args:
            files: 文件列表
            user_request: 用户需求
            
        Returns:
            操作列表
        """
        context = self.conversation_manager.get_context()
        operations = self.classifier.classify_batch(files, user_request, context)
        
        # 记录交互
        self.conversation_manager.add_interaction(
            user_input=user_request,
            ai_response={'operations': operations}
        )
        
        return operations
    
    def preview_operations(self, operations: List[Operation]) -> Dict:
        """预览操作"""
        return self.file_operator.preview_operations(operations)
    
    def execute_operations(
        self,
        operations: List[Operation],
        create_backup: bool = True
    ) -> OperationResult:
        """
        执行操作
        
        Args:
            operations: 操作列表
            create_backup: 是否创建备份
            
        Returns:
            操作结果
        """
        # 验证操作
        validation = self.file_operator.validate_operations(operations)
        if not validation['valid']:
            raise ValueError(f"操作验证失败: {validation['issues']}")
        
        # 创建备份点
        backup_id = None
        if create_backup:
            file_paths = [op.source for op in operations]
            backup_id = self.backup_manager.create_backup_point(file_paths)
        
        try:
            # 执行操作
            batch_size = self.config.get('file_operations.batch_size', 50)
            result = self.file_operator.execute_batch(operations, batch_size)
            
            # 记录操作日志
            for op in result.operations:
                self.logger.log_operation(op, 'success')
            
            # 记录到撤销栈
            self.undo_manager.record_operations(result.operations)
            
            return result
            
        except Exception as e:
            # 记录错误
            for op in operations:
                self.logger.log_operation(op, 'failed', str(e))
            
            # 如果有备份，尝试恢复
            if backup_id:
                try:
                    self.backup_manager.restore_backup(backup_id)
                except Exception as restore_error:
                    print(f"备份恢复失败: {restore_error}")
            
            raise
    
    def refine_plan(
        self,
        previous_operations: List[Operation],
        feedback: str
    ) -> List[Operation]:
        """
        根据反馈优化方案
        
        Args:
            previous_operations: 之前的操作
            feedback: 用户反馈
            
        Returns:
            优化后的操作列表
        """
        refined_operations = self.classifier.refine_with_feedback(
            previous_operations,
            feedback,
            self.current_files
        )
        
        # 记录反馈
        self.conversation_manager.add_interaction(
            user_input=feedback,
            ai_response={'operations': refined_operations},
            user_feedback=feedback
        )
        
        return refined_operations
    
    def undo_last_operation(self) -> bool:
        """撤销最后一次操作"""
        success = self.undo_manager.undo_last()
        if success:
            self.logger.log_operation(
                Operation(
                    type='undo',
                    source='',
                    target='',
                    reason='用户撤销操作'
                ),
                'success'
            )
        return success
    
    def get_operation_history(self, limit: int = 10) -> List[Dict]:
        """获取操作历史"""
        return self.logger.get_recent_operations(limit)
    
    def add_feedback(self, feedback: str):
        """添加用户反馈"""
        if self.conversation_manager.history:
            self.conversation_manager.history[-1]['feedback'] = feedback
