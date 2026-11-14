"""F0.11.11 (spec 113): cadernos de síntese com transclusão."""
from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Response, status

from app.dependencies import CurrentUser, DatabaseSession, Identifier
from app.schemas.synthesis import SynthesisCreate, SynthesisPatch, SynthesisRead, SynthesisResolved, SynthesisSummary
from app.services import synthesis_service as svc
from app.services.export_service import sanitize_filename

router = APIRouter(prefix="/syntheses", tags=["Cadernos de síntese"])


@router.get("", response_model=list[SynthesisSummary], summary="Listar cadernos de síntese")
def list_syntheses(session: DatabaseSession, current_user: CurrentUser):
    return svc.list_notebooks(session, current_user.id)


@router.get("/trash", response_model=list[SynthesisSummary], summary="Cadernos de síntese excluídos (30 dias)")
def list_trashed(session: DatabaseSession, current_user: CurrentUser):
    return svc.list_notebooks(session, current_user.id, trash=True)


@router.post("", response_model=SynthesisRead, status_code=status.HTTP_201_CREATED, summary="Criar caderno de síntese")
def create_synthesis(payload: SynthesisCreate, session: DatabaseSession, current_user: CurrentUser):
    return svc.to_read(svc.create_notebook(session, current_user.id, payload))


@router.get("/{notebook_id}", response_model=SynthesisRead, summary="Consultar caderno de síntese")
def get_synthesis(notebook_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return svc.to_read(svc.get_notebook(session, current_user.id, notebook_id))


@router.get("/{notebook_id}/resolved", response_model=SynthesisResolved, summary="Caderno com os trechos resolvidos")
def get_resolved(notebook_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    row = svc.get_notebook(session, current_user.id, notebook_id)
    return SynthesisResolved(
        synthesis=svc.to_read(row),
        embeds=svc.resolve_embeds(session, current_user.id, svc.parse_embeds(row.body)),
    )


@router.get("/{notebook_id}/export", summary="Exportar o caderno em Markdown (trechos resolvidos)")
def export_synthesis(notebook_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    row = svc.get_notebook(session, current_user.id, notebook_id)
    content = svc.export_markdown(row, svc.resolve_embeds(session, current_user.id, svc.parse_embeds(row.body)))
    filename = sanitize_filename(row.title, "md")
    return Response(
        content=content.encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )


@router.patch("/{notebook_id}", response_model=SynthesisRead, summary="Editar caderno de síntese")
def patch_synthesis(notebook_id: Identifier, payload: SynthesisPatch, session: DatabaseSession, current_user: CurrentUser):
    return svc.to_read(svc.update_notebook(session, current_user.id, notebook_id, payload))


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Mandar o caderno para Excluídos")
def trash_synthesis(notebook_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    svc.trash_notebook(session, current_user.id, notebook_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{notebook_id}/restore", response_model=SynthesisRead, summary="Restaurar caderno excluído")
def restore_synthesis(notebook_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    return svc.to_read(svc.restore_notebook(session, current_user.id, notebook_id))


@router.delete("/{notebook_id}/permanent", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir de vez")
def delete_synthesis(notebook_id: Identifier, session: DatabaseSession, current_user: CurrentUser):
    svc.delete_notebook_permanently(session, current_user.id, notebook_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
