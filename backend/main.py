"""
API FastAPI pour l'Editorial Agent.
Routes : generation, trends, memory, admin.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from .core.config import CONFIG
from .core.logger import get_logger
from .agent.orchestrator import orchestrator

# Logging
logger = get_logger(__name__)

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Editorial Agent...")
    await orchestrator.initialize()
    logger.info("Editorial Agent ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Editorial Agent...")


# FastAPI app
app = FastAPI(
    title="Editorial Agent IA",
    description="Agent IA pour générer des tweets viraux",
    version=CONFIG.version,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
from .api.routes_generate import router as generate_router
from .api.routes_trends import router as trends_router
from .api.routes_memory import router as memory_router
from .api.routes_admin import router as admin_router

app.include_router(generate_router, prefix=f"{CONFIG.api_prefix}/generate", tags=["generate"])
app.include_router(trends_router, prefix=f"{CONFIG.api_prefix}/trends", tags=["trends"])
app.include_router(memory_router, prefix=f"{CONFIG.api_prefix}/memory", tags=["memory"])
app.include_router(admin_router, prefix=f"{CONFIG.api_prefix}/admin", tags=["admin"])


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": CONFIG.app_name,
        "version": CONFIG.version,
    }


@app.get("/")
async def root():
    """API root."""
    return {
        "app": CONFIG.app_name,
        "version": CONFIG.version,
        "docs": "/docs",
        "api": f"{CONFIG.api_prefix}",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=CONFIG.api_host,
        port=CONFIG.api_port,
        log_level=CONFIG.log_level.lower(),
    )
