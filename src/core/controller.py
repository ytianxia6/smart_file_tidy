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
    
    def __init__(
        self,
        config: ConfigManager,
        ai_provider: Optional[str] = None,
        use_agent: bool = True
    ):
        """
        初始化控制器
        
        Args:
            config: 配置管理器
            ai_provider: AI提供商（如不指定则使用配置中的默认值）
            use_agent: 是否使用LangChain Agent模式（默认True）
        """
        self.config = config
        self.use_agent = use_agent
        
        # 获取AI配置
        provider = ai_provider or config.get_default_provider()
        ai_config = config.get_ai_config(provider)
        
        # 初始化AI组件
        if use_agent:
            # 使用LangChain Agent模式
            try:
                from ..langchain_integration import FileOrganizerAgent
                
                dry_run = config.get('langchain.tools.file_operator.dry_run', False)
                verbose = config.get('langchain.agent.verbose', True)
                
                self.agent = FileOrganizerAgent(
                    llm_provider=provider,
                    config=ai_config,
                    dry_run=dry_run,
                    verbose=verbose
                )
                self.ai_adapter = None
                self.classifier = None
            except ImportError as e:
                print(f"警告: 无法导入LangChain Agent，回退到传统模式: {e}")
                self.use_agent = False
        
        if not use_agent or not hasattr(self, 'agent'):
            # 使用传统AI适配器模式
            self.ai_adapter = AIAdapterFactory.create_adapter(provider, ai_config)
            self.classifier = SmartClassifier(self.ai_adapter)
            self.agent = None
        
        # 初始化各个组件
        self.file_scanner = FileScanner(
            max_file_size_mb=config.get('file_operations.max_file_size_mb', 100),
            max_depth=config.get('file_operations.scan_max_depth', 5)
        )
        
        self.file_operator = FileOperator(dry_run=False)
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
        if self.use_agent and self.agent:
            # 使用Agent模式
            # Agent会自己处理整个流程，这里我们使用传统方式作为回退
            context = self.conversation_manager.get_context()
            operations = self.classifier.classify_batch(files, user_request, context) if self.classifier else []
        else:
            # 使用传统分类器
            context = self.conversation_manager.get_context()
            operations = self.classifier.classify_batch(files, user_request, context)
        
        # 记录交互
        self.conversation_manager.add_interaction(
            user_input=user_request,
            ai_response={'operations': operations}
        )
        
        return operations
    
    def organize_with_agent(
        self,
        directory: str,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        使用Agent模式整理文件
        
        Args:
            directory: 目标目录
            user_request: 用户需求
            context: 额外上下文
            
        Returns:
            执行结果
        """
        if not self.use_agent or not self.agent:
            return {
                'success': False,
                'error': 'Agent模式未启用或未初始化'
            }
        
        result = self.agent.organize_files(directory, user_request, context)
        
        # 注意: Agent 操作不需要记录为单个 Operation
        # Agent 内部执行的具体操作会由工具自己记录
        
        return result
    
    def analyze_file_with_agent(self, file_path: str) -> Dict[str, Any]:
        """使用Agent分析文件"""
        if not self.use_agent or not self.agent:
            return {
                'success': False,
                'error': 'Agent模式未启用'
            }
        
        return self.agent.analyze_file(file_path)
    
    def suggest_organization_with_agent(self, directory: str) -> Dict[str, Any]:
        """使用Agent提供整理建议"""
        if not self.use_agent or not self.agent:
            return {
                'success': False,
                'error': 'Agent模式未启用'
            }
        
        return self.agent.suggest_organization(directory)
    
    def chat_with_agent(self, message: str) -> str:
        """与Agent对话"""
        if not self.use_agent or not self.agent:
            return "Agent模式未启用"
        
        return self.agent.chat(message)
    
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
