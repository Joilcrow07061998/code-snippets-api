import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_current_user
from src.db.session import get_db
from src.models.snippet import Snippet
from src.models.user import User
from src.schemas.snippet import SnippetCreate, SnippetRead, SnippetUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=SnippetRead, status_code=status.HTTP_201_CREATED)
async def create_snippet(
    payload: SnippetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Snippet:
    snippet = Snippet(**payload.model_dump(), owner_id=current_user.id)
    db.add(snippet)
    await db.commit()
    await db.refresh(snippet)
    logger.info("Snippet %s created by user %s", snippet.share_id, current_user.id)
    return snippet


@router.get("", response_model=list[SnippetRead])
async def list_my_snippets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Snippet]:
    result = await db.scalars(
        select(Snippet).where(Snippet.owner_id == current_user.id).order_by(Snippet.created_at.desc())
    )
    return list(result.all())


@router.get("/shared/{share_id}", response_model=SnippetRead)
async def get_shared_snippet(share_id: UUID, db: AsyncSession = Depends(get_db)) -> Snippet:
    snippet = await db.scalar(select(Snippet).where(Snippet.share_id == share_id))
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
    snippet = await _get_owned_snippet(db, snippet_id, current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(snippet, field, value)
    await db.commit()
    await db.refresh(snippet)
    logger.info("Snippet %s updated by user %s", snippet.id, current_user.id)
    return snippet


@router.delete("/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snippet(
    snippet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    snippet = await _get_owned_snippet(db, snippet_id, current_user.id)
    await db.delete(snippet)
    await db.commit()
    logger.info("Snippet %s deleted by user %s", snippet_id, current_user.id)


async def _get_owned_snippet(db: AsyncSession, snippet_id: int, user_id: int) -> Snippet:
    snippet = await db.scalar(
        select(Snippet).where(Snippet.id == snippet_id, Snippet.owner_id == user_id)
    )
    if snippet is None:
        # чужой сниппет не раскрываем, как и несуществующий
        raise HTTPException(status_code=404, detail="Snippet not found")
    return snippet
