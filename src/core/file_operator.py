"""文件操作器"""

import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import time

from ..models import Operation, OperationResult, OperationType


class FileOperator:
    """文件操作器 - 执行文件操作（移动、重命名等）"""
    
    def __init__(self, dry_run: bool = False):
        """
        初始化文件操作器
        
        Args:
            dry_run: 仅模拟操作，不实际执行
        """
        self.dry_run = dry_run
    
    def preview_operations(self, operations: List[Operation]) -> Dict:
        """
        预览操作结果
        
        Returns:
            包含预览信息的字典
        """
        preview = {
            'total_operations': len(operations),
            'by_type': {},
            'warnings': [],
            'errors': [],
        }
        
        # 统计操作类型
        for op in operations:
            op_type = op.type.value
            preview['by_type'][op_type] = preview['by_type'].get(op_type, 0) + 1
        
        # 检查潜在问题
        for op in operations:
            # 检查源文件是否存在
            if not Path(op.source).exists():
                preview['errors'].append(f"源文件不存在: {op.source}")
            
            # 检查目标路径
            if op.type in [OperationType.MOVE, OperationType.RENAME]:
                target_path = Path(op.target)
                
                # 检查目标文件是否已存在
                if target_path.exists():
                    preview['warnings'].append(f"目标已存在: {op.target}")
                
                # 检查目标目录是否存在
                if not target_path.parent.exists():
                    preview['warnings'].append(f"目标目录不存在（将自动创建）: {target_path.parent}")
        
        preview['has_errors'] = len(preview['errors']) > 0
        
        return preview
    
    def execute_batch(
        self,
        operations: List[Operation],
        batch_size: int = 50
    ) -> OperationResult:
        """
        分批执行文件操作
        
        Args:
            operations: 操作列表
            batch_size: 批次大小
            
        Returns:
            操作结果
        """
        start_time = time.time()
        result = OperationResult(total=len(operations))
        
        # 分批处理
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            
            for op in batch:
                try:
                    success = self._execute_single_operation(op)
                    if success:
                        result.success_count += 1
                        result.operations.append(op)
                    else:
                        result.skipped_count += 1
                except Exception as e:
                    result.failed_count += 1
                    result.errors.append(f"{op.source}: {str(e)}")
        
        result.duration = time.time() - start_time
        return result
    
    def _execute_single_operation(self, operation: Operation) -> bool:
        """执行单个操作"""
        if self.dry_run:
            print(f"[DRY RUN] {operation.type.value}: {operation.source} -> {operation.target}")
            return True
        
        if operation.type == OperationType.MOVE:
            return self.move_file(operation.source, operation.target)
        elif operation.type == OperationType.RENAME:
            return self.rename_file(operation.source, operation.target)
        elif operation.type == OperationType.CREATE_FOLDER:
            return self.create_folder(operation.target)
        else:
            raise ValueError(f"不支持的操作类型: {operation.type}")
    
    def move_file(self, source: str, target: str) -> bool:
        """
        安全移动文件
        
        Args:
            source: 源路径
            target: 目标路径
            
        Returns:
            是否成功
        """
        source_path = Path(source)
        target_path = Path(target)
        
        if not source_path.exists():
            raise FileNotFoundError(f"源文件不存在: {source}")
        
        # 确保目标目录存在
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 处理文件名冲突
        if target_path.exists():
            target_path = self._resolve_conflict(target_path)
        
        # 移动文件
        shutil.move(str(source_path), str(target_path))
        
        return True
    
    def rename_file(self, source: str, new_name: str) -> bool:
        """
        安全重命名文件
        
        Args:
            source: 源路径
            new_name: 新文件名（可以是完整路径或仅文件名）
            
        Returns:
            是否成功
        """
        source_path = Path(source)
        
        if not source_path.exists():
            raise FileNotFoundError(f"源文件不存在: {source}")
        
        # 如果new_name是完整路径，直接使用；否则在同目录下重命名
        if Path(new_name).is_absolute():
            target_path = Path(new_name)
        else:
            target_path = source_path.parent / new_name
        
        # 处理冲突
        if target_path.exists() and target_path != source_path:
            target_path = self._resolve_conflict(target_path)
        
        source_path.rename(target_path)
        return True
    
    def create_folder(self, folder_path: str) -> bool:
        """
        创建文件夹
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            是否成功
        """
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        return True
    
    def _resolve_conflict(self, target_path: Path) -> Path:
        """处理文件名冲突"""
        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def validate_operations(self, operations: List[Operation]) -> Dict:
        """
        验证操作安全性
        
        Returns:
            验证结果字典
        """
        issues = []
        warnings = []
        
        for op in operations:
            # 检查1: 源文件是否存在
            if not Path(op.source).exists():
                issues.append(f"源文件不存在: {op.source}")
            
            # 检查2: 目标路径是否合法
            try:
                target_path = Path(op.target)
                # 尝试解析路径
                target_path.resolve()
            except Exception as e:
                issues.append(f"目标路径非法 {op.target}: {e}")
            
            # 检查3: 是否会覆盖已存在文件
            if Path(op.target).exists():
                warnings.append(f"目标已存在（将自动重命名）: {op.target}")
            
            # 检查4: 磁盘空间（简化检查）
            if Path(op.source).exists():
                file_size = Path(op.source).stat().st_size
                try:
                    target_disk = Path(op.target).parent
                    if target_disk.exists():
                        free_space = shutil.disk_usage(target_disk).free
                        if file_size > free_space:
                            issues.append(f"磁盘空间不足: 需要 {file_size}, 可用 {free_space}")
                except Exception:
                    pass
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
