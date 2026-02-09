from __future__ import annotations

"""FastAPI entrypoint.

Supports 2 launch modes:
1) From repo root (recommended):
   `python -m uvicorn backend.main:app --reload`
2) From the backend/ folder (works too):
   `python -m uvicorn main:app --reload`

This file uses absolute imports (`backend.*`) for stability.
"""

from contextlib import asynccontextmanager

# If imported as a top-level module (e.g. `uvicorn main:app` from backend/),
# relative imports would fail because Python doesn't know the parent package.
# Add repo root to sys.path to keep startup robust.
if __package__ in (None, ""):
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.agent.orchestrator import orchestrator
from backend.api.routes_admin import router as admin_router
from backend.api.routes_generate import router as generate_router
from backend.api.routes_memory import router as memory_router
from backend.api.routes_trends import router as trends_router
from backend.core.config import SETTINGS
from backend.core.logger import get_logger

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
