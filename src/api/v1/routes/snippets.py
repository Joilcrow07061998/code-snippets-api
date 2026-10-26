import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_current_user
from src.db.session import get_db
from src.models.snippet import Snippet
from src.models.user import User
from src.schemas.snippet import SnippetCreate, SnippetRead, SnippetUpdate
from src.services.snippets import (
    create_snippet as create_snippet_service,
    delete_snippet as delete_snippet_service,
    get_owned_snippet,
    get_shared_snippet as get_shared_snippet_service,
    list_user_snippets,
    update_snippet as update_snippet_service,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=SnippetRead, status_code=status.HTTP_201_CREATED)
async def create_snippet(
    payload: SnippetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Snippet:
    snippet = await create_snippet_service(db, current_user.id, payload)
    logger.info("Snippet %s created by user %s", snippet.share_id, current_user.id)
    return snippet


@router.get("", response_model=list[SnippetRead])
async def list_my_snippets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Snippet]:
    return await list_user_snippets(db, current_user.id)


@router.get("/shared/{share_id}", response_model=SnippetRead)
async def get_shared_snippet(
    share_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Snippet:
    snippet = await get_shared_snippet_service(db, share_id)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return snippet


@router.patch("/{snippet_id}", response_model=SnippetRead)
async def update_snippet(
    snippet_id: int,
    payload: SnippetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Snippet:
    snippet = await get_owned_snippet(db, snippet_id, current_user.id)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")
    snippet = await update_snippet_service(db, snippet, payload)
    logger.info("Snippet %s updated by user %s", snippet.id, current_user.id)
    return snippet


@router.delete("/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snippet(
    snippet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    snippet = await get_owned_snippet(db, snippet_id, current_user.id)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")
    await delete_snippet_service(db, snippet)
    logger.info("Snippet %s deleted by user %s", snippet_id, current_user.id)
