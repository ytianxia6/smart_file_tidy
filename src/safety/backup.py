"""备份管理"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class BackupManager:
    """备份管理器"""
    
    def __init__(self, backup_dir: str = "data/backups"):
        """
        初始化备份管理器
        
        Args:
            backup_dir: 备份目录
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup_point(self, files: List[str]) -> str:
        """
        创建备份点
        
        Args:
            files: 要备份的文件路径列表
            
        Returns:
            备份ID
        """
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # 存储文件元信息而非复制文件（节省空间）
        manifest = {
            'backup_id': backup_id,
            'timestamp': datetime.now().isoformat(),
            'files': []
        }
        
        for file_path in files:
            try:
                path = Path(file_path)
                if path.exists() and path.is_file():
                    file_info = {
                        'path': str(path.absolute()),
                        'hash': self._compute_hash(file_path),
                        'size': path.stat().st_size,
                        'mtime': path.stat().st_mtime,
                        'exists': True
                    }
                else:
                    file_info = {
                        'path': str(path.absolute()),
                        'exists': False
                    }
                
                manifest['files'].append(file_info)
            except Exception as e:
                print(f"备份文件信息失败 {file_path}: {e}")
        
        # 保存manifest
        manifest_file = backup_path / 'manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return backup_id
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        从备份恢复（检查文件是否被修改）
        
        Args:
            backup_id: 备份ID
            
        Returns:
            是否成功恢复
        """
        backup_path = self.backup_dir / backup_id
        manifest_file = backup_path / 'manifest.json'
        
        if not manifest_file.exists():
            raise FileNotFoundError(f"备份不存在: {backup_id}")
        
        # 读取manifest
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        print(f"从备份恢复: {backup_id}")
        
        # 检查文件状态
        for file_info in manifest['files']:
            file_path = Path(file_info['path'])
            
            # 如果文件在备份时存在但现在不存在，可能被移动了
            # 这里我们主要记录状态，实际恢复需要更复杂的逻辑
            if file_info['exists']:
                if not file_path.exists():
                    print(f"文件已被移动或删除: {file_path}")
                else:
                    current_hash = self._compute_hash(str(file_path))
                    if current_hash != file_info['hash']:
                        print(f"文件已被修改: {file_path}")
        
        return True
    
    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                manifest_file = backup_dir / 'manifest.json'
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        
                        backups.append({
                            'backup_id': manifest['backup_id'],
                            'timestamp': manifest['timestamp'],
                            'file_count': len(manifest['files'])
                        })
                    except Exception as e:
                        print(f"读取备份信息失败 {backup_dir}: {e}")
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def delete_backup(self, backup_id: str):
        """删除备份"""
        backup_path = self.backup_dir / backup_id
        if backup_path.exists():
            import shutil
            shutil.rmtree(backup_path)
    
    @staticmethod
    def _compute_hash(file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # 分块读取以处理大文件
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            return f"error:{e}"
