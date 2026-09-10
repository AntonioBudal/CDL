"""Importar este pacote registra todos os modelos no metadata do SQLAlchemy."""

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.study import Study

__all__ = ["Book", "Chapter", "Study"]
