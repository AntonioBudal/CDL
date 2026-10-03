from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models import Book
from app.models.category import Category, book_categories
from app.schemas.category import CategoryRead, CategoryStats, CategorySuggestion
from app.services.canonical_categories import (
    CANONICAL_CATEGORIES,
    CANONICAL_INDEX_BY_NAME_LOWER,
    CANONICAL_INDEX_BY_SLUG,
    is_canonical_slug,
    resolve_legacy_mapping,
)
from app.services.category_normalizer import (
    canonicalize_name,
    normalize_for_search,
    slugify_category,
    validate_category_name,
)


def validate_and_build_hierarchy(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Valida integridade do catálogo taxonômico e calcula o caminho hierárquico (path).

    Garante:
    1. Quantidade superior a 100 categorias.
    2. Unicidade estrita de identificadores (id).
    3. Existência de todas as categorias pai referenciadas.
    4. Ausência total de ciclos na árvore de parentesco.
    """
    if len(entries) < 100:
        raise ValueError(f"O catálogo taxonômico deve conter mais de 100 categorias. Encontradas: {len(entries)}")

    id_map: dict[str, dict[str, Any]] = {}
    for entry in entries:
        cid = (entry.get("id") or "").strip()
        name = (entry.get("name") or "").strip()
        if not cid:
            raise ValueError(f"Identificador de categoria inválido ou vazio: {entry}")
        if not name:
            raise ValueError(f"Nome de categoria inválido ou vazio para ID '{cid}'")
        if cid in id_map:
            raise ValueError(f"Identificador duplicado encontrado no catálogo: '{cid}'")
        id_map[cid] = entry

    # Validar parent_id existente
    for cid, entry in id_map.items():
        pid = entry.get("parent_id")
        if pid is not None:
            pid = str(pid).strip()
            if pid not in id_map:
                raise ValueError(f"Categoria '{cid}' referencia pai inexistente '{pid}'")
            if pid == cid:
                raise ValueError(f"Categoria '{cid}' não pode ser pai de si mesma")

    # Detecção de ciclos via DFS
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {cid: WHITE for cid in id_map}

    def dfs(cid: str) -> None:
        color[cid] = GRAY
        pid = id_map[cid].get("parent_id")
        if pid:
            if color[pid] == GRAY:
                raise ValueError(f"Ciclo hierárquico detectado envolvendo '{cid}' e '{pid}'")
            if color[pid] == WHITE:
                dfs(pid)
        color[cid] = BLACK

    for cid in id_map:
        if color[cid] == WHITE:
            dfs(cid)

    # Computar caminho hierárquico formatado
    result = []
    for entry in entries:
        cid = entry["id"].strip()
        name = entry["name"].strip()
        pid = entry.get("parent_id")
        pid = pid.strip() if pid else None

        parts = [name]
        curr_pid = pid
        while curr_pid:
            parent_entry = id_map[curr_pid]
            parts.append(parent_entry["name"].strip())
            curr_pid = parent_entry.get("parent_id")
            if curr_pid:
                curr_pid = curr_pid.strip()

        path = " / ".join(reversed(parts))
        result.append({
            "id": cid,
            "name": name,
            "parent_id": pid,
            "path": path,
        })

    return result


def get_canonical_categories_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "canonical_categories.json"


def load_canonical_categories_from_file(file_path: Path | None = None) -> list[dict[str, Any]]:
    path = file_path or get_canonical_categories_path()
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo de catálogo canônico não encontrado em: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return validate_and_build_hierarchy(data)


def sync_canonical_categories(session: Session, file_path: Path | None = None) -> int:
    """Sincroniza o catálogo canônico no banco de forma estritamente idempotente."""
    categories_data = load_canonical_categories_from_file(file_path)
    existing = {c.id: c for c in session.scalars(select(Category)).all()}

    count = 0
    for data in categories_data:
        cid = data["id"]
        is_canon = is_canonical_slug(cid)
        if cid in existing:
            cat = existing[cid]
            if is_canon:
                canon_def = CANONICAL_INDEX_BY_SLUG[cid]
                cat.name = canon_def.name
                cat.parent_id = None
                cat.path = cid
                cat.is_canonical = True
                cat.normalized_name = normalize_for_search(canon_def.name)
            else:
                cat.name = data["name"]
                cat.parent_id = data.get("parent_id")
                cat.path = data["path"]
                cat.is_canonical = False
                cat.normalized_name = normalize_for_search(data["name"])
        else:
            cat = Category(
                id=cid,
                name=CANONICAL_INDEX_BY_SLUG[cid].name if is_canon else data["name"],
                parent_id=None if is_canon else data.get("parent_id"),
                path=cid if is_canon else data["path"],
                is_canonical=is_canon,
                normalized_name=normalize_for_search(
                    CANONICAL_INDEX_BY_SLUG[cid].name if is_canon else data["name"]
                ),
            )
            session.add(cat)
            existing[cid] = cat
        count += 1

    # Inserir também as categorias do catálogo canônico oficial que não estavam no json legado
    for can_def in CANONICAL_CATEGORIES:
        if can_def.id not in existing:
            cat = Category(
                id=can_def.id,
                name=can_def.name,
                parent_id=None,
                path=can_def.id,
                is_canonical=True,
                normalized_name=normalize_for_search(can_def.name),
            )
            session.add(cat)
            existing[can_def.id] = cat
            count += 1
        else:
            cat = existing[can_def.id]
            cat.name = can_def.name
            cat.parent_id = None
            cat.path = can_def.id
            cat.is_canonical = True
            cat.normalized_name = normalize_for_search(can_def.name)

    session.commit()
    return len(existing)


def get_descendant_category_ids(session: Session, category_id: str) -> set[str]:
    """Retorna o ID da categoria informada e todos os IDs de suas subcategorias descendentes via CTE recursiva."""
    query = text(
        """
        WITH RECURSIVE subcategories AS (
            SELECT id FROM categories WHERE id = :cat_id
            UNION ALL
            SELECT c.id FROM categories c
            JOIN subcategories s ON c.parent_id = s.id
        )
        SELECT id FROM subcategories
        """
    )
    rows = session.execute(query, {"cat_id": category_id}).fetchall()
    return {row[0] for row in rows}


def get_categories_with_books_count(
    session: Session,
    user_id: str | None = None,
    q: str | None = None,
    canonical_only: bool = False,
) -> list[CategoryRead]:
    """Lista categorias ordenadas alfabeticamente com contagem de livros associados."""
    from sqlalchemy import func, or_

    # Subquery para contagem de livros por categoria
    count_subq = (
        select(
            book_categories.c.category_id,
            func.count(book_categories.c.book_id).label("books_count"),
        )
        .group_by(book_categories.c.category_id)
        .subquery()
    )

    query = (
        select(
            Category,
            func.coalesce(count_subq.c.books_count, 0).label("books_count"),
        )
        .outerjoin(count_subq, Category.id == count_subq.c.category_id)
    )

    if canonical_only or user_id is None:
        query = query.where(Category.is_canonical.is_(True))
    else:
        query = query.where(
            or_(
                Category.is_canonical.is_(True),
                Category.user_id == user_id,
            )
        )

    if q and q.strip():
        norm_q = normalize_for_search(q)
        term = f"%{norm_q}%"
        query = query.where(
            or_(
                Category.normalized_name.ilike(term),
                Category.name.ilike(f"%{q.strip()}%"),
                Category.id.ilike(f"%{q.strip()}%"),
            )
        )

    # Ordenação alfabética estrita por nome
    query = query.order_by(Category.name.asc())

    results = session.execute(query).all()
    output: list[CategoryRead] = []
    for cat, b_count in results:
        output.append(
            CategoryRead(
                id=cat.id,
                name=cat.name,
                parent_id=cat.parent_id,
                path=cat.path,
                user_id=cat.user_id,
                is_canonical=cat.is_canonical,
                books_count=int(b_count),
                created_at=cat.created_at,
            )
        )
    return output


def get_category_suggestions(
    session: Session,
    query_text: str,
    user_id: str | None = None,
) -> CategorySuggestion:
    """Gera sugestões automáticas e determinísticas de categorias canônicas."""
    from sqlalchemy import or_

    clean_term = query_text.strip()
    if not clean_term:
        return CategorySuggestion(
            input_term="",
            suggested_canonical="",
            is_exact_match=False,
            matching_candidates=[],
        )

    suggested = canonicalize_name(clean_term)
    norm_input = normalize_for_search(clean_term)
    norm_suggested = normalize_for_search(suggested)

    # Buscar candidatos no banco correspondendo ao termo normalizado ou termo sugerido
    db_query = (
        select(Category)
        .where(
            or_(
                Category.user_id.is_(None),
                Category.user_id == user_id,
            )
        )
        .where(
            or_(
                Category.normalized_name.ilike(f"%{norm_suggested}%"),
                Category.normalized_name.ilike(f"%{norm_input}%"),
                Category.name.ilike(f"%{suggested}%"),
                Category.name.ilike(f"%{clean_term}%"),
            )
        )
        .order_by(Category.is_canonical.desc(), Category.name.asc())
        .limit(10)
    )
    candidates = session.scalars(db_query).all()

    candidate_reads = [
        CategoryRead(
            id=c.id,
            name=c.name,
            parent_id=c.parent_id,
            path=c.path,
            user_id=c.user_id,
            is_canonical=c.is_canonical,
            books_count=0,
            created_at=c.created_at,
        )
        for c in candidates
    ]

    is_exact = any(c.normalized_name == norm_suggested for c in candidates)

    return CategorySuggestion(
        input_term=clean_term,
        suggested_canonical=suggested,
        is_exact_match=is_exact,
        matching_candidates=candidate_reads,
    )


def get_or_create_canonical_category(
    session: Session,
    name: str,
    user_id: str | None = None,
    category_id: str | None = None,
    parent_id: str | None = None,
) -> tuple[Category, bool]:
    """Cria ou retorna uma categoria aplicando normalização canônica singular.

    Retorna tupla: (categoria, criado_agora: bool).
    """
    from sqlalchemy import or_

    is_valid, error_msg = validate_category_name(name)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    canon_name = canonicalize_name(name)
    norm_name = normalize_for_search(canon_name)
    target_id = category_id.strip() if category_id and category_id.strip() else slugify_category(canon_name)

    # Verificar se já existe categoria canônica ou com mesmo normalized_name
    if category_id and category_id.strip():
        existing = session.get(Category, target_id)
    else:
        existing = session.scalars(
            select(Category)
            .where(
                or_(
                    Category.id == target_id,
                    Category.normalized_name == norm_name,
                )
            )
            .where(
                or_(
                    Category.user_id.is_(None),
                    Category.user_id == user_id,
                )
            )
        ).first()

    if existing is not None:
        return existing, False

    # Determinar caminho e parentesco se informado
    path = canon_name
    clean_parent_id = parent_id.strip() if parent_id and parent_id.strip() else None
    if clean_parent_id:
        parent = session.get(Category, clean_parent_id)
        if parent:
            path = f"{parent.path} / {canon_name}"

    is_canon = is_canonical_slug(target_id)
    new_cat = Category(
        id=target_id,
        name=canon_name,
        normalized_name=norm_name,
        is_canonical=is_canon,
        parent_id=clean_parent_id,
        path=path,
        user_id=None if is_canon else user_id,
    )
    session.add(new_cat)
    return new_cat, True


def get_taxonomy_stats(session: Session) -> CategoryStats:
    """Calcula estatísticas agregadas da taxonomia para o painel de conformidade."""
    from sqlalchemy import func

    total_cats = session.scalar(select(func.count(Category.id))) or 0
    canonical_cats = (
        session.scalar(
            select(func.count(Category.id)).where(Category.is_canonical.is_(True))
        )
        or 0
    )
    total_assocs = session.scalar(select(func.count()).select_from(book_categories)) or 0

    # Categorias sem nenhum livro associado
    used_cats_subq = select(book_categories.c.category_id).distinct()
    unused_cats = (
        session.scalar(
            select(func.count(Category.id)).where(Category.id.not_in(used_cats_subq))
        )
        or 0
    )

    return CategoryStats(
        total_categories=int(total_cats),
        canonical_categories=int(canonical_cats),
        unused_categories=int(unused_cats),
        total_book_associations=int(total_assocs),
    )


def assign_book_categories(session: Session, book: Book, category_ids: list[str]) -> None:
    """Sincroniza as categorias associadas a um livro (relação N:N)."""
    clean_ids = [cid.strip() for cid in category_ids if cid and cid.strip()]
    if not clean_ids:
        book.categories = []
        return

    # Buscar categorias existentes
    stmt = select(Category).where(Category.id.in_(clean_ids))
    found = list(session.scalars(stmt).all())
    found_ids = {c.id for c in found}

    missing = [cid for cid in clean_ids if cid not in found_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"As seguintes categorias não existem no catálogo: {', '.join(missing)}",
        )

    book.categories = found
