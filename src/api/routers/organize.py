"""
整理路由
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import asyncio
import json

from ..models.requests import (
    OrganizePlanRequest,
    OrganizeAgentRequest,
    ExecuteRequest,
    RefineRequest,
    OperationModel,
)
from ..models.responses import (
    TaskResponse,
    OperationResponse,
    OperationResultResponse,
    ErrorResponse,
)
from ..services.organize_service import get_organize_service
from ..services.task_manager import get_task_manager

router = APIRouter()


@router.post(
    "/plan",
    response_model=List[OperationResponse],
    responses={400: {"model": ErrorResponse}},
    summary="生成整理方案",
    description="基于扫描结果和用户需求生成整理方案（不执行）",
)
async def generate_plan(request: OrganizePlanRequest):
    """生成整理方案"""
    try:
        service = get_organize_service()
        operations = service.generate_plan(
            scan_id=request.scan_id,
            user_request=request.request,
            ai_provider=request.provider,
        )
        return operations
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成方案失败: {str(e)}")


@router.post(
    "/refine",
    response_model=List[OperationResponse],
    responses={400: {"model": ErrorResponse}},
    summary="优化整理方案",
    description="根据用户反馈优化整理方案",
)
async def refine_plan(request: RefineRequest):
    """优化整理方案"""
    try:
        service = get_organize_service()
        operations = service.refine_plan(
            scan_id=request.scan_id,
            operations=request.operations,
            feedback=request.feedback,
        )
        return operations
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化方案失败: {str(e)}")


@router.post(
    "/execute",
    response_model=TaskResponse,
    responses={400: {"model": ErrorResponse}},
    summary="执行整理操作",
    description="执行整理操作（异步）",
)
async def execute_operations(request: ExecuteRequest):
    """执行整理操作"""
    try:
        service = get_organize_service()
        task_id = service.execute_operations_async(
            operations=request.operations,
            create_backup=request.create_backup,
        )
        
        # 返回任务状态
        task_response = service.get_task_status(task_id)
        if task_response:
            return task_response
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            progress=0,
            message="任务已创建",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")


@router.post(
    "/agent",
    response_model=TaskResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Agent模式整理",
    description="使用AI Agent自动整理文件（推荐）",
)
async def organize_with_agent(request: OrganizeAgentRequest):
    """Agent模式整理"""
    try:
        service = get_organize_service()
        task_id = service.organize_with_agent(
            directory=request.directory,
            user_request=request.request,
            ai_provider=request.provider,
            dry_run=request.dry_run,
            create_backup=request.create_backup,
        )
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            progress=0,
            message="Agent任务已创建",
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent执行失败: {str(e)}")


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    responses={404: {"model": ErrorResponse}},
    summary="获取任务状态",
    description="获取整理任务的当前状态",
)
async def get_task_status(task_id: str):
    """获取任务状态"""
    service = get_organize_service()
    task_response = service.get_task_status(task_id)
    
    if not task_response:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    
    return task_response


@router.get(
    "/{task_id}/stream",
    summary="任务进度流",
    description="获取任务进度的SSE流",
)
async def stream_task_progress(task_id: str):
    """任务进度SSE流"""
    task_manager = get_task_manager()
    task = task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    
    async def event_generator():
        queue = task_manager.subscribe(task_id)
        
        try:
            # 先发送当前状态
            yield f"data: {json.dumps(task.to_dict())}\n\n"
            
            # 持续监听更新
            while True:
                try:
                    # 等待更新，超时30秒
                    update = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(update)}\n\n"
                    
                    # 如果任务完成或失败，结束流
                    if update.get("status") in ("completed", "failed"):
                        break
                        
                except asyncio.TimeoutError:
                    # 发送心跳
                    yield f": heartbeat\n\n"
                    
        finally:
            task_manager.unsubscribe(task_id, queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post(
    "/preview",
    summary="预览操作",
    description="预览操作效果（不实际执行）",
)
async def preview_operations(operations: List[OperationModel]):
    """预览操作"""
    try:
        service = get_organize_service()
        preview = service.preview_operations(operations)
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.post(
    "/validate",
    summary="验证操作",
    description="验证操作是否可以安全执行",
)
async def validate_operations(operations: List[OperationModel]):
    """验证操作"""
    try:
        service = get_organize_service()
        validation = service.validate_operations(operations)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")
