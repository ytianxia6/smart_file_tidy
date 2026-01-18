"""撤销管理器"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from ..models import Operation, OperationType


class UndoManager:
    """撤销管理器 - 支持撤销文件操作"""
    
    def __init__(self, max_history: int = 10):
        """
        初始化撤销管理器
        
        Args:
            max_history: 最大历史记录数
        """
        self.undo_stack: List[Dict] = []
        self.max_history = max_history
    
    def record_operations(self, operations: List[Operation]):
        """
        记录操作用于撤销
        
        Args:
            operations: 操作列表
        """
        undo_info = {
            'timestamp': datetime.now(),
            'operations': []
        }
        
        for op in operations:
            reverse_op = self._create_reverse_operation(op)
            if reverse_op:
                undo_info['operations'].append({
                    'original': op,
                    'reverse': reverse_op
                })
        
        # 添加到栈顶
        self.undo_stack.append(undo_info)
        
        # 限制历史记录数量
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
    
    def undo_last(self) -> bool:
        """
        撤销最后一次操作
        
        Returns:
            是否成功撤销
        """
        if not self.undo_stack:
            print("没有可撤销的操作")
            return False
        
        last_batch = self.undo_stack.pop()
        success_count = 0
        failed_count = 0
        
        # 倒序执行反向操作
        for item in reversed(last_batch['operations']):
            reverse_op = item['reverse']
            try:
                self._execute_reverse_operation(reverse_op)
                success_count += 1
            except Exception as e:
                print(f"撤销操作失败: {e}")
                failed_count += 1
        
        print(f"撤销完成: 成功 {success_count}, 失败 {failed_count}")
        return failed_count == 0
    
    def can_undo(self) -> bool:
        """是否有可撤销的操作"""
        return len(self.undo_stack) > 0
    
    def get_undo_history(self) -> List[Dict]:
        """获取撤销历史"""
        return [
            {
                'timestamp': item['timestamp'].isoformat(),
                'operation_count': len(item['operations'])
            }
            for item in self.undo_stack
        ]
    
    def clear_history(self):
        """清空历史记录"""
        self.undo_stack.clear()
    
    def _create_reverse_operation(self, operation: Operation) -> Optional[Dict]:
        """创建反向操作"""
        if operation.type == OperationType.MOVE:
            # 移动的反向操作是移回原位置
            return {
                'type': 'move',
                'source': operation.target,
                'target': operation.source
            }
        elif operation.type == OperationType.RENAME:
            # 重命名的反向操作是改回原名称
            return {
                'type': 'rename',
                'source': operation.target,
                'target': operation.source
            }
        elif operation.type == OperationType.CREATE_FOLDER:
            # 创建文件夹的反向操作是删除（如果为空）
            return {
                'type': 'delete_folder',
                'source': operation.target,
                'target': ''
            }
        else:
            return None
    
    def _execute_reverse_operation(self, reverse_op: Dict):
        """执行反向操作"""
        op_type = reverse_op['type']
        source = Path(reverse_op['source'])
        target = Path(reverse_op['target'])
        
        if op_type == 'move':
            # 移回原位置
            if source.exists():
                # 确保目标目录存在
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(target))
            else:
                raise FileNotFoundError(f"源文件不存在: {source}")
        
        elif op_type == 'rename':
            # 改回原名称
            if source.exists():
                source.rename(target)
            else:
                raise FileNotFoundError(f"源文件不存在: {source}")
        
        elif op_type == 'delete_folder':
            # 删除文件夹（仅当为空时）
            if source.exists() and source.is_dir():
                # 检查是否为空
                if not any(source.iterdir()):
                    source.rmdir()
                else:
                    print(f"文件夹不为空，跳过删除: {source}")
        
        else:
            raise ValueError(f"不支持的反向操作类型: {op_type}")
