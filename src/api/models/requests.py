"""
API 请求模型
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """扫描请求"""
    directory: str = Field(..., description="要扫描的目录路径")
    recursive: bool = Field(default=False, description="是否递归扫描子目录")
    extensions: Optional[List[str]] = Field(default=None, description="要包含的文件扩展名列表")
    include_metadata: bool = Field(default=True, description="是否提取文件元数据")
    include_content: bool = Field(default=False, description="是否提取文件内容样本")


class OrganizePlanRequest(BaseModel):
    """生成整理方案请求"""
    scan_id: str = Field(..., description="扫描结果ID")
    request: str = Field(..., description="用户需求描述")
    provider: Optional[str] = Field(default=None, description="AI提供商 (claude/openai/local/custom)")


class OrganizeAgentRequest(BaseModel):
    """Agent模式整理请求"""
    directory: str = Field(..., description="要整理的目录路径")
    request: str = Field(..., description="用户需求描述")
    provider: Optional[str] = Field(default=None, description="AI提供商 (claude/openai/local/custom)")
    dry_run: bool = Field(default=False, description="是否仅模拟执行")
    create_backup: bool = Field(default=True, description="是否创建备份")


class OperationModel(BaseModel):
    """操作模型"""
    id: Optional[str] = Field(default=None, description="操作ID")
    type: str = Field(..., description="操作类型 (move/rename/create_folder/delete)")
    source: str = Field(..., description="源路径")
    target: str = Field(..., description="目标路径")
    reason: str = Field(default="", description="操作原因")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="置信度")


class ExecuteRequest(BaseModel):
    """执行操作请求"""
    operations: List[OperationModel] = Field(..., description="要执行的操作列表")
    create_backup: bool = Field(default=True, description="是否创建备份")


class RefineRequest(BaseModel):
    """优化方案请求"""
    operations: List[OperationModel] = Field(..., description="当前操作方案")
    feedback: str = Field(..., description="用户反馈")
    scan_id: str = Field(..., description="扫描结果ID")


class ChatRequest(BaseModel):
    """AI对话请求"""
    message: str = Field(..., description="用户消息")
    provider: Optional[str] = Field(default=None, description="AI提供商")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class SuggestRequest(BaseModel):
    """整理建议请求"""
    directory: str = Field(..., description="目录路径")
    provider: Optional[str] = Field(default=None, description="AI提供商")


class AnalyzeRequest(BaseModel):
    """文件分析请求"""
    file_path: str = Field(..., description="文件路径")
    provider: Optional[str] = Field(default=None, description="AI提供商")


class AIConfigRequest(BaseModel):
    """AI配置请求"""
    provider: str = Field(..., description="AI提供商")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    model: Optional[str] = Field(default=None, description="模型名称")
    base_url: Optional[str] = Field(default=None, description="API基础URL")
    max_tokens: Optional[int] = Field(default=None, description="最大Token数")
    temperature: Optional[float] = Field(default=None, description="温度参数")


class BackupRestoreRequest(BaseModel):
    """备份恢复请求"""
    backup_id: str = Field(..., description="备份ID")


class UndoRequest(BaseModel):
    """撤销请求"""
    confirm: bool = Field(default=False, description="确认撤销")
