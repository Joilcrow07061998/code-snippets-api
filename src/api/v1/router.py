from fastapi import APIRouter

from src.api.v1.routes.auth import router as auth_router
from src.api.v1.routes.snippets import router as snippets_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(snippets_router, prefix="/snippets", tags=["snippets"])
