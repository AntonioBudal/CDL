"""Importar este pacote registra todos os modelos no metadata do SQLAlchemy."""

from app.models.audit_log import AuditLog
from app.models.book import Book
from app.models.canvas_frame import CanvasFrame
from app.models.category import Category, book_categories
from app.models.chapter import Chapter
from app.models.external_identity import ExternalIdentity
from app.models.friendship import Friendship
from app.models.local_credential import LocalCredential
from app.models.notification import Notification
from app.models.resource_permission import ResourcePermission
from app.models.search_history import SearchHistory
from app.models.study import Study
from app.models.study_canvas_node import StudyCanvasNode
from app.models.study_highlight import StudyHighlight
from app.models.study_mention import StudyMention
from app.models.study_relation import StudyRelation
from app.models.study_version import StudyVersion
from app.models.support_setting import SupportSetting
from app.models.user import User
from app.models.user_preference import UserPreference
from app.models.user_profile import UserProfile
from app.models.user_session import UserSession

__all__ = [
    "AuditLog",
    "Book",
    "CanvasFrame",
    "Category",
    "Chapter",
    "ExternalIdentity",
    "Friendship",
    "LocalCredential",
    "Notification",
    "ResourcePermission",
    "SearchHistory",
    "Study",
    "StudyCanvasNode",
    "StudyHighlight",
    "StudyMention",
    "StudyRelation",
    "StudyVersion",
    "SupportSetting",
    "User",
    "UserPreference",
    "UserProfile",
    "UserSession",
    "book_categories",
]




