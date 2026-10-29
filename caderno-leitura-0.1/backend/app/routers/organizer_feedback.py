"""Envio silencioso do feedback do organizador depois de salvar o estudo (feature 091-B).

Nunca muda nada na tela: responde ``204`` sempre que o pedido for válido, gravando ou não, e uma falha interna só
vira código no log. O estudo já está salvo e nada aqui o desfaz.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Response

from app.dependencies import CurrentUser, DatabaseSession
from app.models.organizer_feedback import OrganizerFeedback
from app.models.study import Study
from app.schemas.organizer_feedback import OrganizerFeedbackRequest
from app.services.organizer import adapter_service, feedback

logger = logging.getLogger("leitorum.organizer.feedback")

router = APIRouter(prefix="/studies", tags=["Organização"])


@router.post(
    "/{study_id}/organizer-feedback",
    status_code=204,
    summary="Registrar em silêncio a sugestão do organizador contra o estudo salvo",
)
def record_organizer_feedback(
    study_id: int, body: OrganizerFeedbackRequest, current_user: CurrentUser, session: DatabaseSession
) -> Response:
    study = session.get(Study, study_id)
    if study is None or study.user_id != current_user.id or study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")
    try:
        code, counts = feedback.record_feedback(session, study, current_user.id, body)
        if code == "recorded":
            session.commit()
    except Exception:  # o estudo já está salvo: o registro nunca pode virar erro para o leitor
        session.rollback()
        code, counts = "error", {}
    learned, ms = "-", 0
    if code == "recorded":
        try:  # adaptador (091-C): aprende sempre, mesmo desligado; uma falha não desfaz o registro
            row = session.query(OrganizerFeedback).filter_by(study_id=study.id).one()
            learned, ms = adapter_service.update_after_feedback(session, row)
        except Exception:
            session.rollback()
            learned = "error"
    logger.info(
        "organizer-feedback: %s (%s, %d trechos, %d correções, %d bytes); adaptador: %s, %d ms",
        code,
        body.origin,
        counts.get("segments", 0),
        counts.get("corrections", 0),
        counts.get("bytes", 0),
        learned,
        ms,
    )
    return Response(status_code=204)
