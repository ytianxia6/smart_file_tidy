"""操作日志系统"""

import json
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional

from ..models import Operation


class OperationLogger:
    """操作日志记录器"""
    
    def __init__(self, log_dir: str = "data/logs"):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志目录
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_operation(
        self,
        operation: Operation,
        status: str,
        error: Optional[str] = None
    ):
        """
        记录单个操作
        
        Args:
            operation: 操作对象
            status: 状态（pending/success/failed/reverted）
            error: 错误信息（如果有）
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation_id': operation.id,
            'type': operation.type.value if hasattr(operation.type, 'value') else str(operation.type),
            'source': operation.source,
            'target': operation.target,
            'reason': operation.reason,
            'status': status,
            'error': error
        }
        
        # 写入日志文件（JSONL格式，每行一个JSON对象）
        log_file = self.log_dir / f"{date.today()}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_recent_operations(self, limit: int = 10) -> List[Dict]:
        """
        获取最近的操作记录
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            操作记录列表
        """
        operations = []
        
        # 读取最近几天的日志文件
        log_files = sorted(self.log_dir.glob('*.jsonl'), reverse=True)
        
        for log_file in log_files[:7]:  # 最多读取最近7天
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            operations.append(json.loads(line))
                        if len(operations) >= limit:
                            break
                
                if len(operations) >= limit:
                    break
            except Exception as e:
                print(f"读取日志文件失败 {log_file}: {e}")
        
        return operations[:limit]
    
    def get_operations_by_date(self, target_date: date) -> List[Dict]:
        """
        获取指定日期的操作记录
        
        Args:
            target_date: 目标日期
            
        Returns:
            操作记录列表
        """
        operations = []
        log_file = self.log_dir / f"{target_date}.jsonl"
        
        if not log_file.exists():
            return operations
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        operations.append(json.loads(line))
        except Exception as e:
            print(f"读取日志文件失败 {log_file}: {e}")
        
        return operations
    
    def cleanup_old_logs(self, retention_days: int = 30):
        """
        清理旧日志
        
        Args:
            retention_days: 保留天数
        """
        from datetime import timedelta
        
        cutoff_date = date.today() - timedelta(days=retention_days)
        
        for log_file in self.log_dir.glob('*.jsonl'):
            try:
                # 从文件名提取日期
                file_date_str = log_file.stem
                file_date = date.fromisoformat(file_date_str)
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    print(f"删除旧日志: {log_file}")
            except Exception as e:
                print(f"处理日志文件失败 {log_file}: {e}")
