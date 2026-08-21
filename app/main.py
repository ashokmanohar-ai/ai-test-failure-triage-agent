from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.routes import router
from app.observability import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    yield


app = FastAPI(title="AI Test Failure Triage Agent", version=__version__, lifespan=lifespan)
app.include_router(router)


@app.get("/")
def index() -> dict[str, str]:
    return {"name": "AI Test Failure Triage Agent", "docs": "/docs", "health": "/api/v1/health"}
