"""
历史路由
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..models.requests import UndoRequest
from ..models.responses import HistoryResponse, ErrorResponse
from ..services.history_service import get_history_service

router = APIRouter()


@router.get(
    "/operations",
    response_model=HistoryResponse,
    summary="获取操作历史",
    description="获取文件操作历史记录",
)
async def get_operation_history(
    limit: int = Query(default=20, ge=1, le=100, description="每页数量"),
    page: int = Query(default=1, ge=1, description="页码"),
):
    """获取操作历史"""
    try:
        service = get_history_service()
        return service.get_operation_history(limit=limit, page=page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@router.post(
    "/undo",
    summary="撤销操作",
    description="撤销最后一次文件操作",
)
async def undo_last_operation(request: UndoRequest):
    """撤销最后一次操作"""
    try:
        service = get_history_service()
        
        if not service.can_undo():
            raise HTTPException(status_code=400, detail="没有可撤销的操作")
        
        if not request.confirm:
            # 返回将要撤销的操作信息
            undo_history = service.get_undo_history()
            if undo_history:
                return {
                    "message": "请确认撤销操作",
                    "operation": undo_history[-1] if undo_history else None,
                    "confirm_required": True,
                }
            raise HTTPException(status_code=400, detail="没有可撤销的操作")
        
        success = service.undo_last_operation()
        
        if success:
            return {"message": "撤销成功", "success": True}
        else:
            raise HTTPException(status_code=500, detail="撤销失败")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"撤销失败: {str(e)}")


@router.get(
    "/can-undo",
    summary="检查是否可撤销",
    description="检查是否有可撤销的操作",
)
async def check_can_undo():
    """检查是否可撤销"""
    service = get_history_service()
    return {
        "can_undo": service.can_undo(),
    }
