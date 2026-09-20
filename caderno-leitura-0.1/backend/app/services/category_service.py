from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models import Book
from app.models.category import Category, book_categories


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
        if cid in existing:
            cat = existing[cid]
            cat.name = data["name"]
            cat.parent_id = data["parent_id"]
            cat.path = data["path"]
        else:
            cat = Category(
                id=cid,
                name=data["name"],
                parent_id=data["parent_id"],
                path=data["path"],
            )
            session.add(cat)
        count += 1

    session.commit()
    return count


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
