"""F0.12.07 (spec 120): círculos de leitura com trava anti-spoiler (`/api/circles…`)."""
from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import Field

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.common import InputModel
from app.services import reading_circle_service as circles

router = APIRouter(prefix="/circles", tags=["Círculos de leitura"])


class CircleCreate(InputModel):
    book_id: int = Field(gt=0)
    name: str | None = Field(default=None, max_length=200)


class NameUpdate(InputModel):
    name: str = Field(max_length=300)


class InviteRequest(InputModel):
    username: str = Field(min_length=1, max_length=100)


class ProgressUpdate(InputModel):
    progress: int = Field(ge=0, le=1000)
    finished: bool = False


class PostBody(InputModel):
    body: str = Field(max_length=8000)


@router.get("", summary="Meus círculos e convites")
def list_circles(session: DatabaseSession, current_user: CurrentUser):
    return circles.list_circles(session, current_user.id)


@router.get("/invites/count", summary="Quantos convites de círculo estão pendentes")
def invites_count(session: DatabaseSession, current_user: CurrentUser):
    return {"count": circles.invite_count(session, current_user.id)}


@router.post("", status_code=201, summary="Criar um círculo a partir de um livro meu")
def create_circle(payload: CircleCreate, session: DatabaseSession, current_user: CurrentUser):
    return circles.create_circle(session, current_user.id, payload.book_id, payload.name)


@router.get("/{circle_id}", summary="Detalhe do círculo (partes com a trava aplicada)")
def get_circle(circle_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return circles.circle_detail(session, current_user.id, circle_id)


@router.patch("/{circle_id}", summary="Renomear o círculo")
def rename_circle(circle_id: Identifier, payload: NameUpdate, session: DatabaseSession, current_user: CurrentUser):
    return circles.rename(session, current_user.id, circle_id, payload.name)


@router.delete("/{circle_id}", status_code=204, summary="Apagar o círculo")
def delete_circle(circle_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    circles.delete_circle(session, current_user.id, circle_id)
    return Response(status_code=204)


@router.get("/{circle_id}/invitable", summary="Amigos que ainda podem ser convidados")
def invitable(circle_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return circles.invitable_friends(session, current_user.id, circle_id)


@router.post("/{circle_id}/invites", summary="Convidar um amigo")
def invite(circle_id: Identifier, payload: InviteRequest, session: DatabaseSession, current_user: CurrentUser):
    return circles.invite(session, current_user.id, circle_id, payload.username)


@router.post("/{circle_id}/accept", summary="Aceitar o convite")
def accept(circle_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return circles.accept(session, current_user.id, circle_id)


@router.post("/{circle_id}/decline", status_code=204, summary="Recusar o convite")
def decline(circle_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    circles.decline(session, current_user.id, circle_id)
    return Response(status_code=204)


@router.post("/{circle_id}/leave", status_code=204, summary="Sair do círculo")
def leave(circle_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    circles.leave(session, current_user.id, circle_id)
    return Response(status_code=204)


@router.delete("/{circle_id}/members/{user_id}", summary="Tirar um membro do círculo")
def remove_member(circle_id: Identifier, user_id: str, session: DatabaseSession, current_user: CurrentUser):
    return circles.remove_member(session, current_user.id, circle_id, user_id)


@router.put("/{circle_id}/progress", summary="Marcar em que parte estou")
def set_progress(circle_id: Identifier, payload: ProgressUpdate, session: DatabaseSession, current_user: CurrentUser):
    return circles.set_progress(session, current_user.id, circle_id, payload.progress, payload.finished)


@router.post("/{circle_id}/parts", summary="Acrescentar uma parte no fim")
def add_part(circle_id: Identifier, payload: NameUpdate, session: DatabaseSession, current_user: CurrentUser):
    return circles.add_part(session, current_user.id, circle_id, payload.name)


@router.patch("/{circle_id}/parts/{part_id}", summary="Renomear uma parte")
def rename_part(
    circle_id: Identifier, part_id: Identifier, payload: NameUpdate, session: DatabaseSession,
    current_user: CurrentUser,
):
    return circles.rename_part(session, current_user.id, circle_id, part_id, payload.name)


@router.delete("/{circle_id}/parts/{part_id}", summary="Apagar a última parte (sem mensagens)")
def delete_part(circle_id: Identifier, part_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return circles.delete_part(session, current_user.id, circle_id, part_id)


@router.get("/{circle_id}/parts/{part_id}/posts", summary="Mensagens de uma parte (trancada = só a contagem)")
def part_posts(circle_id: Identifier, part_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return circles.part_posts(session, current_user.id, circle_id, part_id)


@router.post("/{circle_id}/parts/{part_id}/posts", summary="Escrever numa parte")
def create_post(
    circle_id: Identifier, part_id: Identifier, payload: PostBody, session: DatabaseSession, current_user: CurrentUser,
):
    return circles.create_post(session, current_user.id, circle_id, part_id, payload.body)


@router.patch("/{circle_id}/posts/{post_id}", summary="Editar a própria mensagem")
def edit_post(
    circle_id: Identifier, post_id: Identifier, payload: PostBody, session: DatabaseSession, current_user: CurrentUser,
):
    return circles.edit_post(session, current_user.id, circle_id, post_id, payload.body)


@router.delete("/{circle_id}/posts/{post_id}", summary="Apagar uma mensagem")
def delete_post(circle_id: Identifier, post_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return circles.delete_post(session, current_user.id, circle_id, post_id)
