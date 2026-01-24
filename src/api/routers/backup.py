"""
备份路由
"""

from fastapi import APIRouter, HTTPException
from typing import List

from ..models.requests import BackupRestoreRequest
from ..models.responses import BackupResponse, ErrorResponse
from ..services.history_service import get_history_service

router = APIRouter()


@router.get(
    "/points",
    response_model=BackupResponse,
    summary="获取备份列表",
    description="获取所有备份点列表",
)
async def list_backups():
    """获取备份列表"""
    try:
        service = get_history_service()
        return service.list_backups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取备份列表失败: {str(e)}")


@router.post(
    "/create",
    summary="创建备份",
    description="为指定文件创建备份点",
)
async def create_backup(file_paths: List[str]):
    """创建备份"""
    try:
        if not file_paths:
            raise HTTPException(status_code=400, detail="文件路径列表不能为空")
        
        service = get_history_service()
        backup_id = service.create_backup(file_paths)
        
        return {
            "message": "备份创建成功",
            "backup_id": backup_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建备份失败: {str(e)}")


@router.post(
    "/restore",
    summary="恢复备份",
    description="从备份点恢复文件",
)
async def restore_backup(request: BackupRestoreRequest):
    """恢复备份"""
    try:
        service = get_history_service()
        success = service.restore_backup(request.backup_id)
        
        if success:
            return {
                "message": "备份恢复成功",
                "backup_id": request.backup_id,
            }
        else:
            raise HTTPException(status_code=500, detail="备份恢复失败")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复备份失败: {str(e)}")


@router.delete(
    "/{backup_id}",
    summary="删除备份",
    description="删除指定的备份点",
)
async def delete_backup(backup_id: str):
    """删除备份"""
    try:
        service = get_history_service()
        success = service.delete_backup(backup_id)
        
        if success:
            return {
                "message": "备份删除成功",
                "backup_id": backup_id,
            }
        else:
            raise HTTPException(status_code=404, detail=f"备份不存在: {backup_id}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除备份失败: {str(e)}")
