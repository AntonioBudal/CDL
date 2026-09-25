from __future__ import annotations

from datetime import datetime
from enum import Enum
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.-]{3,30}$")


class VisibilityLevel(str, Enum):
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"


class ProfileReadingStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_books: int = 0
    total_studies: int = 0
    current_streak_days: int = 0


class UserProfilePublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None
    profile_visibility: VisibilityLevel
    is_private: bool = False
    reading_stats: ProfileReadingStats | None = None
    created_at: datetime


class UserProfilePrivateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str
    display_name: str
    email: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    profile_visibility: VisibilityLevel
    dashboard_visibility: VisibilityLevel
    is_discoverable: bool
    show_reading_stats: bool
    has_google_avatar: bool = False
    google_avatar_url: str | None = None
    reading_stats: ProfileReadingStats
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=30)
    display_name: str | None = Field(default=None, min_length=1, max_length=60)
    bio: str | None = Field(default=None, max_length=280)
    profile_visibility: VisibilityLevel | None = None
    dashboard_visibility: VisibilityLevel | None = None
    is_discoverable: bool | None = None
    show_reading_stats: bool | None = None
    use_google_avatar: bool | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not USERNAME_REGEX.match(v):
                raise ValueError("O nome de usuário deve conter de 3 a 30 caracteres alfanuméricos, hífens ou pontos.")
        return v

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                raise ValueError("O nome de exibição não pode estar em branco.")
        return v


class UserSearchItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    display_name: str
    avatar_url: str | None = None
    bio: str | None = None


class AvatarResponse(BaseModel):
    avatar_url: str | None = None
