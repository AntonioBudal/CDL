"""Serviço de geração e formatação de exportações em Markdown e Texto Puro."""
from __future__ import annotations

from datetime import UTC, datetime
import io
import json
import re
from typing import TYPE_CHECKING
import unicodedata
import zipfile

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Book, Category, Chapter, Study, User, UserPreference, UserProfile
from app.schemas.export import ExportFormat, ExportOptions

if TYPE_CHECKING:
    pass


def sanitize_filename(title: str, extension: str, max_length: int = 80) -> str:
    """Sanitiza um título para uso seguro como nome de arquivo no Windows e outros sistemas.

    - Converte caracteres com acento para ASCII se possível.
    - Substitui caracteres ilegais no Windows (\\ / : * ? " < > |) por hífens.
    - Limpa espaços e hífens repetidos.
    - Trunca para no máximo max_length caracteres antes da extensão.
    """
    ext = extension.lstrip(".")

    # Tenta transliteração ASCII para manter compatibilidade máxima
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    target = ascii_title.lower() if ascii_title.strip() else title.lower()

    # Substitui caracteres proibidos no Windows e caracteres de controle
    clean = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "-", target)
    # Substitui espaços e underscores por hífen
    clean = re.sub(r"[\s_]+", "-", clean)
    # Remove hífens duplicados
    clean = re.sub(r"-+", "-", clean)
    # Remove pontos e hífens das pontas
    clean = clean.strip(".- ")

    if not clean:
        clean = "export"

    # Trunca preservando no máximo max_length caracteres
    clean = clean[:max_length].rstrip(".- ")
    if not clean:
        clean = "export"

    return f"{clean}.{ext}"


def _yaml_quote(val: str) -> str:
    """Escapa valor de string para bloco YAML."""
    escaped = val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{escaped}"'


def format_book_markdown(
    book: Book,
    chapters_with_studies: list[tuple[Chapter, list[Study]]],
    categories: list[str],
    options: ExportOptions,
) -> str:
    """Formata os dados consolidados do livro em Markdown com Frontmatter YAML."""
    lines: list[str] = []
    now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    if options.include_metadata:
        cats_formatted = f'[{", ".join(_yaml_quote(c) for c in categories)}]'
        lines.append("---")
        lines.append(f"title: {_yaml_quote(book.title)}")
        lines.append(f"author: {_yaml_quote(book.author or '')}")
        lines.append(f"subtitle: {_yaml_quote(book.subtitle or '')}")
        lines.append(f"year: {book.year if book.year is not None else 'null'}")
        lines.append(f"categories: {cats_formatted}")
        lines.append(f'date_exported: "{now_iso}"')
        lines.append('app: "Leitorum"')
        lines.append("---")
        lines.append("")

    lines.append(f"# {book.title}")
    lines.append("")

    if book.subtitle:
        lines.append(f"> {book.subtitle}")
        lines.append("")

    if book.author:
        lines.append(f"**Autor:** {book.author}")
        lines.append("")

    if categories:
        lines.append(f"**Categorias:** {', '.join(categories)}")
        lines.append("")

    total_studies = sum(len(studies) for _, studies in chapters_with_studies)
    if total_studies == 0:
        lines.append("*Nenhum estudo registrado para este livro até o momento.*")
        lines.append("")
        return "\n".join(lines)

    for chapter, studies in chapters_with_studies:
        lines.append(f"## {chapter.name}")
        lines.append("")

        for study in studies:
            lines.append(f"### {study.title}")
            lines.append("")
            if study.location:
                lines.append(f"*Localização: {study.location}*")
                lines.append("")

            if options.include_notes and study.notes and study.notes.strip():
                lines.append("#### Minhas Anotações")
                lines.append("")
                lines.append(study.notes.strip())
                lines.append("")

            if options.include_sections:
                if study.summary and study.summary.strip():
                    lines.append("#### Resumo")
                    lines.append("")
                    lines.append(study.summary.strip())
                    lines.append("")

                if study.explanation and study.explanation.strip():
                    lines.append("#### Explicação")
                    lines.append("")
                    lines.append(study.explanation.strip())
                    lines.append("")

                if study.concepts and study.concepts.strip():
                    lines.append("#### Conceitos Principais")
                    lines.append("")
                    lines.append(study.concepts.strip())
                    lines.append("")

                if study.references and study.references.strip():
                    lines.append("#### Referências e Conexões")
                    lines.append("")
                    lines.append(study.references.strip())
                    lines.append("")

            if options.include_source and study.source_response and study.source_response.strip():
                lines.append("#### Resposta Original de Importação")
                lines.append("")
                lines.append(study.source_response.strip())
                lines.append("")

    return "\n".join(lines)


def format_book_text(
    book: Book,
    chapters_with_studies: list[tuple[Chapter, list[Study]]],
    categories: list[str],
    options: ExportOptions,
) -> str:
    """Formata os dados consolidados do livro em Texto Puro com divisores ASCII."""
    lines: list[str] = []
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    divider = "=" * 80
    section_divider = "-" * 80

    lines.append(divider)
    lines.append(book.title.upper())
    lines.append(divider)

    if options.include_metadata:
        if book.subtitle:
            lines.append(f"Subtítulo: {book.subtitle}")
        if book.author:
            lines.append(f"Autor: {book.author}")
        if book.year:
            lines.append(f"Ano: {book.year}")
        if categories:
            lines.append(f"Categorias: {', '.join(categories)}")
        lines.append(f"Exportado em: {now_str}")
        lines.append(divider)

    total_studies = sum(len(studies) for _, studies in chapters_with_studies)
    if total_studies == 0:
        lines.append("")
        lines.append("(Nenhum estudo registrado para este livro até o momento.)")
        lines.append("")
        return "\n".join(lines)

    for chapter, studies in chapters_with_studies:
        lines.append("")
        lines.append(section_divider)
        lines.append(f"CAPÍTULO: {chapter.name.upper()}")
        lines.append(section_divider)

        for study in studies:
            lines.append("")
            lines.append(f"ESTUDO: {study.title}")
            if study.location:
                lines.append(f"Localização: {study.location}")
            lines.append("")

            if options.include_notes and study.notes and study.notes.strip():
                lines.append("[MINHAS ANOTAÇÕES]")
                lines.append(study.notes.strip())
                lines.append("")

            if options.include_sections:
                if study.summary and study.summary.strip():
                    lines.append("[RESUMO]")
                    lines.append(study.summary.strip())
                    lines.append("")

                if study.explanation and study.explanation.strip():
                    lines.append("[EXPLICAÇÃO]")
                    lines.append(study.explanation.strip())
                    lines.append("")

                if study.concepts and study.concepts.strip():
                    lines.append("[CONCEITOS PRINCIPAIS]")
                    lines.append(study.concepts.strip())
                    lines.append("")

                if study.references and study.references.strip():
                    lines.append("[REFERÊNCIAS E CONEXÕES]")
                    lines.append(study.references.strip())
                    lines.append("")

            if options.include_source and study.source_response and study.source_response.strip():
                lines.append("[RESPOSTA ORIGINAL DE IMPORTAÇÃO]")
                lines.append(study.source_response.strip())
                lines.append("")

            lines.append(section_divider)

    return "\n".join(lines)


def format_study_markdown(
    book: Book,
    chapter: Chapter,
    study: Study,
    options: ExportOptions,
) -> str:
    """Formata um estudo individual em Markdown."""
    lines: list[str] = []
    now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    if options.include_metadata:
        lines.append("---")
        lines.append(f"title: {_yaml_quote(study.title)}")
        lines.append(f"book: {_yaml_quote(book.title)}")
        lines.append(f"chapter: {_yaml_quote(chapter.name)}")
        lines.append(f"location: {_yaml_quote(study.location or '')}")
        lines.append(f'date_exported: "{now_iso}"')
        lines.append('app: "Leitorum"')
        lines.append("---")
        lines.append("")

    lines.append(f"# {study.title}")
    lines.append("")
    lines.append(f"*Livro: {book.title} | Capítulo: {chapter.name}*")
    if study.location:
        lines.append(f"*Localização: {study.location}*")
    lines.append("")

    if options.include_notes and study.notes and study.notes.strip():
        lines.append("#### Minhas Anotações")
        lines.append("")
        lines.append(study.notes.strip())
        lines.append("")

    if options.include_sections:
        if study.summary and study.summary.strip():
            lines.append("#### Resumo")
            lines.append("")
            lines.append(study.summary.strip())
            lines.append("")

        if study.explanation and study.explanation.strip():
            lines.append("#### Explicação")
            lines.append("")
            lines.append(study.explanation.strip())
            lines.append("")

        if study.concepts and study.concepts.strip():
            lines.append("#### Conceitos Principais")
            lines.append("")
            lines.append(study.concepts.strip())
            lines.append("")

        if study.references and study.references.strip():
            lines.append("#### Referências e Conexões")
            lines.append("")
            lines.append(study.references.strip())
            lines.append("")

    if options.include_source and study.source_response and study.source_response.strip():
        lines.append("#### Resposta Original de Importação")
        lines.append("")
        lines.append(study.source_response.strip())
        lines.append("")

    return "\n".join(lines)


def format_study_text(
    book: Book,
    chapter: Chapter,
    study: Study,
    options: ExportOptions,
) -> str:
    """Formata um estudo individual em Texto Puro."""
    lines: list[str] = []
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    divider = "=" * 80
    section_divider = "-" * 80

    lines.append(divider)
    lines.append(f"ESTUDO: {study.title.upper()}")
    lines.append(divider)

    if options.include_metadata:
        lines.append(f"Livro: {book.title}")
        lines.append(f"Capítulo: {chapter.name}")
        if study.location:
            lines.append(f"Localização: {study.location}")
        lines.append(f"Exportado em: {now_str}")
        lines.append(divider)

    lines.append("")

    if options.include_notes and study.notes and study.notes.strip():
        lines.append("[MINHAS ANOTAÇÕES]")
        lines.append(study.notes.strip())
        lines.append("")

    if options.include_sections:
        if study.summary and study.summary.strip():
            lines.append("[RESUMO]")
            lines.append(study.summary.strip())
            lines.append("")

        if study.explanation and study.explanation.strip():
            lines.append("[EXPLICAÇÃO]")
            lines.append(study.explanation.strip())
            lines.append("")

        if study.concepts and study.concepts.strip():
            lines.append("[CONCEITOS PRINCIPAIS]")
            lines.append(study.concepts.strip())
            lines.append("")

        if study.references and study.references.strip():
            lines.append("[REFERÊNCIAS E CONEXÕES]")
            lines.append(study.references.strip())
            lines.append("")

    if options.include_source and study.source_response and study.source_response.strip():
        lines.append("[RESPOSTA ORIGINAL DE IMPORTAÇÃO]")
        lines.append(study.source_response.strip())
        lines.append("")

    lines.append(section_divider)

    return "\n".join(lines)


def generate_book_export(
    session: Session,
    book_id: int,
    options: ExportOptions,
) -> tuple[str, str, str]:
    """Gera o conteúdo consolidado de exportação do livro.

    Retorna: (conteúdo, nome_arquivo, media_type)
    Lança: HTTPException(404) se o livro não existir ou estiver na lixeira.
    """
    book = session.get(Book, book_id)
    if book is None or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    chapters = (
        session.query(Chapter)
        .filter(Chapter.book_id == book_id)
        .order_by(Chapter.position, Chapter.id)
        .all()
    )

    chapters_with_studies: list[tuple[Chapter, list[Study]]] = []
    for ch in chapters:
        studies = (
            session.query(Study)
            .filter(Study.chapter_id == ch.id, Study.deleted_at.is_(None))
            .order_by(Study.id)
            .all()
        )
        chapters_with_studies.append((ch, studies))

    categories = [c.name for c in book.categories] if book.categories else []

    if options.format == ExportFormat.MARKDOWN:
        content = format_book_markdown(book, chapters_with_studies, categories, options)
        filename = sanitize_filename(book.title, "md")
        media_type = "text/markdown; charset=utf-8"
    else:
        content = format_book_text(book, chapters_with_studies, categories, options)
        filename = sanitize_filename(book.title, "txt")
        media_type = "text/plain; charset=utf-8"

    return content, filename, media_type


def generate_study_export(
    session: Session,
    study_id: int,
    options: ExportOptions,
) -> tuple[str, str, str]:
    """Gera o conteúdo de exportação de um estudo individual.

    Retorna: (conteúdo, nome_arquivo, media_type)
    Lança: HTTPException(404) se o estudo ou livro estiver na lixeira ou não existir.
    """
    study = session.get(Study, study_id)
    if study is None or study.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")

    chapter = session.get(Chapter, study.chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Capítulo não encontrado.")

    book = session.get(Book, chapter.book_id)
    if book is None or book.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")

    file_title = f"{book.title}-{chapter.name}-{study.title}"

    if options.format == ExportFormat.MARKDOWN:
        content = format_study_markdown(book, chapter, study, options)
        filename = sanitize_filename(file_title, "md")
        media_type = "text/markdown; charset=utf-8"
    else:
        content = format_study_text(book, chapter, study, options)
        filename = sanitize_filename(file_title, "txt")
        media_type = "text/plain; charset=utf-8"

    return content, filename, media_type


def sanitize_folder_name(name: str, max_length: int = 60) -> str:
    """Sanitiza nomes de pastas para o arquivo ZIP no Windows/Linux/macOS."""
    clean = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "-", name.strip())
    clean = re.sub(r"[\s_]+", " ", clean)
    clean = re.sub(r"-+", "-", clean).strip(".- ")
    if not clean:
        clean = "item"
    return clean[:max_length].rstrip(".- ")


def generate_account_export_zip(
    session: Session,
    user: User,
) -> tuple[bytes, str]:
    """Compila o pacote completo de portabilidade do acervo do usuário (LGPD - Opção A).

    Retorna: (zip_bytes, filename)
    - Pastas: [Nome do Livro]/[Nome do Capítulo]/[Nome do Estudo].md
    - Raiz: dados_acervo.json com histórico, categorias, relações e metadados.
    """
    books = (
        session.query(Book)
        .filter(Book.user_id == user.id, Book.deleted_at.is_(None))
        .order_by(Book.id)
        .all()
    )

    profile = session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    preference = session.query(UserPreference).filter(UserPreference.user_id == user.id).first()
    categories = session.query(Category).filter(Category.user_id == user.id).all()

    export_opts = ExportOptions(
        format=ExportFormat.MARKDOWN,
        include_metadata=True,
        include_notes=True,
        include_sections=True,
        include_source=True,
    )

    markdown_files: list[tuple[str, str]] = []
    books_data = []
    total_chapters_count = 0
    total_studies_count = 0

    for book in books:
        chapters = (
            session.query(Chapter)
            .filter(Chapter.book_id == book.id)
            .order_by(Chapter.position, Chapter.id)
            .all()
        )
        total_chapters_count += len(chapters)

        chapters_data = []
        book_folder = sanitize_folder_name(book.title)

        for ch in chapters:
            studies = (
                session.query(Study)
                .filter(Study.chapter_id == ch.id, Study.deleted_at.is_(None))
                .order_by(Study.id)
                .all()
            )
            total_studies_count += len(studies)
            chapter_folder = sanitize_folder_name(ch.name)

            studies_data = []
            for st in studies:
                study_filename = sanitize_folder_name(st.title) + ".md"
                rel_path = f"{book_folder}/{chapter_folder}/{study_filename}"
                content = format_study_markdown(book, ch, st, export_opts)
                markdown_files.append((rel_path, content))

                studies_data.append({
                    "id": st.id,
                    "title": st.title,
                    "location": st.location,
                    "summary": st.summary,
                    "notes": st.notes,
                    "explanation": st.explanation,
                    "concepts": st.concepts,
                    "references": st.references,
                    "created_at": st.created_at.isoformat() if st.created_at else None,
                    "updated_at": st.updated_at.isoformat() if st.updated_at else None,
                })

            chapters_data.append({
                "id": ch.id,
                "name": ch.name,
                "position": ch.position,
                "studies": studies_data,
            })

        books_data.append({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "subtitle": book.subtitle,
            "year": book.year,
            "categories": [c.name for c in book.categories] if book.categories else [],
            "chapters": chapters_data,
        })

    acervo_data = {
        "exported_at": datetime.now(UTC).isoformat(),
        "app": "Leitorum",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "profile": {
            "bio": profile.bio if profile else None,
            "profile_visibility": profile.profile_visibility if profile else "public",
            "dashboard_visibility": profile.dashboard_visibility if profile else "private",
        } if profile else None,
        "preferences": {
            "active_superclass": preference.active_superclass if preference else None,
            "theme_mode": preference.theme_mode if preference else None,
        } if preference else None,
        "total_books": len(books),
        "total_chapters": total_chapters_count,
        "total_studies": total_studies_count,
        "categories": [{"id": cat.id, "name": cat.name} for cat in categories],
        "books": books_data,
    }

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("dados_acervo.json", json.dumps(acervo_data, ensure_ascii=False, indent=2))
        for rel_path, content in markdown_files:
            zf.writestr(rel_path, content)

    now_str = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    filename = f"caderno-dados-{user.username}-{now_str}.zip"
    return zip_buffer.getvalue(), filename

