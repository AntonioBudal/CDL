from __future__ import annotations

import logging
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.db.types import utc_now
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.friendship import Friendship
from app.models.resource_permission import ResourcePermission
from app.models.study import Study
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.sharing import (
    ResourcePermissionItem,
    ResourcePermissionsRead,
    SharedBookSummary,
    SharedStudySummary,
    VALID_BOOK_VISIBILITIES,
    VALID_STUDY_VISIBILITIES,
)
from app.services.friendship_service import is_blocked_between
from app.services import notification_service

logger = logging.getLogger(__name__)


def is_friends_between(session: Session, user_id_1: str, user_id_2: str) -> bool:
    """Verifica se há relacionamento de amizade aceita (mútua) entre os dois usuários."""
    if user_id_1 == user_id_2:
        return False
    u_a, u_b = Friendship.normalize_pair(user_id_1, user_id_2)
    friendship = session.scalar(
        select(Friendship).where(
            Friendship.user_id_a == u_a,
            Friendship.user_id_b == u_b,
            Friendship.status == "accepted",
        )
    )
    return friendship is not None


def resolve_effective_visibility(study: Study, book: Book | None) -> str:
    """Calcula a visibilidade efetiva de um estudo, resolvendo herança do livro pai se necessário."""
    if study.visibility != "inherit":
        return study.visibility
    if book is None:
        return "private"
    return book.visibility or "private"


def can_read_book(session: Session, user_id: str | None, book: Book) -> bool:
    """Determina se o usuário requisitante possui permissão de leitura sobre o livro.

    Regras:
    - Proprietário: acesso irrestrito.
    - Anônimo (sem user_id): acesso negado (Q3: A).
    - Bloqueio mútuo/unilateral: acesso negado incondicionalmente (404 anti-enumeração).
    - Público: permitido para qualquer usuário autenticado.
    - Amigos: permitido se houver amizade aceita.
    - Privado: apenas o proprietário.
    """
    if user_id is None:
        return False
    if user_id == book.user_id:
        return True
    if is_blocked_between(session, user_id, book.user_id):
        return False

    vis = book.visibility or "private"
    if vis == "public":
        return True
    if vis == "friends":
        return is_friends_between(session, user_id, book.user_id)
    return False


def can_read_study(
    session: Session,
    user_id: str | None,
    study: Study,
    book: Book | None = None,
) -> bool:
    """Determina se o usuário requisitante possui permissão de leitura sobre o estudo."""
    if user_id is None:
        return False
    if user_id == study.user_id:
        return True
    if is_blocked_between(session, user_id, study.user_id):
        return False

    if book is None:
        chapter = session.get(Chapter, study.chapter_id)
        if chapter is not None:
            book = session.get(Book, chapter.book_id)

    effective_vis = resolve_effective_visibility(study, book)

    if effective_vis == "public":
        return True
    if effective_vis == "friends":
        return is_friends_between(session, user_id, study.user_id)
    if effective_vis == "custom":
        # Verifica na ACL nominal
        perm = session.scalar(
            select(ResourcePermission).where(
                ResourcePermission.resource_type == "study",
                ResourcePermission.resource_id == study.id,
                ResourcePermission.granted_to_user_id == user_id,
                ResourcePermission.can_view == True,
            )
        )
        return perm is not None

    return False


def can_manage_study(user_id: str | None, study: Study) -> bool:
    """Apenas o proprietário pode editar, excluir ou gerenciar permissões do estudo."""
    return user_id is not None and user_id == study.user_id


def can_manage_book(user_id: str | None, book: Book) -> bool:
    """Apenas o proprietário pode editar, excluir ou gerenciar permissões do livro."""
    return user_id is not None and user_id == book.user_id


def update_study_visibility(session: Session, owner_id: str, study_id: int, new_visibility: str) -> Study:
    """Atualiza o nível de visibilidade de um estudo pelo proprietário."""
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudo não encontrado.")

    if not can_manage_study(owner_id, study):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudo não encontrado.")

    clean_vis = new_visibility.strip().lower()
    if clean_vis not in VALID_STUDY_VISIBILITIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Visibilidade inválida. Opções: {', '.join(sorted(VALID_STUDY_VISIBILITIES))}",
        )

    study.visibility = clean_vis
    session.flush()
    return study


def update_book_visibility(session: Session, owner_id: str, book_id: int, new_visibility: str) -> Book:
    """Atualiza o nível de visibilidade de um livro pelo proprietário."""
    book = session.get(Book, book_id)
    if book is None or book.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")

    if not can_manage_book(owner_id, book):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")

    clean_vis = new_visibility.strip().lower()
    if clean_vis not in VALID_BOOK_VISIBILITIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Visibilidade inválida. Opções: {', '.join(sorted(VALID_BOOK_VISIBILITIES))}",
        )

    book.visibility = clean_vis
    session.flush()
    return book


def grant_permission(
    session: Session,
    owner_id: str,
    resource_type: str,
    resource_id: int,
    target_username: str,
) -> ResourcePermission:
    """Concede permissão nominal de leitura a um leitor (@username) para o recurso."""
    if resource_type == "study":
        resource = session.get(Study, resource_id)
    elif resource_type == "book":
        resource = session.get(Book, resource_id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de recurso inválido.")

    if resource is None or resource.deleted_at is not None or resource.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso não encontrado.")

    clean_username = target_username.strip().lstrip("@").lower()
    target_user = session.scalar(
        select(User).where(func.lower(User.username) == clean_username)
    )
    if target_user is None or target_user.status != "ativo":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    if target_user.id == owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode conceder permissão para si mesmo.",
        )

    # Verifica se há bloqueio mútuo/unilateral (F06)
    if is_blocked_between(session, owner_id, target_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível conceder permissão para um usuário com bloqueio ativo.",
        )

    # Verifica duplicata
    existing = session.scalar(
        select(ResourcePermission).where(
            ResourcePermission.resource_type == resource_type,
            ResourcePermission.resource_id == resource_id,
            ResourcePermission.granted_to_user_id == target_user.id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este usuário já possui permissão de acesso para o recurso.",
        )

    perm = ResourcePermission(
        resource_type=resource_type,
        resource_id=resource_id,
        granted_to_user_id=target_user.id,
        can_view=True,
        created_at=utc_now(),
    )
    session.add(perm)
    session.flush()

    # Emissão de notificação study_shared (F09)
    owner = session.get(User, owner_id)
    resource_title = getattr(resource, "title", "Recurso")
    book_id: int | None = None
    book_title: str | None = None
    link: str

    if resource_type == "study":
        link = f"/estudos/{resource_id}"
        if getattr(resource, "chapter_id", None):
            ch = session.get(Chapter, resource.chapter_id)
            if ch and ch.book_id:
                bk = session.get(Book, ch.book_id)
                if bk:
                    book_id = bk.id
                    book_title = bk.title
    else:
        link = f"/livro/{resource_id}"
        book_id = resource_id
        book_title = resource_title

    owner_name = (owner.display_name or owner.username) if owner else "Alguém"
    notification_service.create_notification(
        session=session,
        user_id=target_user.id,
        actor_id=owner_id,
        event_type="study_shared",
        payload={
            "resource_type": resource_type,
            "resource_id": resource_id,
            "resource_title": resource_title,
            "book_id": book_id,
            "book_title": book_title,
            "shared_by_id": owner_id,
            "shared_by_username": owner.username if owner else "",
            "shared_by_display_name": owner_name,
            "link": link,
            "message": f"{owner_name} compartilhou o {'estudo' if resource_type == 'study' else 'livro'} '{resource_title}' com você.",
        },
    )

    session.refresh(perm)
    return perm


def revoke_permission(
    session: Session,
    owner_id: str,
    resource_type: str,
    resource_id: int,
    granted_to_user_id: str,
) -> None:
    """Revoga a permissão nominal de leitura de um usuário sobre o recurso."""
    if resource_type == "study":
        resource = session.get(Study, resource_id)
    elif resource_type == "book":
        resource = session.get(Book, resource_id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de recurso inválido.")

    if resource is None or resource.deleted_at is not None or resource.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso não encontrado.")

    perm = session.scalar(
        select(ResourcePermission).where(
            ResourcePermission.resource_type == resource_type,
            ResourcePermission.resource_id == resource_id,
            ResourcePermission.granted_to_user_id == granted_to_user_id,
        )
    )
    if perm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permissão não encontrada.")

    session.delete(perm)
    session.flush()


def get_resource_permissions_read(
    session: Session,
    owner_id: str,
    resource_type: str,
    resource_id: int,
) -> ResourcePermissionsRead:
    """Retorna o estado de visibilidade e as permissões nominais concedidas para o recurso."""
    if resource_type == "study":
        study = session.get(Study, resource_id)
        if study is None or study.deleted_at is not None or study.user_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudo não encontrado.")

        chapter = session.get(Chapter, study.chapter_id)
        book = session.get(Book, chapter.book_id) if chapter else None
        effective_vis = resolve_effective_visibility(study, book)
        vis = study.visibility
    elif resource_type == "book":
        book = session.get(Book, resource_id)
        if book is None or book.deleted_at is not None or book.user_id != owner_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
        effective_vis = book.visibility
        vis = book.visibility
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de recurso inválido.")

    stmt = (
        select(ResourcePermission)
        .options(
            joinedload(ResourcePermission.granted_to_user).joinedload(User.profile)
        )
        .where(
            ResourcePermission.resource_type == resource_type,
            ResourcePermission.resource_id == resource_id,
        )
        .order_by(ResourcePermission.created_at.desc())
    )
    perms = session.scalars(stmt).all()
    perm_items: list[ResourcePermissionItem] = []
    for p in perms:
        user = p.granted_to_user
        avatar = user.profile.avatar_url if hasattr(user, "profile") and user.profile else None
        perm_items.append(
            ResourcePermissionItem(
                user_id=user.id,
                username=user.username,
                display_name=user.display_name,
                avatar_url=avatar,
                created_at=p.created_at,
            )
        )

    return ResourcePermissionsRead(
        resource_type=resource_type,
        resource_id=resource_id,
        visibility=vis,
        effective_visibility=effective_vis,
        is_owner=True,
        permissions=perm_items,
    )


def get_study_permissions(session: Session, owner_id: str, study_id: int) -> ResourcePermissionsRead:
    """Atalho para obter permissões de um estudo."""
    return get_resource_permissions_read(session, owner_id, "study", study_id)


def get_book_permissions(session: Session, owner_id: str, book_id: int) -> ResourcePermissionsRead:
    """Atalho para obter permissões de um livro."""
    return get_resource_permissions_read(session, owner_id, "book", book_id)


def get_shared_studies_for_user(
    session: Session,
    user_id: str,
    query: str | None = None,
    author: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[SharedStudySummary], int]:
    """Retorna os estudos de terceiros que foram compartilhados com o usuário atual."""
    # 1. Obtém lista de amigos aceitos
    friend_ids: set[str] = set()
    f_stmt = select(Friendship).where(
        or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
        Friendship.status == "accepted",
    )
    for f in session.scalars(f_stmt).all():
        friend_ids.add(f.user_id_b if f.user_id_a == user_id else f.user_id_a)

    # 2. Obtém lista de usuários bloqueados (em qualquer direção)
    blocked_ids: set[str] = set()
    b_stmt = select(Friendship).where(
        or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
        Friendship.status == "blocked",
    )
    for f in session.scalars(b_stmt).all():
        blocked_ids.add(f.user_id_b if f.user_id_a == user_id else f.user_id_a)

    # 3. Obtém estudos com permissão nominal em resource_permissions
    perm_study_ids = set(
        session.scalars(
            select(ResourcePermission.resource_id).where(
                ResourcePermission.resource_type == "study",
                ResourcePermission.granted_to_user_id == user_id,
                ResourcePermission.can_view == True,
            )
        ).all()
    )

    # Monta a consulta de estudos
    stmt = (
        select(Study, Book, Chapter, User)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .join(Book, Chapter.book_id == Book.id)
        .join(User, Study.user_id == User.id)
        .options(joinedload(User.profile))
        .where(
            Study.deleted_at.is_(None),
            Book.deleted_at.is_(None),
            Study.user_id != user_id,
        )
    )

    if blocked_ids:
        stmt = stmt.where(Study.user_id.not_in(blocked_ids))

    if author:
        stmt = stmt.where(func.lower(User.username) == author.strip().lower())

    if query and query.strip():
        term = f"%{query.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Study.title).like(term),
                func.lower(Book.title).like(term),
                func.lower(User.username).like(term),
            )
        )

    # Condição de acesso compartilhado:
    # - Está na lista de permissões nominais (custom)
    # - OU Estudo é public
    # - OU (Estudo é inherit E Book é public)
    # - OU (Estudo é friends E autor é amigo)
    # - OU (Estudo é inherit E Book é friends E autor é amigo)
    access_conditions = []
    if perm_study_ids:
        access_conditions.append(Study.id.in_(perm_study_ids))

    access_conditions.append(Study.visibility == "public")
    access_conditions.append(
        (Study.visibility == "inherit") & (Book.visibility == "public")
    )

    if friend_ids:
        access_conditions.append(
            (Study.visibility == "friends") & (Study.user_id.in_(friend_ids))
        )
        access_conditions.append(
            (Study.visibility == "inherit")
            & (Book.visibility == "friends")
            & (Study.user_id.in_(friend_ids))
        )

    stmt = stmt.where(or_(*access_conditions))

    # Total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.scalar(count_stmt) or 0

    # Paginação e ordenação
    stmt = stmt.order_by(Study.updated_at.desc()).limit(limit).offset(offset)
    results = session.execute(stmt).all()

    items: list[SharedStudySummary] = []
    for study_obj, book_obj, chapter_obj, user_obj in results:
        avatar = user_obj.profile.avatar_url if hasattr(user_obj, "profile") and user_obj.profile else None
        eff_vis = resolve_effective_visibility(study_obj, book_obj)
        items.append(
            SharedStudySummary(
                id=study_obj.id,
                title=study_obj.title,
                book_id=book_obj.id,
                book_title=book_obj.title,
                chapter_id=chapter_obj.id if chapter_obj else None,
                chapter_name=chapter_obj.name if chapter_obj else None,
                owner_id=user_obj.id,
                owner_username=user_obj.username,
                owner_display_name=user_obj.display_name,
                owner_avatar_url=avatar,
                visibility=eff_vis,
                updated_at=study_obj.updated_at,
            )
        )

    return items, total


def get_shared_books_for_user(
    session: Session,
    user_id: str,
    query: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[SharedBookSummary], int]:
    """Retorna os livros de terceiros compartilhados com o usuário atual."""
    friend_ids: set[str] = set()
    f_stmt = select(Friendship).where(
        or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
        Friendship.status == "accepted",
    )
    for f in session.scalars(f_stmt).all():
        friend_ids.add(f.user_id_b if f.user_id_a == user_id else f.user_id_a)

    blocked_ids: set[str] = set()
    b_stmt = select(Friendship).where(
        or_(Friendship.user_id_a == user_id, Friendship.user_id_b == user_id),
        Friendship.status == "blocked",
    )
    for f in session.scalars(b_stmt).all():
        blocked_ids.add(f.user_id_b if f.user_id_a == user_id else f.user_id_a)

    stmt = (
        select(Book, User)
        .join(User, Book.user_id == User.id)
        .options(joinedload(User.profile))
        .where(
            Book.deleted_at.is_(None),
            Book.user_id != user_id,
        )
    )

    if blocked_ids:
        stmt = stmt.where(Book.user_id.not_in(blocked_ids))

    access_conditions = [Book.visibility == "public"]
    if friend_ids:
        access_conditions.append(
            (Book.visibility == "friends") & (Book.user_id.in_(friend_ids))
        )
    stmt = stmt.where(or_(*access_conditions))

    if query and query.strip():
        term = f"%{query.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Book.title).like(term),
                func.lower(User.username).like(term),
            )
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = session.scalar(count_stmt) or 0

    stmt = stmt.order_by(Book.updated_at.desc()).limit(limit).offset(offset)
    results = session.execute(stmt).all()

    items: list[SharedBookSummary] = []
    for book_obj, user_obj in results:
        avatar = user_obj.profile.avatar_url if hasattr(user_obj, "profile") and user_obj.profile else None
        items.append(
            SharedBookSummary(
                id=book_obj.id,
                title=book_obj.title,
                author=book_obj.author,
                subtitle=book_obj.subtitle,
                cover_image=book_obj.cover_image,
                owner_id=user_obj.id,
                owner_username=user_obj.username,
                owner_display_name=user_obj.display_name,
                owner_avatar_url=avatar,
                visibility=book_obj.visibility,
                updated_at=book_obj.updated_at,
            )
        )

    return items, total
