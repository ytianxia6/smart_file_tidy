"""验证工具"""

import json
from typing import Type, List
from pathlib import Path
from pydantic import BaseModel, Field

# 尝试从不同位置导入 BaseTool
try:
    from langchain_core.tools import BaseTool
except ImportError:
    from langchain.tools import BaseTool


class ValidationInput(BaseModel):
    """验证工具的输入参数"""
    validation_type: str = Field(
        ...,
        description="验证类型：'file_exists'（文件存在）、'path_valid'（路径有效）、'disk_space'（磁盘空间）"
    )
    paths: str = Field(..., description="要验证的路径，多个路径用逗号分隔")


class ValidationTool(BaseTool):
    """验证工具 - 验证文件和路径"""
    
    name: str = "validation_tool"
    description: str = """验证文件、路径和系统状态。
    支持的验证类型：
    - file_exists: 检查文件或文件夹是否存在
    - path_valid: 检查路径是否有效（格式正确、可访问等）
    - disk_space: 检查磁盘空间是否足够
    
    使用场景：
    - 在执行操作前验证源文件是否存在
    - 检查目标路径是否有效
    - 确保有足够的磁盘空间
    """
    args_schema: Type[BaseModel] = ValidationInput
    
    def _run(
        self,
        validation_type: str,
        paths: str
    ) -> str:
        """执行验证"""
        try:
            # 解析路径列表
            path_list = [p.strip() for p in paths.split(',')]
            
            if validation_type == 'file_exists':
                return self._validate_file_exists(path_list)
            elif validation_type == 'path_valid':
                return self._validate_path_valid(path_list)
            elif validation_type == 'disk_space':
                return self._validate_disk_space(path_list)
            else:
                return json.dumps({
                    'success': False,
                    'error': f"不支持的验证类型: {validation_type}",
                    'supported_types': ['file_exists', 'path_valid', 'disk_space']
                }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e)
            }, ensure_ascii=False)
    
    def _validate_file_exists(self, paths: List[str]) -> str:
        """验证文件是否存在"""
        results = []
        all_exist = True
        
        for path_str in paths:
            path = Path(path_str)
            exists = path.exists()
            results.append({
                'path': path_str,
                'exists': exists,
                'is_file': path.is_file() if exists else None,
                'is_dir': path.is_dir() if exists else None
            })
            if not exists:
                all_exist = False
        
        return json.dumps({
            'success': True,
            'validation_type': 'file_exists',
            'all_exist': all_exist,
            'results': results
        }, ensure_ascii=False, indent=2)
    
    def _validate_path_valid(self, paths: List[str]) -> str:
        """验证路径是否有效"""
        results = []
        all_valid = True
        
        for path_str in paths:
            try:
                path = Path(path_str)
                # 尝试解析路径
                path.resolve()
                
                # 检查父目录是否存在
                parent_exists = path.parent.exists()
                
                results.append({
                    'path': path_str,
                    'valid': True,
                    'parent_exists': parent_exists,
                    'absolute_path': str(path.resolve())
                })
            except Exception as e:
                results.append({
                    'path': path_str,
                    'valid': False,
                    'error': str(e)
                })
                all_valid = False
        
        return json.dumps({
            'success': True,
            'validation_type': 'path_valid',
            'all_valid': all_valid,
            'results': results
        }, ensure_ascii=False, indent=2)
    
    def _validate_disk_space(self, paths: List[str]) -> str:
        """验证磁盘空间"""
        import shutil
        
        results = []
        
        for path_str in paths:
            try:
                path = Path(path_str)
                
                # 如果路径不存在，使用父目录
                check_path = path if path.exists() else path.parent
                
                if check_path.exists():
                    usage = shutil.disk_usage(check_path)
                    results.append({
                        'path': path_str,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percent_used': round(usage.used / usage.total * 100, 1)
                    })
                else:
                    results.append({
                        'path': path_str,
                        'error': '路径不存在'
                    })
            except Exception as e:
                results.append({
                    'path': path_str,
                    'error': str(e)
                })
        
        return json.dumps({
            'success': True,
            'validation_type': 'disk_space',
            'results': results
        }, ensure_ascii=False, indent=2)
    
    async def _arun(self, *args, **kwargs) -> str:
        """异步运行（暂不支持）"""
        raise NotImplementedError("异步验证暂不支持")
