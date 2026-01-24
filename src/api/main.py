"""
Smart File Tidy API - FastAPI 入口
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import scan, organize, history, config, backup, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("Smart File Tidy API 启动中...")
    yield
    # 关闭时清理
    print("Smart File Tidy API 关闭中...")


app = FastAPI(
    title="Smart File Tidy API",
    description="智能文件整理助手 API - 基于 AI 的文件分类和整理服务",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(scan.router, prefix="/api/v1/scan", tags=["扫描"])
app.include_router(organize.router, prefix="/api/v1/organize", tags=["整理"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(history.router, prefix="/api/v1/history", tags=["历史"])
app.include_router(backup.router, prefix="/api/v1/backup", tags=["备份"])
app.include_router(config.router, prefix="/api/v1/config", tags=["配置"])


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "Smart File Tidy API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}
