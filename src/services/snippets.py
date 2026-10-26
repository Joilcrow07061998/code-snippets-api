from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.snippet import Snippet
from src.schemas.snippet import SnippetCreate, SnippetUpdate


async def create_snippet(
    db: AsyncSession,
    owner_id: int,
    payload: SnippetCreate,
) -> Snippet:
    snippet = Snippet(**payload.model_dump(), owner_id=owner_id)
    db.add(snippet)
    await db.commit()
    await db.refresh(snippet)
    return snippet


async def list_user_snippets(db: AsyncSession, owner_id: int) -> list[Snippet]:
    result = await db.scalars(
        select(Snippet)
        .where(Snippet.owner_id == owner_id)
        .order_by(Snippet.created_at.desc())
    )
    return list(result.all())


async def get_shared_snippet(db: AsyncSession, share_id: UUID) -> Snippet | None:
    return await db.scalar(select(Snippet).where(Snippet.share_id == share_id))


async def get_owned_snippet(
    db: AsyncSession,
    snippet_id: int,
    owner_id: int,
) -> Snippet | None:
    return await db.scalar(
        select(Snippet).where(Snippet.id == snippet_id, Snippet.owner_id == owner_id)
    )


async def update_snippet(
    db: AsyncSession,
    snippet: Snippet,
    payload: SnippetUpdate,
) -> Snippet:
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(snippet, field, value)
    await db.commit()
    await db.refresh(snippet)
    return snippet


async def delete_snippet(db: AsyncSession, snippet: Snippet) -> None:
    await db.delete(snippet)
    await db.commit()
