"""
AI 路由
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import asyncio
import json

from ..models.requests import ChatRequest, SuggestRequest, AnalyzeRequest
from ..models.responses import (
    ChatResponse,
    SuggestionResponse,
    AnalyzeResponse,
    ErrorResponse,
)
from ..dependencies import get_config, get_controller
from ...core.controller import Controller

router = APIRouter()


@router.post(
    "/suggest",
    response_model=SuggestionResponse,
    responses={400: {"model": ErrorResponse}},
    summary="获取整理建议",
    description="AI分析目录并提供整理建议",
)
async def get_suggestions(request: SuggestRequest):
    """获取整理建议"""
    try:
        config = get_config()
        controller = Controller(
            config=config,
            ai_provider=request.provider,
            use_agent=True
        )
        
        result = controller.suggest_organization_with_agent(request.directory)
        
        if not result.get('success', True):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '获取建议失败')
            )
        
        # 解析结果
        suggestions = []
        recommended_structure = []
        analysis = None
        
        if isinstance(result, dict):
            suggestions = result.get('suggestions', [])
            recommended_structure = result.get('recommended_structure', [])
            analysis = result.get('analysis', str(result))
        else:
            analysis = str(result)
        
        return SuggestionResponse(
            suggestions=suggestions if isinstance(suggestions, list) else [str(suggestions)],
            recommended_structure=recommended_structure,
            analysis=analysis,
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取建议失败: {str(e)}")


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={400: {"model": ErrorResponse}},
    summary="分析文件",
    description="AI深度分析单个文件",
)
async def analyze_file(request: AnalyzeRequest):
    """分析文件"""
    try:
        config = get_config()
        controller = Controller(
            config=config,
            ai_provider=request.provider,
            use_agent=True
        )
        
        result = controller.analyze_file_with_agent(request.file_path)
        
        if not result.get('success', True):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '分析失败')
            )
        
        return AnalyzeResponse(
            file_path=request.file_path,
            file_type=result.get('file_type', 'unknown'),
            is_paper=result.get('is_paper', False),
            analysis=result.get('analysis', {}),
            suggestions=result.get('suggestions', []),
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={400: {"model": ErrorResponse}},
    summary="AI对话",
    description="与AI助手对话",
)
async def chat(request: ChatRequest):
    """AI对话"""
    try:
        config = get_config()
        controller = Controller(
            config=config,
            ai_provider=request.provider,
            use_agent=True
        )
        
        response = controller.chat_with_agent(request.message)
        
        return ChatResponse(
            message=response,
            provider=request.provider or config.get_default_provider(),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@router.post(
    "/chat/stream",
    summary="AI对话（流式）",
    description="与AI助手对话，流式返回响应",
)
async def chat_stream(request: ChatRequest):
    """AI对话（流式）"""
    try:
        config = get_config()
        provider = request.provider or config.get_default_provider()
        
        async def generate():
            try:
                controller = Controller(
                    config=config,
                    ai_provider=provider,
                    use_agent=True
                )
                
                # 获取完整响应
                response = controller.chat_with_agent(request.message)
                
                # 模拟流式输出（按句子分割）
                sentences = response.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').split('\n')
                
                for sentence in sentences:
                    if sentence.strip():
                        data = {
                            "type": "content",
                            "content": sentence,
                            "provider": provider,
                        }
                        yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.05)  # 小延迟模拟打字效果
                
                # 发送完成信号
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "error": str(e),
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")
