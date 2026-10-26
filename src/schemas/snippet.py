from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SnippetCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    code: str = Field(min_length=1)
    language: str = Field(default="text", min_length=1, max_length=60)


class SnippetUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    code: str | None = Field(default=None, min_length=1)
    language: str | None = Field(default=None, min_length=1, max_length=60)


class SnippetRead(BaseModel):
    id: int
    share_id: UUID
    title: str
    code: str
    language: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
