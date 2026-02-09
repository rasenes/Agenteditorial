from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agent.orchestrator import orchestrator
from .api.routes_admin import router as admin_router
from .api.routes_generate import router as generate_router
from .api.routes_memory import router as memory_router
from .api.routes_trends import router as trends_router
from .core.config import SETTINGS
from .core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting Editorial Agent v%s", SETTINGS.app.version)
    await orchestrator.fetch_trends(limit=20, force_refresh=True)
    yield
    logger.info("Stopping Editorial Agent")


app = FastAPI(
    title=SETTINGS.app.app_name,
    version=SETTINGS.app.version,
    lifespan=lifespan,
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base = SETTINGS.api.prefix
app.include_router(generate_router, prefix=f"{base}/generate", tags=["generate"])
app.include_router(trends_router, prefix=f"{base}/trends", tags=["trends"])
app.include_router(memory_router, prefix=f"{base}/memory", tags=["memory"])
app.include_router(admin_router, prefix=f"{base}/admin", tags=["admin"])


@app.get("/")
async def root():
    return {
        "name": SETTINGS.app.app_name,
        "version": SETTINGS.app.version,
        "docs": "/docs",
        "api_prefix": SETTINGS.api.prefix,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": SETTINGS.app.app_name}
