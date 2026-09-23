"""Importar este pacote registra todos os modelos no metadata do SQLAlchemy."""

from app.models.book import Book
from app.models.canvas_frame import CanvasFrame
from app.models.category import Category, book_categories
from app.models.chapter import Chapter
from app.models.external_identity import ExternalIdentity
from app.models.local_credential import LocalCredential
from app.models.search_history import SearchHistory
from app.models.study import Study
from app.models.study_canvas_node import StudyCanvasNode
from app.models.study_relation import StudyRelation
from app.models.user import User
from app.models.user_session import UserSession

__all__ = [
    "Book",
    "CanvasFrame",
    "Category",
    "Chapter",
    "ExternalIdentity",
    "LocalCredential",
    "SearchHistory",
    "Study",
    "StudyCanvasNode",
    "StudyRelation",
    "User",
    "UserSession",
    "book_categories",
]


