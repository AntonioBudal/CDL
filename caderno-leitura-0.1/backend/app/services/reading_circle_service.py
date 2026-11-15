"""F0.12.07 (spec 120): círculos de leitura com trava anti-spoiler.

Regras centrais:
- Só **amigos** são convidados (e nunca quem tem bloqueio com quem convida); quem não é membro ativo recebe 404.
- Progresso = posição da parte atual (0 = não comecei) ou ``finished``. Uma parte é **visível** para quem está nela ou
  adiante. A trava é aplicada **aqui**, numa única função (``_visible``): a resposta nunca traz o texto de uma parte
  trancada, só a contagem.
- Bloqueio entre dois membros: cada um deixa de ver as mensagens do outro.
- Partes só crescem no fim; apagar só a última e só sem mensagens.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models import Book, Chapter, ReadingCircle, ReadingCircleMember, ReadingCirclePart, ReadingCirclePost, User
from app.services.friendship_service import get_blocked_user_ids_bilateral, is_blocked_between
from app.services.in_common_service import _authors_compatible, normalize_title_key
from app.services.persistence import commit_changes
from app.services.sharing_service import is_friends_between

MAX_MEMBERS = 20
MAX_PARTS = 100
MAX_CIRCLES = 50
MAX_BODY = 4000
MAX_NAME = 120
MAX_PART_NAME = 200


def _error(code: int, detail: str) -> HTTPException:
    return HTTPException(status_code=code, detail=detail)


def _not_found() -> HTTPException:
    return _error(status.HTTP_404_NOT_FOUND, "Círculo não encontrado.")


def _clean(text: str | None, limit: int, what: str) -> str:
    value = " ".join((text or "").split())
    if not value:
        raise _error(422, f"Informe {what}.")
    return value[:limit]


# --- Acesso ---------------------------------------------------------------------------------------------------------


def _membership(session: Session, circle_id: int, user_id: str) -> ReadingCircleMember | None:
    return session.scalar(
        select(ReadingCircleMember).where(
            ReadingCircleMember.circle_id == circle_id, ReadingCircleMember.user_id == user_id
        )
    )


def _active(session: Session, circle_id: int, user_id: str) -> tuple[ReadingCircle, ReadingCircleMember]:
    circle = session.get(ReadingCircle, circle_id)
    member = _membership(session, circle_id, user_id) if circle else None
    if circle is None or member is None or member.status != "active":
        raise _not_found()
    return circle, member


def _owner(session: Session, circle_id: int, user_id: str) -> tuple[ReadingCircle, ReadingCircleMember]:
    circle, member = _active(session, circle_id, user_id)
    if member.role != "owner":
        raise _error(status.HTTP_403_FORBIDDEN, "Só quem criou o círculo pode fazer isso.")
    return circle, member


def _parts(session: Session, circle_id: int) -> list[ReadingCirclePart]:
    return list(session.scalars(
        select(ReadingCirclePart).where(ReadingCirclePart.circle_id == circle_id).order_by(ReadingCirclePart.position)
    ).all())


def _visible(member: ReadingCircleMember, part: ReadingCirclePart) -> bool:
    """A trava anti-spoiler: a parte só abre para quem está nela ou adiante."""
    return member.finished or member.progress >= part.position


def _user_brief(user: User | None) -> dict:
    if user is None:
        return {"id": None, "username": "", "display_name": "Leitor removido"}
    return {"id": user.id, "username": user.username, "display_name": user.display_name or user.username}


# --- Exemplar do leitor ---------------------------------------------------------------------------------------------


def _my_copy(session: Session, user_id: str, circle: ReadingCircle) -> int | None:
    """Livro do próprio leitor que casa com o do círculo (ISBN, ou título + sobrenome do autor)."""
    books = session.execute(
        select(Book.id, Book.title, Book.author, Book.isbn)
        .where(Book.user_id == user_id, Book.deleted_at.is_(None))
        .order_by(Book.id)
    ).all()
    if circle.isbn:
        for book_id, _, _, isbn in books:
            if isbn and isbn == circle.isbn:
                return book_id
    key = normalize_title_key(circle.book_title)
    if not key:
        return None
    for book_id, title, author, _ in books:
        if normalize_title_key(title) == key and _authors_compatible(author, circle.book_author):
            return book_id
    return None


# --- Listas e detalhe -----------------------------------------------------------------------------------------------


def invite_count(session: Session, user_id: str) -> int:
    return session.scalar(
        select(func.count(ReadingCircleMember.id)).where(
            ReadingCircleMember.user_id == user_id, ReadingCircleMember.status == "invited"
        )
    ) or 0


def list_circles(session: Session, user_id: str) -> dict:
    rows = session.execute(
        select(ReadingCircle, ReadingCircleMember)
        .join(ReadingCircleMember, ReadingCircleMember.circle_id == ReadingCircle.id)
        .where(ReadingCircleMember.user_id == user_id)
        .order_by(ReadingCircle.updated_at.desc(), ReadingCircle.id.desc())
    ).all()
    circles, invites = [], []
    for circle, member in rows:
        if member.status == "invited":
            inviter = session.get(User, member.invited_by) if member.invited_by else None
            invites.append({
                "id": circle.id, "name": circle.name, "book_title": circle.book_title,
                "book_author": circle.book_author, "invited_by": _user_brief(inviter),
            })
            continue
        parts = session.scalar(select(func.count(ReadingCirclePart.id)).where(ReadingCirclePart.circle_id == circle.id))
        members = session.scalar(select(func.count(ReadingCircleMember.id)).where(
            ReadingCircleMember.circle_id == circle.id, ReadingCircleMember.status == "active"))
        circles.append({
            "id": circle.id, "name": circle.name, "book_title": circle.book_title, "book_author": circle.book_author,
            "role": member.role, "member_count": members or 0, "part_count": parts or 0,
            "progress": member.progress, "finished": member.finished,
        })
    return {"circles": circles, "invites": invites}


def circle_detail(session: Session, user_id: str, circle_id: int) -> dict:
    circle, me = _active(session, circle_id, user_id)
    parts = _parts(session, circle.id)
    counts = dict(session.execute(
        select(ReadingCirclePost.part_id, func.count(ReadingCirclePost.id))
        .where(ReadingCirclePost.circle_id == circle.id).group_by(ReadingCirclePost.part_id)
    ).all())
    members = session.execute(
        select(ReadingCircleMember, User).join(User, User.id == ReadingCircleMember.user_id)
        .where(ReadingCircleMember.circle_id == circle.id)
        .order_by(ReadingCircleMember.role.desc(), ReadingCircleMember.created_at, ReadingCircleMember.id)
    ).all()
    return {
        "id": circle.id,
        "name": circle.name,
        "book_title": circle.book_title,
        "book_author": circle.book_author,
        "isbn": circle.isbn,
        "role": me.role,
        "progress": me.progress,
        "finished": me.finished,
        "my_book_id": _my_copy(session, user_id, circle),
        "parts": [
            {"id": p.id, "position": p.position, "name": p.name, "post_count": counts.get(p.id, 0),
             "visible": _visible(me, p)}
            for p in parts
        ],
        "members": [
            {**_user_brief(user), "role": m.role, "status": m.status, "progress": m.progress, "finished": m.finished}
            for m, user in members
            if m.status == "active" or me.role == "owner"
        ],
    }


# --- Criar, convidar, entrar e sair ---------------------------------------------------------------------------------


def create_circle(session: Session, user_id: str, book_id: int, name: str | None) -> dict:
    book = session.get(Book, book_id)
    if book is None or book.user_id != user_id or book.deleted_at is not None:
        raise _error(status.HTTP_404_NOT_FOUND, "Livro não encontrado.")
    mine = session.scalar(select(func.count(ReadingCircleMember.id)).where(
        ReadingCircleMember.user_id == user_id, ReadingCircleMember.status == "active")) or 0
    if mine >= MAX_CIRCLES:
        raise _error(422, f"No máximo {MAX_CIRCLES} círculos por leitor.")
    circle = ReadingCircle(
        owner_id=user_id, name=_clean(name or book.title, MAX_NAME, "o nome do círculo"),
        book_title=book.title, book_author=book.author, isbn=book.isbn, source_book_id=book.id,
    )
    session.add(circle)
    session.flush()
    chapters = session.scalars(
        select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.position, Chapter.id)
    ).all()
    names = [c.name for c in chapters if (c.name or "").strip()][:MAX_PARTS] or ["Parte 1"]
    for position, part_name in enumerate(names, start=1):
        session.add(ReadingCirclePart(circle_id=circle.id, position=position,
                                      name=_clean(part_name, MAX_PART_NAME, "o nome da parte")))
    session.add(ReadingCircleMember(circle_id=circle.id, user_id=user_id, role="owner", status="active",
                                    joined_at=utc_now()))
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


def invitable_friends(session: Session, user_id: str, circle_id: int) -> list[dict]:
    circle, _ = _owner(session, circle_id, user_id)
    taken = set(session.scalars(select(ReadingCircleMember.user_id).where(
        ReadingCircleMember.circle_id == circle.id)).all())
    from app.services.friendship_service import get_user_friends

    result = []
    for item in get_user_friends(session, user_id):
        friend = getattr(item, "user", None) or item
        friend_id = getattr(friend, "id", None)
        if friend_id and friend_id not in taken:
            result.append({"id": friend_id, "username": friend.username,
                           "display_name": getattr(friend, "display_name", None) or friend.username})
    return result


def invite(session: Session, user_id: str, circle_id: int, username: str) -> dict:
    circle, _ = _owner(session, circle_id, user_id)
    target = session.scalar(select(User).where(func.lower(User.username) == (username or "").strip().lower()))
    if target is None or target.id == user_id or is_blocked_between(session, user_id, target.id):
        raise _error(status.HTTP_404_NOT_FOUND, "Leitor não encontrado.")
    if not is_friends_between(session, user_id, target.id):
        raise _error(422, "Só dá para convidar amigos.")
    if _membership(session, circle.id, target.id) is not None:
        raise _error(409, "Este leitor já está no círculo ou já foi convidado.")
    total = session.scalar(select(func.count(ReadingCircleMember.id)).where(
        ReadingCircleMember.circle_id == circle.id)) or 0
    if total >= MAX_MEMBERS:
        raise _error(422, f"No máximo {MAX_MEMBERS} membros por círculo.")
    session.add(ReadingCircleMember(circle_id=circle.id, user_id=target.id, role="member", status="invited",
                                    invited_by=user_id))
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


def _invitation(session: Session, user_id: str, circle_id: int) -> tuple[ReadingCircle, ReadingCircleMember]:
    circle = session.get(ReadingCircle, circle_id)
    member = _membership(session, circle_id, user_id) if circle else None
    if circle is None or member is None or member.status != "invited":
        raise _error(status.HTTP_404_NOT_FOUND, "Convite não encontrado.")
    return circle, member


def accept(session: Session, user_id: str, circle_id: int) -> dict:
    circle, member = _invitation(session, user_id, circle_id)
    if is_blocked_between(session, user_id, circle.owner_id):
        raise _error(status.HTTP_404_NOT_FOUND, "Convite não encontrado.")
    member.status = "active"
    member.joined_at = utc_now()
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


def decline(session: Session, user_id: str, circle_id: int) -> None:
    _, member = _invitation(session, user_id, circle_id)
    session.delete(member)
    commit_changes(session)


def leave(session: Session, user_id: str, circle_id: int) -> None:
    _, member = _active(session, circle_id, user_id)
    if member.role == "owner":
        raise _error(422, "Quem criou o círculo não pode sair; apague o círculo se quiser encerrá-lo.")
    session.delete(member)
    commit_changes(session)


def remove_member(session: Session, user_id: str, circle_id: int, member_user_id: str) -> dict:
    circle, _ = _owner(session, circle_id, user_id)
    target = _membership(session, circle.id, member_user_id)
    if target is None or target.role == "owner":
        raise _error(status.HTTP_404_NOT_FOUND, "Membro não encontrado.")
    session.delete(target)
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


def delete_circle(session: Session, user_id: str, circle_id: int) -> None:
    circle, _ = _owner(session, circle_id, user_id)
    # Apaga explicitamente (não depende de PRAGMA foreign_keys).
    for model in (ReadingCirclePost, ReadingCircleMember, ReadingCirclePart):
        session.execute(delete(model).where(model.circle_id == circle.id))
    session.delete(circle)
    commit_changes(session)


def rename(session: Session, user_id: str, circle_id: int, name: str) -> dict:
    circle, _ = _owner(session, circle_id, user_id)
    circle.name = _clean(name, MAX_NAME, "o nome do círculo")
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


# --- Progresso e partes ---------------------------------------------------------------------------------------------


def set_progress(session: Session, user_id: str, circle_id: int, progress: int, finished: bool) -> dict:
    circle, member = _active(session, circle_id, user_id)
    total = len(_parts(session, circle.id))
    if progress < 0 or progress > total:
        raise _error(422, "Parte inválida.")
    member.finished = bool(finished)
    member.progress = total if finished else progress
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


def add_part(session: Session, user_id: str, circle_id: int, name: str) -> dict:
    circle, _ = _owner(session, circle_id, user_id)
    parts = _parts(session, circle.id)
    if len(parts) >= MAX_PARTS:
        raise _error(422, f"No máximo {MAX_PARTS} partes por círculo.")
    session.add(ReadingCirclePart(circle_id=circle.id, position=len(parts) + 1,
                                  name=_clean(name, MAX_PART_NAME, "o nome da parte")))
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


def _part(session: Session, circle_id: int, part_id: int) -> ReadingCirclePart:
    part = session.get(ReadingCirclePart, part_id)
    if part is None or part.circle_id != circle_id:
        raise _error(status.HTTP_404_NOT_FOUND, "Parte não encontrada.")
    return part


def rename_part(session: Session, user_id: str, circle_id: int, part_id: int, name: str) -> dict:
    circle, _ = _owner(session, circle_id, user_id)
    _part(session, circle.id, part_id).name = _clean(name, MAX_PART_NAME, "o nome da parte")
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


def delete_part(session: Session, user_id: str, circle_id: int, part_id: int) -> dict:
    circle, _ = _owner(session, circle_id, user_id)
    part = _part(session, circle.id, part_id)
    parts = _parts(session, circle.id)
    if part.position != len(parts) or len(parts) == 1:
        raise _error(422, "Só dá para apagar a última parte (e o círculo precisa de ao menos uma).")
    if session.scalar(select(func.count(ReadingCirclePost.id)).where(ReadingCirclePost.part_id == part.id)):
        raise _error(409, "Esta parte tem mensagens; ela não pode ser apagada.")
    session.delete(part)
    for member in session.scalars(select(ReadingCircleMember).where(ReadingCircleMember.circle_id == circle.id)):
        member.progress = min(member.progress, len(parts) - 1)
    commit_changes(session)
    return circle_detail(session, user_id, circle.id)


# --- Mensagens ------------------------------------------------------------------------------------------------------


def _post_payload(post: ReadingCirclePost, author: User | None, viewer_id: str, viewer_role: str) -> dict:
    return {
        "id": post.id, "part_id": post.part_id, "body": post.body, "author": _user_brief(author),
        "created_at": post.created_at, "edited_at": post.edited_at,
        "can_edit": post.author_id == viewer_id,
        "can_delete": post.author_id == viewer_id or viewer_role == "owner",
    }


def part_posts(session: Session, user_id: str, circle_id: int, part_id: int) -> dict:
    circle, me = _active(session, circle_id, user_id)
    part = _part(session, circle.id, part_id)
    total = session.scalar(select(func.count(ReadingCirclePost.id)).where(ReadingCirclePost.part_id == part.id)) or 0
    if not _visible(me, part):
        return {"part_id": part.id, "locked": True, "count": total, "posts": []}
    blocked = get_blocked_user_ids_bilateral(session, user_id)
    rows = session.execute(
        select(ReadingCirclePost, User).outerjoin(User, User.id == ReadingCirclePost.author_id)
        .where(ReadingCirclePost.part_id == part.id)
        .order_by(ReadingCirclePost.created_at, ReadingCirclePost.id)
    ).all()
    posts = [_post_payload(p, u, user_id, me.role) for p, u in rows if p.author_id not in blocked]
    return {"part_id": part.id, "locked": False, "count": total, "posts": posts}


def _body(text: str) -> str:
    value = (text or "").strip()
    if not value:
        raise _error(422, "Escreva a mensagem.")
    if len(value) > MAX_BODY:
        raise _error(422, f"No máximo {MAX_BODY} caracteres.")
    return value


def create_post(session: Session, user_id: str, circle_id: int, part_id: int, body: str) -> dict:
    circle, me = _active(session, circle_id, user_id)
    part = _part(session, circle.id, part_id)
    if not _visible(me, part):
        raise _error(403, "Avance seu progresso até esta parte para escrever nela.")
    session.add(ReadingCirclePost(circle_id=circle.id, part_id=part.id, author_id=user_id, body=_body(body)))
    circle.updated_at = utc_now()
    commit_changes(session)
    return part_posts(session, user_id, circle.id, part.id)


def _own_post(session: Session, circle_id: int, post_id: int) -> ReadingCirclePost:
    post = session.get(ReadingCirclePost, post_id)
    if post is None or post.circle_id != circle_id:
        raise _error(status.HTTP_404_NOT_FOUND, "Mensagem não encontrada.")
    return post


def edit_post(session: Session, user_id: str, circle_id: int, post_id: int, body: str) -> dict:
    circle, _ = _active(session, circle_id, user_id)
    post = _own_post(session, circle.id, post_id)
    if post.author_id != user_id:
        raise _error(403, "Só quem escreveu pode editar.")
    post.body = _body(body)
    post.edited_at = utc_now()
    commit_changes(session)
    return part_posts(session, user_id, circle.id, post.part_id)


def delete_post(session: Session, user_id: str, circle_id: int, post_id: int) -> dict:
    circle, me = _active(session, circle_id, user_id)
    post = _own_post(session, circle.id, post_id)
    if post.author_id != user_id and me.role != "owner":
        raise _error(403, "Só quem escreveu (ou quem criou o círculo) pode apagar.")
    part_id = post.part_id
    session.delete(post)
    commit_changes(session)
    return part_posts(session, user_id, circle.id, part_id)
