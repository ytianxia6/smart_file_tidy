"""
整理服务 - 封装文件整理功能
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

from ...core.controller import Controller
from ...core.file_operator import FileOperator
from ...models import FileInfo, Operation, OperationResult, OperationType
from ...utils.config import ConfigManager
from ..models.requests import OperationModel
from ..models.responses import (
    TaskResponse,
    OperationResponse,
    OperationResultResponse,
)
from .task_manager import TaskManager, TaskStatus, get_task_manager
from .scan_service import get_scan_service


class OrganizeService:
    """整理服务"""
    
    def __init__(self):
        self._config = ConfigManager()
        self._task_manager = get_task_manager()
        self._scan_service = get_scan_service()
    
    def _operation_to_response(self, op: Operation) -> OperationResponse:
        """转换 Operation 为响应模型"""
        return OperationResponse(
            id=op.id,
            type=op.type.value if isinstance(op.type, OperationType) else op.type,
            source=op.source,
            target=op.target,
            reason=op.reason,
            confidence=op.confidence,
            timestamp=op.timestamp,
        )
    
    def _operation_model_to_operation(self, model: OperationModel) -> Operation:
        """转换请求模型为 Operation"""
        return Operation(
            id=model.id or "",
            type=OperationType(model.type),
            source=model.source,
            target=model.target,
            reason=model.reason,
            confidence=model.confidence,
        )
    
    def _result_to_response(self, result: OperationResult) -> OperationResultResponse:
        """转换 OperationResult 为响应模型"""
        return OperationResultResponse(
            total=result.total,
            success_count=result.success_count,
            failed_count=result.failed_count,
            skipped_count=result.skipped_count,
            success_rate=result.success_rate,
            operations=[self._operation_to_response(op) for op in result.operations],
            errors=result.errors,
            duration=result.duration,
        )
    
    def generate_plan(
        self,
        scan_id: str,
        user_request: str,
        ai_provider: Optional[str] = None,
    ) -> List[OperationResponse]:
        """
        生成整理方案
        
        Args:
            scan_id: 扫描结果ID
            user_request: 用户需求描述
            ai_provider: AI提供商
        
        Returns:
            操作列表
        """
        # 获取扫描结果
        files = self._scan_service.get_scan_files(scan_id)
        if not files:
            raise ValueError(f"扫描结果不存在: {scan_id}")
        
        # 创建控制器
        controller = Controller(
            config=self._config,
            ai_provider=ai_provider,
            use_agent=False  # 生成方案时不使用Agent
        )
        
        # 生成方案
        operations = controller.generate_plan(files, user_request)
        
        return [self._operation_to_response(op) for op in operations]
    
    def refine_plan(
        self,
        scan_id: str,
        operations: List[OperationModel],
        feedback: str,
        ai_provider: Optional[str] = None,
    ) -> List[OperationResponse]:
        """
        根据反馈优化方案
        
        Args:
            scan_id: 扫描结果ID
            operations: 当前操作方案
            feedback: 用户反馈
            ai_provider: AI提供商
        
        Returns:
            优化后的操作列表
        """
        # 获取扫描结果
        files = self._scan_service.get_scan_files(scan_id)
        if not files:
            raise ValueError(f"扫描结果不存在: {scan_id}")
        
        # 转换操作
        ops = [self._operation_model_to_operation(m) for m in operations]
        
        # 创建控制器
        controller = Controller(
            config=self._config,
            ai_provider=ai_provider,
            use_agent=False
        )
        controller.current_files = files
        
        # 优化方案
        refined_ops = controller.refine_plan(ops, feedback)
        
        return [self._operation_to_response(op) for op in refined_ops]
    
    async def execute_operations(
        self,
        operations: List[OperationModel],
        create_backup: bool = True,
        progress_callback: Optional[Callable[[int, str, str], None]] = None,
    ) -> OperationResultResponse:
        """
        执行操作
        
        Args:
            operations: 操作列表
            create_backup: 是否创建备份
            progress_callback: 进度回调 (progress, current_file, message)
        
        Returns:
            操作结果
        """
        # 转换操作
        ops = [self._operation_model_to_operation(m) for m in operations]
        
        # 创建控制器
        controller = Controller(
            config=self._config,
            use_agent=False
        )
        
        # 执行操作
        result = controller.execute_operations(ops, create_backup=create_backup)
        
        return self._result_to_response(result)
    
    def execute_operations_async(
        self,
        operations: List[OperationModel],
        create_backup: bool = True,
    ) -> str:
        """
        异步执行操作
        
        Args:
            operations: 操作列表
            create_backup: 是否创建备份
        
        Returns:
            任务ID
        """
        # 创建任务
        task_id = self._task_manager.create_task(
            operations=[m.model_dump() for m in operations]
        )
        
        # 启动后台任务
        asyncio.create_task(
            self._execute_task(task_id, operations, create_backup)
        )
        
        return task_id
    
    async def _execute_task(
        self,
        task_id: str,
        operations: List[OperationModel],
        create_backup: bool,
    ):
        """执行任务"""
        try:
            self._task_manager.update_task(
                task_id,
                status=TaskStatus.RUNNING,
                message="开始执行..."
            )
            
            # 转换操作
            ops = [self._operation_model_to_operation(m) for m in operations]
            total = len(ops)
            
            # 创建控制器
            controller = Controller(
                config=self._config,
                use_agent=False
            )
            
            # 逐个执行并更新进度
            success_count = 0
            failed_count = 0
            errors = []
            
            for i, op in enumerate(ops):
                try:
                    # 更新进度
                    progress = int((i / total) * 100)
                    self._task_manager.update_task(
                        task_id,
                        progress=progress,
                        current_file=op.source,
                        message=f"处理中: {op.source}"
                    )
                    
                    # 执行单个操作
                    single_result = controller.execute_operations([op], create_backup=create_backup and i == 0)
                    
                    if single_result.success_count > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                        if single_result.errors:
                            errors.extend(single_result.errors)
                    
                    # 短暂延迟以便前端接收更新
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    failed_count += 1
                    errors.append(f"{op.source}: {str(e)}")
            
            # 构建结果
            result = OperationResultResponse(
                total=total,
                success_count=success_count,
                failed_count=failed_count,
                skipped_count=0,
                success_rate=success_count / total if total > 0 else 0,
                operations=[self._operation_to_response(self._operation_model_to_operation(m)) for m in operations],
                errors=errors,
                duration=0.0,
            )
            
            self._task_manager.update_task(
                task_id,
                status=TaskStatus.COMPLETED,
                progress=100,
                result=result.model_dump(),
                message="执行完成"
            )
            
        except Exception as e:
            self._task_manager.update_task(
                task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                message=f"执行失败: {str(e)}"
            )
    
    def organize_with_agent(
        self,
        directory: str,
        user_request: str,
        ai_provider: Optional[str] = None,
        dry_run: bool = False,
        create_backup: bool = True,
    ) -> str:
        """
        使用Agent模式整理（异步）
        
        Args:
            directory: 目录路径
            user_request: 用户需求
            ai_provider: AI提供商
            dry_run: 是否模拟执行
            create_backup: 是否创建备份
        
        Returns:
            任务ID
        """
        # 创建任务
        task_id = self._task_manager.create_task()
        
        # 启动后台任务
        asyncio.create_task(
            self._agent_task(task_id, directory, user_request, ai_provider, dry_run, create_backup)
        )
        
        return task_id
    
    async def _agent_task(
        self,
        task_id: str,
        directory: str,
        user_request: str,
        ai_provider: Optional[str],
        dry_run: bool,
        create_backup: bool,
    ):
        """Agent模式任务"""
        try:
            self._task_manager.update_task(
                task_id,
                status=TaskStatus.RUNNING,
                message="Agent 正在分析..."
            )
            
            # 创建控制器
            controller = Controller(
                config=self._config,
                ai_provider=ai_provider,
                use_agent=True
            )
            
            # 更新配置
            if dry_run:
                self._config.set('langchain.tools.file_operator.dry_run', True)
            
            # 执行Agent
            result = controller.organize_with_agent(
                directory=directory,
                user_request=user_request
            )
            
            self._task_manager.update_task(
                task_id,
                status=TaskStatus.COMPLETED,
                progress=100,
                result=result,
                message="Agent 执行完成"
            )
            
        except Exception as e:
            self._task_manager.update_task(
                task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                message=f"Agent 执行失败: {str(e)}"
            )
    
    def get_task_status(self, task_id: str) -> Optional[TaskResponse]:
        """获取任务状态"""
        task = self._task_manager.get_task(task_id)
        if not task:
            return None
        
        return TaskResponse(
            task_id=task.task_id,
            status=task.status.value,
            progress=task.progress,
            current_file=task.current_file,
            message=task.message,
            operations=task.operations,
            result=task.result,
            error=task.error,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
    
    def preview_operations(
        self,
        operations: List[OperationModel],
    ) -> Dict[str, Any]:
        """预览操作"""
        ops = [self._operation_model_to_operation(m) for m in operations]
        
        file_operator = FileOperator(dry_run=True)
        return file_operator.preview_operations(ops)
    
    def validate_operations(
        self,
        operations: List[OperationModel],
    ) -> Dict[str, Any]:
        """验证操作"""
        ops = [self._operation_model_to_operation(m) for m in operations]
        
        file_operator = FileOperator(dry_run=True)
        return file_operator.validate_operations(ops)


# 全局服务实例
_organize_service: Optional[OrganizeService] = None


def get_organize_service() -> OrganizeService:
    """获取整理服务单例"""
    global _organize_service
    if _organize_service is None:
        _organize_service = OrganizeService()
    return _organize_service
