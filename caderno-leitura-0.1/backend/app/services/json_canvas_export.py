"""F0.12.05 (spec 118): exportar o livro em JSON Canvas 1.0 (https://jsoncanvas.org/), o formato aberto do Obsidian.

Só exportação (decisão do usuário em 2026-11-15; o quadro na tela saiu na 0.9 e não volta). Lê o que sobrou do quadro
antigo: posição/tamanho/cor dos estudos (`study_canvas_nodes`), molduras (`canvas_frames`) e relações
(`study_relations`). Estudo sem posição entra no layout automático, uma coluna por capítulo, à direita do resto.
Cada estudo vai como nó de texto (título + Resumo); nada de notas pessoais nem fichamento.
"""
from __future__ import annotations

import math
import re

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Book, CanvasFrame, Chapter, Study, StudyCanvasNode, StudyRelation

CARD_WIDTH = 400
MIN_CARD_HEIGHT = 120
MAX_CARD_HEIGHT = 600
GAP = 40
GROUP_PADDING = 40
GROUP_HEADER = 60
COLUMN_GAP = 120
CHARS_PER_LINE = 48
LINE_HEIGHT = 24

RELATION_LABELS = {
    "relacionado_com": "Relacionado com",
    "complementa": "Complementa",
    "contradiz": "Contradiz",
    "depende_de": "Depende de",
    "mesmo_tema": "Mesmo tema",
    "desdobramento_de": "Desdobramento de",
}
COLOR_PRESETS = {
    "1": ("red", "rose", "danger", "vermelho"),
    "2": ("orange", "amber", "warning", "laranja"),
    "3": ("yellow", "amarelo"),
    "4": ("green", "emerald", "lime", "success", "verde"),
    "5": ("cyan", "teal", "blue", "sky", "info", "azul", "ciano"),
    "6": ("purple", "violet", "indigo", "fuchsia", "accent", "roxo"),
}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def canvas_color(value: str | None) -> str | None:
    """Cor do quadro antigo → preset "1"–"6" do JSON Canvas, ou o próprio #RRGGBB; desconhecida → sem cor."""
    text = (value or "").strip()
    if HEX_COLOR.match(text):
        return text.lower()
    key = text.lower()
    for preset, names in COLOR_PRESETS.items():
        if key in names:
            return preset
    return None


def card_text(study: Study) -> str:
    body = ""
    for attr in ("summary", "explanation", "concepts", "references"):
        body = (getattr(study, attr) or "").strip()
        if body:
            break
    return f"## {study.title.strip()}\n\n{body}".strip()


def estimate_height(text: str) -> int:
    lines = sum(max(1, math.ceil(len(line) / CHARS_PER_LINE)) for line in text.split("\n"))
    return max(MIN_CARD_HEIGHT, min(MAX_CARD_HEIGHT, 40 + lines * LINE_HEIGHT))


def _node(node_id: str, node_type: str, x: float, y: float, width: float, height: float, **extra) -> dict:
    node = {"id": node_id, "type": node_type, "x": round(x), "y": round(y), "width": round(width), "height": round(height)}
    node.update({k: v for k, v in extra.items() if v is not None})
    return node


def build_book_canvas(session: Session, user_id: str, book_id: int) -> tuple[Book, dict]:
    book = session.scalar(select(Book).where(Book.id == book_id, Book.user_id == user_id, Book.deleted_at.is_(None)))
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")
    chapters = session.scalars(
        select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.position, Chapter.id)
    ).all()
    studies = session.scalars(
        select(Study)
        .join(Chapter, Study.chapter_id == Chapter.id)
        .where(Chapter.book_id == book.id, Study.user_id == user_id, Study.deleted_at.is_(None))
        .order_by(Chapter.position, Chapter.id, Study.position, Study.id)
    ).all()
    saved = {
        n.study_id: n
        for n in session.scalars(select(StudyCanvasNode).where(StudyCanvasNode.book_id == book.id,
                                                               StudyCanvasNode.user_id == user_id)).all()
    }
    frames = session.scalars(
        select(CanvasFrame).where(CanvasFrame.book_id == book.id, CanvasFrame.user_id == user_id).order_by(CanvasFrame.id)
    ).all()

    nodes: list[dict] = []
    right_edge = 0.0
    for frame in frames:
        nodes.append(_node(f"frame-{frame.id}", "group", frame.pos_x, frame.pos_y, frame.width, frame.height,
                           label=frame.title, color=canvas_color(frame.color)))
        right_edge = max(right_edge, frame.pos_x + frame.width)

    pending: dict[int, list[Study]] = {}
    for study in studies:
        text = card_text(study)
        position = saved.get(study.id)
        if position is not None:
            width = position.width or CARD_WIDTH
            height = position.height or estimate_height(text)
            nodes.append(_node(f"study-{study.id}", "text", position.pos_x, position.pos_y, width, height, text=text,
                               color=canvas_color(position.color_tag)))
            right_edge = max(right_edge, position.pos_x + width)
        else:
            pending.setdefault(study.chapter_id, []).append(study)

    # Layout automático: uma coluna (grupo) por capítulo, à direita do que já tinha posição.
    x = right_edge + COLUMN_GAP if nodes else 0.0
    for chapter in chapters:
        group_studies = pending.get(chapter.id)
        if not group_studies:
            continue
        y = GROUP_HEADER
        cards: list[dict] = []
        for study in group_studies:
            text = card_text(study)
            height = estimate_height(text)
            cards.append(_node(f"study-{study.id}", "text", x + GROUP_PADDING, y, CARD_WIDTH, height, text=text))
            y += height + GAP
        group_height = y - GAP + GROUP_PADDING
        nodes.append(_node(f"chapter-{chapter.id}", "group", x, 0, CARD_WIDTH + 2 * GROUP_PADDING, group_height,
                           label=chapter.name))
        nodes.extend(cards)
        x += CARD_WIDTH + 2 * GROUP_PADDING + COLUMN_GAP

    study_ids = {s.id for s in studies}
    edges: list[dict] = []
    if study_ids:
        relations = session.scalars(
            select(StudyRelation)
            .where(StudyRelation.user_id == user_id,
                   StudyRelation.source_study_id.in_(study_ids), StudyRelation.target_study_id.in_(study_ids))
            .order_by(StudyRelation.id)
        ).all()
        for relation in relations:
            label = RELATION_LABELS.get(relation.relation_type, relation.relation_type)
            if (relation.description or "").strip():
                label = f"{label}: {relation.description.strip()}"
            edges.append({"id": f"relation-{relation.id}", "fromNode": f"study-{relation.source_study_id}",
                          "toNode": f"study-{relation.target_study_id}", "toEnd": "arrow", "label": label})
    return book, {"nodes": nodes, "edges": edges}
