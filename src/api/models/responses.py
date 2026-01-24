"""
API 响应模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class FileInfoResponse(BaseModel):
    """文件信息响应"""
    path: str = Field(..., description="文件完整路径")
    name: str = Field(..., description="文件名")
    extension: str = Field(..., description="文件扩展名")
    size: int = Field(..., description="文件大小（字节）")
    size_human: str = Field(..., description="人类可读的文件大小")
    created_time: datetime = Field(..., description="创建时间")
    modified_time: datetime = Field(..., description="修改时间")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="文件元数据")
    content_sample: Optional[str] = Field(default=None, description="内容样本")


class ScanStatsResponse(BaseModel):
    """扫描统计响应"""
    total_size: int = Field(..., description="总大小（字节）")
    total_size_human: str = Field(..., description="人类可读的总大小")
    by_extension: Dict[str, int] = Field(default_factory=dict, description="按扩展名分类的文件数量")
    by_category: Dict[str, int] = Field(default_factory=dict, description="按类型分类的文件数量")


class ScanResponse(BaseModel):
    """扫描响应"""
    scan_id: str = Field(..., description="扫描ID")
    directory: str = Field(..., description="扫描的目录")
    total_files: int = Field(..., description="文件总数")
    files: List[FileInfoResponse] = Field(default_factory=list, description="文件列表")
    stats: ScanStatsResponse = Field(..., description="统计信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="扫描时间")


class OperationResponse(BaseModel):
    """操作响应"""
    id: str = Field(..., description="操作ID")
    type: str = Field(..., description="操作类型")
    source: str = Field(..., description="源路径")
    target: str = Field(..., description="目标路径")
    reason: str = Field(default="", description="操作原因")
    confidence: float = Field(default=1.0, description="置信度")
    timestamp: Optional[datetime] = Field(default=None, description="时间戳")


class OperationResultResponse(BaseModel):
    """操作结果响应"""
    total: int = Field(..., description="总操作数")
    success_count: int = Field(default=0, description="成功数")
    failed_count: int = Field(default=0, description="失败数")
    skipped_count: int = Field(default=0, description="跳过数")
    success_rate: float = Field(default=0.0, description="成功率")
    operations: List[OperationResponse] = Field(default_factory=list, description="操作列表")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    duration: float = Field(default=0.0, description="执行时长（秒）")


class TaskResponse(BaseModel):
    """任务状态响应"""
    task_id: str = Field(..., description="任务ID")
    status: Literal["pending", "running", "completed", "failed"] = Field(..., description="任务状态")
    progress: int = Field(default=0, ge=0, le=100, description="进度百分比")
    current_file: Optional[str] = Field(default=None, description="当前处理的文件")
    message: Optional[str] = Field(default=None, description="状态消息")
    operations: Optional[List[OperationResponse]] = Field(default=None, description="操作列表")
    result: Optional[OperationResultResponse] = Field(default=None, description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")


class HistoryItemResponse(BaseModel):
    """历史记录项"""
    id: str = Field(..., description="操作ID")
    type: str = Field(..., description="操作类型")
    source: str = Field(..., description="源路径")
    target: str = Field(..., description="目标路径")
    reason: str = Field(default="", description="操作原因")
    status: str = Field(..., description="状态")
    timestamp: datetime = Field(..., description="时间戳")
    error: Optional[str] = Field(default=None, description="错误信息")


class HistoryResponse(BaseModel):
    """历史记录响应"""
    operations: List[HistoryItemResponse] = Field(default_factory=list, description="操作历史")
    total: int = Field(..., description="总数")
    page: int = Field(default=1, description="当前页")
    page_size: int = Field(default=20, description="每页数量")
    can_undo: bool = Field(default=False, description="是否可撤销")


class BackupPointResponse(BaseModel):
    """备份点响应"""
    backup_id: str = Field(..., description="备份ID")
    timestamp: datetime = Field(..., description="备份时间")
    file_count: int = Field(..., description="文件数量")
    description: Optional[str] = Field(default=None, description="描述")


class BackupResponse(BaseModel):
    """备份列表响应"""
    backups: List[BackupPointResponse] = Field(default_factory=list, description="备份点列表")
    total: int = Field(..., description="总数")


class AIProviderConfig(BaseModel):
    """AI提供商配置"""
    provider: str = Field(..., description="提供商名称")
    model: str = Field(..., description="模型名称")
    is_configured: bool = Field(..., description="是否已配置")
    is_default: bool = Field(default=False, description="是否为默认提供商")


class ConfigResponse(BaseModel):
    """配置响应"""
    default_provider: str = Field(..., description="默认AI提供商")
    providers: List[AIProviderConfig] = Field(default_factory=list, description="可用的AI提供商")
    file_operations: Dict[str, Any] = Field(default_factory=dict, description="文件操作配置")


class SuggestionResponse(BaseModel):
    """整理建议响应"""
    suggestions: List[str] = Field(default_factory=list, description="建议列表")
    recommended_structure: List[Dict[str, str]] = Field(
        default_factory=list,
        description="推荐的目录结构"
    )
    analysis: Optional[str] = Field(default=None, description="分析说明")


class ChatResponse(BaseModel):
    """AI对话响应"""
    message: str = Field(..., description="AI回复")
    provider: str = Field(..., description="使用的AI提供商")


class AnalyzeResponse(BaseModel):
    """文件分析响应"""
    file_path: str = Field(..., description="文件路径")
    file_type: str = Field(..., description="文件类型")
    is_paper: bool = Field(default=False, description="是否为学术论文")
    analysis: Dict[str, Any] = Field(default_factory=dict, description="分析结果")
    suggestions: List[str] = Field(default_factory=list, description="处理建议")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(default=None, description="详细信息")
