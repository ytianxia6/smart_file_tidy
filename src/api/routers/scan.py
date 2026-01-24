"""
扫描路由
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from ..models.requests import ScanRequest
from ..models.responses import ScanResponse, ErrorResponse
from ..services.scan_service import get_scan_service

router = APIRouter()


@router.post(
    "",
    response_model=ScanResponse,
    responses={400: {"model": ErrorResponse}},
    summary="扫描目录",
    description="扫描指定目录，获取文件列表和统计信息",
)
async def scan_directory(request: ScanRequest):
    """扫描目录"""
    try:
        service = get_scan_service()
        result = service.scan_directory(
            directory=request.directory,
            recursive=request.recursive,
            extensions=request.extensions,
            include_metadata=request.include_metadata,
            include_content=request.include_content,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=f"权限不足: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"扫描失败: {str(e)}")


@router.get(
    "/{scan_id}",
    response_model=ScanResponse,
    responses={404: {"model": ErrorResponse}},
    summary="获取扫描结果",
    description="获取之前扫描的结果",
)
async def get_scan_result(scan_id: str):
    """获取扫描结果"""
    service = get_scan_service()
    result = service.get_scan_result(scan_id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"扫描结果不存在: {scan_id}")
    
    # 重新构建响应
    from ..models.responses import FileInfoResponse, ScanStatsResponse
    from datetime import datetime
    
    files = result.get("files", [])
    file_responses = []
    for f in files:
        file_responses.append(FileInfoResponse(
            path=f.path,
            name=f.name,
            extension=f.extension,
            size=f.size,
            size_human=f.size_human,
            created_time=f.created_time,
            modified_time=f.modified_time,
            metadata=f.metadata,
            content_sample=f.content_sample,
        ))
    
    # 简单统计
    total_size = sum(f.size for f in files)
    size = total_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            total_size_human = f"{size:.2f} {unit}"
            break
        size /= 1024.0
    else:
        total_size_human = f"{size:.2f} TB"
    
    return ScanResponse(
        scan_id=scan_id,
        directory=result.get("directory", ""),
        total_files=len(files),
        files=file_responses,
        stats=ScanStatsResponse(
            total_size=total_size,
            total_size_human=total_size_human,
            by_extension={},
            by_category={},
        ),
        timestamp=result.get("timestamp", datetime.now()),
    )


@router.delete(
    "/{scan_id}",
    summary="删除扫描结果",
    description="删除缓存的扫描结果",
)
async def delete_scan_result(scan_id: str):
    """删除扫描结果"""
    service = get_scan_service()
    service.delete_scan_result(scan_id)
    return {"message": "扫描结果已删除", "scan_id": scan_id}
