from __future__ import annotations

import difflib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.types import utc_now
from app.models.study import Study
from app.models.study_highlight import StudyHighlight
from app.models.study_version import StudyVersion
from app.models.user import User
from app.schemas.study_version import (
    DiffChunk,
    SectionDiff,
    StudyDiffResponse,
    StudyVersionDetail,
    StudyVersionSummary,
)
from app.services.sharing_service import can_read_study

ANALYSIS_FIELDS = ("summary", "explanation", "concepts", "references", "notes")
VERSIONED_FIELDS = ("title", *ANALYSIS_FIELDS)
COALESCE_WINDOW_SECONDS = 300  # 5 minutos


def check_study_access(session: Session, study_id: int, user_id: str, *, for_mutation: bool = False) -> Study:
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado ou está na lixeira.")

    if study.user_id == user_id:
        return study

    if can_read_study(session, user_id, study):
        if for_mutation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso somente leitura. Apenas o proprietário pode alterar este estudo.",
            )
        return study

    raise HTTPException(status_code=404, detail="Estudo não encontrado.")


def serialize_highlights(session: Session, study_id: int) -> str:
    stmt = (
        select(StudyHighlight)
        .where(StudyHighlight.study_id == study_id)
        .order_by(StudyHighlight.id)
    )
    highlights = session.scalars(stmt).all()
    data = [
        {
            "section": h.section,
            "start_offset": h.start_offset,
            "end_offset": h.end_offset,
            "selected_text": h.selected_text,
            "prefix": h.prefix,
            "suffix": h.suffix,
            "color": h.color,
            "kind": h.kind,
            "note": h.note,
        }
        for h in highlights
    ]
    return json.dumps(data, ensure_ascii=False)


def record_study_version_on_change(
    session: Session,
    study: Study,
    new_values: dict[str, Any],
    user_id: str | None,
    change_summary: str = "Edição",
) -> StudyVersion | None:
    """Registra ou agrupa automaticamente uma versão quando há alterações nos campos de texto."""
    # Verificar se algum campo versionado realmente mudou
    has_changes = False
    for field in VERSIONED_FIELDS:
        if field in new_values:
            old_val = getattr(study, field, "") or ""
            new_val = new_values[field] or ""
            if old_val != new_val:
                has_changes = True
                break

    if not has_changes:
        return None

    now = utc_now()
    highlights_json = serialize_highlights(session, study.id)

    # Buscar última versão registrada para este estudo
    latest_version = session.scalars(
        select(StudyVersion)
        .where(StudyVersion.study_id == study.id)
        .order_by(StudyVersion.version_number.desc())
    ).first()

    # Se ainda não existe nenhuma versão anterior (ex: estudo antigo no banco),
    # criar primeiro a Versão 1 como baseline do estado anterior ao salvamento.
    if latest_version is None:
        baseline_v = StudyVersion(
            study_id=study.id,
            version_number=1,
            user_id=study.user_id,
            title=study.title,
            summary=study.summary,
            explanation=study.explanation,
            concepts=study.concepts,
            references=study.references,
            notes=study.notes,
            highlights_data=highlights_json,
            change_summary="Versão inicial",
            created_at=study.created_at or now,
            updated_at=study.created_at or now,
        )
        session.add(baseline_v)
        session.flush()
        latest_version = baseline_v

    # Valores finais após aplicação da alteração
    target_title = new_values.get("title", study.title)
    target_summary = new_values.get("summary", study.summary)
    target_explanation = new_values.get("explanation", study.explanation)
    target_concepts = new_values.get("concepts", study.concepts)
    target_references = new_values.get("references", study.references)
    target_notes = new_values.get("notes", study.notes)

    # Verificar coalescência (janela de 5 minutos, mesmo autor, não sendo restauração)
    delta_seconds = (now - latest_version.updated_at).total_seconds() if latest_version.updated_at else 9999
    is_same_author = (latest_version.user_id == user_id)
    is_not_restoration = not latest_version.change_summary.startswith("Restauração")
    can_coalesce = (
        latest_version.version_number > 1
        and delta_seconds <= COALESCE_WINDOW_SECONDS
        and is_same_author
        and is_not_restoration
    )

    if can_coalesce:
        latest_version.title = target_title
        latest_version.summary = target_summary
        latest_version.explanation = target_explanation
        latest_version.concepts = target_concepts
        latest_version.references = target_references
        latest_version.notes = target_notes
        latest_version.highlights_data = highlights_json
        latest_version.updated_at = now
        session.flush()
        return latest_version
    else:
        new_version_num = latest_version.version_number + 1
        new_v = StudyVersion(
            study_id=study.id,
            version_number=new_version_num,
            user_id=user_id,
            title=target_title,
            summary=target_summary,
            explanation=target_explanation,
            concepts=target_concepts,
            references=target_references,
            notes=target_notes,
            highlights_data=highlights_json,
            change_summary=change_summary,
            created_at=now,
            updated_at=now,
        )
        session.add(new_v)
        session.flush()
        return new_v


def get_study_versions(session: Session, study_id: int) -> list[StudyVersionSummary]:
    stmt = (
        select(StudyVersion)
        .where(StudyVersion.study_id == study_id)
        .order_by(StudyVersion.version_number.desc())
    )
    versions = session.scalars(stmt).all()
    result: list[StudyVersionSummary] = []

    for index, v in enumerate(versions):
        author_name = None
        if v.user_id:
            user = session.get(User, v.user_id)
            if user:
                author_name = user.display_name or user.username

        char_count = (
            len(v.title or "")
            + len(v.summary or "")
            + len(v.explanation or "")
            + len(v.concepts or "")
            + len(v.references or "")
            + len(v.notes or "")
        )

        try:
            hl_list = json.loads(v.highlights_data or "[]")
            highlights_count = len(hl_list) if isinstance(hl_list, list) else 0
        except Exception:
            highlights_count = 0

        result.append(
            StudyVersionSummary(
                id=v.id,
                study_id=v.study_id,
                version_number=v.version_number,
                user_id=v.user_id,
                author_name=author_name,
                change_summary=v.change_summary,
                char_count=char_count,
                highlights_count=highlights_count,
                is_current=(index == 0),
                created_at=v.created_at,
                updated_at=v.updated_at,
            )
        )
    return result


def get_study_version_detail(session: Session, study_id: int, version_id: int) -> StudyVersionDetail:
    v = session.get(StudyVersion, version_id)
    if v is None or v.study_id != study_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versão não encontrada.")

    author_name = None
    if v.user_id:
        user = session.get(User, v.user_id)
        if user:
            author_name = user.display_name or user.username

    char_count = (
        len(v.title or "")
        + len(v.summary or "")
        + len(v.explanation or "")
        + len(v.concepts or "")
        + len(v.references or "")
        + len(v.notes or "")
    )

    try:
        highlights = json.loads(v.highlights_data or "[]")
        if not isinstance(highlights, list):
            highlights = []
    except Exception:
        highlights = []

    # Verificar se é a mais recente
    latest_id = session.scalar(
        select(StudyVersion.id)
        .where(StudyVersion.study_id == study_id)
        .order_by(StudyVersion.version_number.desc())
        .limit(1)
    )

    return StudyVersionDetail(
        id=v.id,
        study_id=v.study_id,
        version_number=v.version_number,
        user_id=v.user_id,
        author_name=author_name,
        change_summary=v.change_summary,
        char_count=char_count,
        highlights_count=len(highlights),
        is_current=(v.id == latest_id),
        created_at=v.created_at,
        updated_at=v.updated_at,
        title=v.title,
        summary=v.summary,
        explanation=v.explanation,
        concepts=v.concepts,
        references=v.references,
        notes=v.notes,
        highlights=highlights,
    )


def compute_section_diff(source_text: str, target_text: str) -> SectionDiff:
    if source_text == target_text:
        return SectionDiff(
            status="unchanged",
            chunks=[DiffChunk(type="equal", text=source_text)] if source_text else [],
        )

    matcher = difflib.SequenceMatcher(None, source_text, target_text)
    chunks: list[DiffChunk] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            chunks.append(DiffChunk(type="equal", text=source_text[i1:i2]))
        elif tag == "delete":
            chunks.append(DiffChunk(type="delete", text=source_text[i1:i2]))
        elif tag == "insert":
            chunks.append(DiffChunk(type="insert", text=target_text[j1:j2]))
        elif tag == "replace":
            chunks.append(DiffChunk(type="delete", text=source_text[i1:i2]))
            chunks.append(DiffChunk(type="insert", text=target_text[j1:j2]))

    if not source_text and target_text:
        section_status = "added"
    elif source_text and not target_text:
        section_status = "removed"
    else:
        section_status = "modified"

    return SectionDiff(status=section_status, chunks=chunks)


def compute_study_diff(
    session: Session,
    study_id: int,
    version_id: int,
    target_version_id: int | None = None,
) -> StudyDiffResponse:
    source_v = session.get(StudyVersion, version_id)
    if source_v is None or source_v.study_id != study_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versão de origem não encontrada.")

    is_target_current = False
    if target_version_id is not None:
        target_v = session.get(StudyVersion, target_version_id)
        if target_v is None or target_v.study_id != study_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versão de destino não encontrada.")
        target_version_number = target_v.version_number
        target_data = {
            "title": target_v.title,
            "summary": target_v.summary,
            "explanation": target_v.explanation,
            "concepts": target_v.concepts,
            "references": target_v.references,
            "notes": target_v.notes,
        }
    else:
        study = session.get(Study, study_id)
        if study is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudo não encontrado.")
        is_target_current = True
        latest_num = session.scalar(
            select(StudyVersion.version_number)
            .where(StudyVersion.study_id == study_id)
            .order_by(StudyVersion.version_number.desc())
            .limit(1)
        ) or 1
        target_version_number = latest_num
        target_data = {
            "title": study.title,
            "summary": study.summary,
            "explanation": study.explanation,
            "concepts": study.concepts,
            "references": study.references,
            "notes": study.notes,
        }

    sections_diff: dict[str, SectionDiff] = {}
    for field in VERSIONED_FIELDS:
        s_val = getattr(source_v, field, "") or ""
        t_val = target_data.get(field, "") or ""
        sections_diff[field] = compute_section_diff(s_val, t_val)

    return StudyDiffResponse(
        version_number=source_v.version_number,
        target_version_number=target_version_number,
        is_target_current=is_target_current,
        sections=sections_diff,
    )


def restore_study_version(
    session: Session,
    study_id: int,
    version_id: int,
    user_id: str,
) -> Study:
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudo não encontrado.")

    target_v = session.get(StudyVersion, version_id)
    if target_v is None or target_v.study_id != study_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versão alvo não encontrada.")

    now = utc_now()

    # 1. Salvar preventivamente o estado presente se houver diferenças em relação à última versão
    latest_v = session.scalars(
        select(StudyVersion)
        .where(StudyVersion.study_id == study.id)
        .order_by(StudyVersion.version_number.desc())
    ).first()

    current_highlights = serialize_highlights(session, study.id)
    max_version_number = latest_v.version_number if latest_v else 0

    if latest_v is None:
        # Se não havia versões gravadas, registrar baseline inicial
        max_version_number += 1
        baseline = StudyVersion(
            study_id=study.id,
            version_number=max_version_number,
            user_id=study.user_id,
            title=study.title,
            summary=study.summary,
            explanation=study.explanation,
            concepts=study.concepts,
            references=study.references,
            notes=study.notes,
            highlights_data=current_highlights,
            change_summary="Versão inicial",
            created_at=study.created_at or now,
            updated_at=study.created_at or now,
        )
        session.add(baseline)
        session.flush()

    # 2. Reverter os campos do Study para os valores da versão restaurada
    study.title = target_v.title
    study.summary = target_v.summary
    study.explanation = target_v.explanation
    study.concepts = target_v.concepts
    study.references = target_v.references
    study.notes = target_v.notes
    study.version += 1
    study.updated_at = now

    # 3. Restaurar highlights (apaga atuais e recria a partir do snapshot)
    session.execute(delete(StudyHighlight).where(StudyHighlight.study_id == study.id))
    try:
        hl_data = json.loads(target_v.highlights_data or "[]")
        if isinstance(hl_data, list):
            for h in hl_data:
                new_hl = StudyHighlight(
                    study_id=study.id,
                    user_id=user_id,
                    section=h.get("section", "summary"),
                    start_offset=h.get("start_offset", 0),
                    end_offset=h.get("end_offset", 0),
                    selected_text=h.get("selected_text", ""),
                    prefix=h.get("prefix", ""),
                    suffix=h.get("suffix", ""),
                    color=h.get("color", "yellow"),
                    kind=h.get("kind", "highlight"),
                    note=h.get("note", ""),
                    created_at=now,
                    updated_at=now,
                )
                session.add(new_hl)
    except Exception:
        pass

    session.flush()

    # 4. Criar o novo marco de versão que registra a restauração
    latest_num = session.scalar(
        select(StudyVersion.version_number)
        .where(StudyVersion.study_id == study.id)
        .order_by(StudyVersion.version_number.desc())
        .limit(1)
    ) or 0

    restored_v = StudyVersion(
        study_id=study.id,
        version_number=latest_num + 1,
        user_id=user_id,
        title=study.title,
        summary=study.summary,
        explanation=study.explanation,
        concepts=study.concepts,
        references=study.references,
        notes=study.notes,
        highlights_data=target_v.highlights_data,
        change_summary=f"Restauração da versão {target_v.version_number}",
        created_at=now,
        updated_at=now,
    )
    session.add(restored_v)
    session.flush()

    return study
