"""文件操作工具"""

import json
from typing import Type
from pathlib import Path
from pydantic import BaseModel, Field

# 尝试从不同位置导入 BaseTool
try:
    from langchain_core.tools import BaseTool
except ImportError:
    from langchain.tools import BaseTool

from ...core.file_operator import FileOperator
from ...models.operation import Operation, OperationType


class FileOperatorInput(BaseModel):
    """文件操作工具的输入参数"""
    operation_type: str = Field(
        ...,
        description="操作类型：'move'（移动）、'rename'（重命名）、'create_folder'（创建文件夹）"
    )
    source: str = Field(
        default="",
        description="源文件或文件夹路径（create_folder操作时可为空字符串）"
    )
    target: str = Field(..., description="目标路径")
    reason: str = Field(default="", description="操作原因说明")


class FileOperatorTool(BaseTool):
    """文件操作工具 - 执行文件操作"""
    
    name: str = "file_operator"
    description: str = """执行文件系统操作。
    支持的操作类型：
    - move: 移动文件到新位置
    - rename: 重命名文件
    - create_folder: 创建文件夹
    
    注意事项：
    - 操作前会自动验证文件是否存在
    - 如果目标位置已存在同名文件，会自动重命名避免冲突
    - 所有操作都会被记录，支持撤销
    
    使用场景：
    - 根据分类结果移动文件到对应文件夹
    - 根据规则重命名文件
    - 创建分类文件夹结构
    """
    args_schema: Type[BaseModel] = FileOperatorInput
    dry_run_mode: bool = False  # 声明为类字段
    
    def __init__(self, dry_run: bool = False):
        super().__init__()
        # 使用 object.__setattr__ 绕过 Pydantic 验证
        object.__setattr__(self, 'dry_run_mode', dry_run)
    
    def _run(
        self,
        operation_type: str,
        source: str,
        target: str,
        reason: str = ""
    ) -> str:
        """执行文件操作"""
        try:
            # 创建操作器
            operator = FileOperator(dry_run=self.dry_run_mode)
            
            # 验证操作类型
            op_type_map = {
                'move': OperationType.MOVE,
                'rename': OperationType.RENAME,
                'create_folder': OperationType.CREATE_FOLDER,
            }
            
            if operation_type not in op_type_map:
                return json.dumps({
                    'success': False,
                    'error': f"不支持的操作类型: {operation_type}",
                    'supported_types': list(op_type_map.keys())
                }, ensure_ascii=False)
            
            # 创建操作对象
            operation = Operation(
                type=op_type_map[operation_type],
                source=source,
                target=target,
                reason=reason
            )
            
            # 验证操作
            validation = operator.validate_operations([operation])
            
            if not validation['valid']:
                return json.dumps({
                    'success': False,
                    'validation_failed': True,
                    'issues': validation['issues'],
                    'warnings': validation['warnings']
                }, ensure_ascii=False)
            
            # 执行操作
            if self.dry_run_mode:
                result = {
                    'success': True,
                    'dry_run': True,
                    'operation': {
                        'type': operation_type,
                        'source': source,
                        'target': target,
                        'reason': reason
                    },
                    'warnings': validation['warnings']
                }
            else:
                result_obj = operator.execute_batch([operation])
                result = {
                    'success': result_obj.success_count > 0,
                    'operation': {
                        'type': operation_type,
                        'source': source,
                        'target': target,
                        'reason': reason
                    },
                    'success_count': result_obj.success_count,
                    'failed_count': result_obj.failed_count,
                    'errors': result_obj.errors,
                    'warnings': validation['warnings']
                }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e),
                'operation_type': operation_type,
                'source': source,
                'target': target
            }, ensure_ascii=False)
    
    async def _arun(self, *args, **kwargs) -> str:
        """异步运行（暂不支持）"""
        raise NotImplementedError("异步操作暂不支持")
