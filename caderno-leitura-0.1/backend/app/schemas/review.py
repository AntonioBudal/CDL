from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import InputModel, OutputModel, RecordId

ReviewRating = Literal["easy", "medium", "hard"]
# Baldes da revisão (F0.10.04): "new" = nunca avaliado; os demais = última avaliação.
ReviewBucket = Literal["new", "hard", "medium", "easy"]


class ReviewRecordRequest(InputModel):
    rating: ReviewRating


class ReviewRecordResponse(OutputModel):
    id: RecordId
    last_reviewed_at: datetime
    review_count: int
    last_rating: ReviewRating


class ConceptCardDefinition(OutputModel):
    text: str
    study_id: RecordId
    study_title: str
    book_title: str
    chapter_name: str


class FragileConcept(OutputModel):
    key: str
    term: str
    weight: float
    reason: Literal["card", "questions"]


class ConceptRecordResponse(OutputModel):
    concept_key: str
    last_reviewed_at: datetime
    review_count: int
    last_rating: ReviewRating
    difficulty_weight: float


class OcclusionRegion(OutputModel):
    """F0.12.06: retângulo de um cartão de imagem, em coordenadas relativas (0–1)."""
    id: RecordId
    x: float
    y: float
    width: float
    height: float


class ReviewItemRead(OutputModel):
    id: RecordId
    study_id: RecordId
    study_title: str
    book_id: RecordId
    book_title: str
    chapter_id: RecordId
    chapter_name: str
    kind: str
    section: str
    question_text: str
    expected_answer: str
    context_prefix: str = ""
    context_suffix: str = ""
    last_reviewed_at: datetime | None = None
    review_count: int = 0
    last_rating: ReviewRating | None = None
    # F0.11.08
    difficulty_weight: float | None = None
    concept_key: str | None = None
    definitions: list[ConceptCardDefinition] = Field(default_factory=list)
    # F0.12.06: cartão de imagem (kind "image"): a imagem, o retângulo perguntado e todos os da mesma imagem
    media_id: str | None = None
    occlusion_id: RecordId | None = None
    regions: list[OcclusionRegion] = Field(default_factory=list)


class ReviewBookItem(OutputModel):
    book_id: RecordId
    title: str
    items_count: int


class ReviewBucketCounts(OutputModel):
    new: int = 0
    hard: int = 0
    medium: int = 0
    easy: int = 0


class ReviewStatsResponse(OutputModel):
    total_eligible: int
    total_questions: int
    total_hidden: int
    total_images: int = 0  # F0.12.06
    reviewed_today: int
    pending_review: int
    books: list[ReviewBookItem] = Field(default_factory=list)
    buckets: ReviewBucketCounts = Field(default_factory=ReviewBucketCounts)
