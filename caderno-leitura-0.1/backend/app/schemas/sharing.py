from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from app.schemas.common import InputModel, OutputModel

VALID_STUDY_VISIBILITIES = {"inherit", "private", "friends", "custom", "public"}
VALID_BOOK_VISIBILITIES = {"private", "friends", "public"}


class ResourceOwnerSummary(OutputModel):
    id: str
    username: str
    display_name: str
    avatar_url: str | None = None


class VisibilityUpdateRequest(InputModel):
    visibility: str = Field(description="Nível de visibilidade do recurso")

    @field_validator("visibility")
    @classmethod
    def validate_visibility(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in VALID_STUDY_VISIBILITIES:
            raise ValueError(
                f"Visibilidade inválida. Deve ser uma de: {', '.join(sorted(VALID_STUDY_VISIBILITIES))}"
            )
        return clean


class GrantPermissionRequest(InputModel):
    username: str = Field(min_length=1, max_length=50, description="Handle do usuário (@username)")

    @field_validator("username", mode="before")
    @classmethod
    def clean_username(cls, v: Any) -> str:
        if isinstance(v, str):
            v = v.strip().lstrip("@").lower()
            if len(v) < 1:
                raise ValueError("Informe o nome de usuário.")
            return v
        return v


class ResourcePermissionItem(OutputModel):
    user_id: str
    username: str
    display_name: str
    avatar_url: str | None = None
    created_at: datetime


class ResourcePermissionsRead(OutputModel):
    resource_type: str
    resource_id: int
    visibility: str
    effective_visibility: str
    is_owner: bool
    permissions: list[ResourcePermissionItem] = []


class SharedStudySummary(OutputModel):
    id: int
    title: str
    book_id: int
    book_title: str
    chapter_id: int | None = None
    chapter_name: str | None = None
    owner_id: str
    owner_username: str
    owner_display_name: str
    owner_avatar_url: str | None = None
    visibility: str
    updated_at: datetime


class SharedStudiesResponse(OutputModel):
    items: list[SharedStudySummary]
    total: int


class SharedBookSummary(OutputModel):
    id: int
    title: str
    author: str | None = None
    subtitle: str | None = None
    cover_image: str | None = None
    owner_id: str
    owner_username: str
    owner_display_name: str
    owner_avatar_url: str | None = None
    visibility: str
    updated_at: datetime


class SharedBooksResponse(OutputModel):
    items: list[SharedBookSummary]
    total: int
