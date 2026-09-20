"""Serviço de integridade hierárquica, validação DAG e reorganização de estudos."""
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import select

from app.models import Study
from app.schemas.study import StudyMoveRequest
from app.schemas.study_grouping import StudyStatusUpdate
from app.services.persistence import check_optimistic_lock, commit_changes, get_or_404

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

MAX_HIERARCHY_DEPTH = 5


def get_descendant_ids(session: Session, study_id: int, include_deleted: bool = False) -> list[int]:
    """Retorna recursivamente os IDs de todos os estudos descendentes (filhos, netos, etc.)."""
    descendants: list[int] = []
    queue = [study_id]

    while queue:
        current_parent_id = queue.pop(0)
        query = select(Study.id).where(Study.parent_study_id == current_parent_id)
        if not include_deleted:
            query = query.where(Study.deleted_at.is_(None))
        child_ids = list(session.scalars(query).all())
        descendants.extend(child_ids)
        queue.extend(child_ids)

    return descendants


def get_node_depth(session: Session, study: Study) -> int:
    """Calcula a profundidade de um nó na árvore (raiz = 0)."""
    depth = 0
    current = study
    visited = {current.id}

    while current.parent_study_id is not None:
        depth += 1
        if depth >= MAX_HIERARCHY_DEPTH * 2:
            # Salvaguarda contra loop preexistente
            break
        parent = session.get(Study, current.parent_study_id)
        if parent is None or parent.id in visited:
            break
        visited.add(parent.id)
        current = parent

    return depth


def get_subtree_height(session: Session, study_id: int) -> int:
    """Calcula a altura máxima da subárvore sob um estudo (folha = 0)."""
    child_ids = list(
        session.scalars(
            select(Study.id).where(Study.parent_study_id == study_id, Study.deleted_at.is_(None))
        ).all()
    )
    if not child_ids:
        return 0
    return 1 + max(get_subtree_height(session, cid) for cid in child_ids)


def validate_hierarchy_move(session: Session, study: Study, new_parent_id: int | None) -> Study | None:
    """Valida se a movimentação é segura contra ciclos e não ultrapassa 5 níveis."""
    if new_parent_id is None:
        # Mover para a raiz sempre é permitido em termos de ciclo
        subtree_height = get_subtree_height(session, study.id)
        if subtree_height >= MAX_HIERARCHY_DEPTH:
            raise HTTPException(
                status_code=422,
                detail=f"Limite de profundidade excedido: a hierarquia suporta no máximo {MAX_HIERARCHY_DEPTH} níveis.",
            )
        return None

    if new_parent_id == study.id:
        raise HTTPException(
            status_code=422,
            detail="Auto-referência inválida: um estudo não pode ser pai de si mesmo.",
        )

    parent = get_or_404(session, Study, new_parent_id, "Estudo pai")

    if parent.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Não é possível definir como pai um estudo na lixeira.")

    if parent.chapter_id != study.chapter_id:
        raise HTTPException(status_code=422, detail="Estudo pai deve pertencer ao mesmo capítulo.")

    # 1. Prevenção estrita de ciclos (DAG): o novo pai não pode ser descendente do estudo
    descendant_ids = set(get_descendant_ids(session, study.id, include_deleted=True))
    if parent.id in descendant_ids:
        raise HTTPException(
            status_code=422,
            detail="Ciclo hierárquico detectado: um estudo não pode ser filho de seus próprios descendentes.",
        )

    # 2. Verificação do limite de profundidade (máximo 5 níveis, índices 0 a 4)
    parent_depth = get_node_depth(session, parent)
    subtree_height = get_subtree_height(session, study.id)
    total_depth = parent_depth + 1 + subtree_height

    if total_depth >= MAX_HIERARCHY_DEPTH:
        raise HTTPException(
            status_code=422,
            detail=f"Limite de profundidade excedido: a árvore permite no máximo {MAX_HIERARCHY_DEPTH} níveis.",
        )

    return parent


def move_study(session: Session, study_id: int, payload: StudyMoveRequest) -> list[Study]:
    """Move e reposiciona um estudo na árvore, reordenando irmãos de forma estável."""
    study = get_or_404(session, Study, study_id, "Estudo")
    if study.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Não é possível mover um estudo que está na lixeira.")

    check_optimistic_lock(study.updated_at, payload.expected_updated_at, "Estudo")

    old_parent_id = study.parent_study_id
    new_parent_id = payload.parent_study_id

    # Validação de integridade hierárquica e DAG
    validate_hierarchy_move(session, study, new_parent_id)

    # Se mudou de pai, reindexa os antigos irmãos
    if old_parent_id != new_parent_id:
        old_siblings = list(
            session.scalars(
                select(Study)
                .where(
                    Study.chapter_id == study.chapter_id,
                    Study.parent_study_id == old_parent_id,
                    Study.id != study.id,
                    Study.deleted_at.is_(None),
                )
                .order_by(Study.position, Study.id)
            ).all()
        )
        for idx, sib in enumerate(old_siblings):
            sib.position = idx
        study.parent_study_id = new_parent_id

    # Busca irmãos no novo pai (excluindo o estudo que está sendo movido)
    new_siblings = list(
        session.scalars(
            select(Study)
            .where(
                Study.chapter_id == study.chapter_id,
                Study.parent_study_id == new_parent_id,
                Study.id != study.id,
                Study.deleted_at.is_(None),
            )
            .order_by(Study.position, Study.id)
        ).all()
    )

    # Insere o estudo na posição desejada (limitada entre 0 e len(new_siblings))
    target_pos = max(0, min(payload.target_position, len(new_siblings)))
    new_siblings.insert(target_pos, study)

    # Reatribui ordenação contígua
    for idx, sib in enumerate(new_siblings):
        sib.position = idx

    commit_changes(session)

    # Retorna todos os estudos ativos do capítulo ordenados
    return list(
        session.scalars(
            select(Study)
            .where(Study.chapter_id == study.chapter_id, Study.deleted_at.is_(None))
            .order_by(Study.parent_study_id.nullsfirst(), Study.position, Study.id)
        ).all()
    )


def update_study_status(session: Session, study_id: int, payload: StudyStatusUpdate) -> Study:
    """Atualiza o reading_status de um estudo com verificação de concorrência otimista."""
    study = get_or_404(session, Study, study_id, "Estudo")
    if study.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Não é possível alterar o status de um estudo na lixeira.")

    check_optimistic_lock(study.updated_at, payload.expected_updated_at, "Estudo")

    study.reading_status = str(payload.reading_status)
    commit_changes(session)
    return study

