from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1.router import api_router
from src.core.config import settings
from src.core.exceptions import unexpected_error_handler
from src.core.logging import configure_logging
from src.db.session import engine
from src.models import Snippet, User  # noqa: F401

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
    description="Save code snippets and share them with a public UUID link.",
    lifespan=lifespan,
)
app.add_exception_handler(Exception, unexpected_error_handler)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
