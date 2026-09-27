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

from app.models import Book, Category, Chapter, Study, StudyHighlight, User, UserPreference, UserProfile
from app.schemas.export import ExportFormat, ExportOptions, ExportType

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


def inject_highlights_into_text(
    text: str,
    highlights: list[StudyHighlight],
    fmt: ExportFormat = ExportFormat.MARKDOWN,
    note_start_index: int = 1,
) -> tuple[str, list[tuple[int, str]], int]:
    """Injeta destaques no texto de uma seção usando percurso reverso por offset.

    Retorna: (texto_modificado, lista_de_notas_de_rodape, proximo_indice_de_nota)
    Onde lista_de_notas_de_rodape = [(numero_nota, texto_da_nota), ...]
    """
    if not text or not highlights:
        return text, [], note_start_index

    valid_hls = [h for h in highlights if h.selected_text and h.selected_text.strip()]
    if not valid_hls:
        return text, [], note_start_index

    # 1. Ordena por ordem de leitura (ascendente) para atribuir índices sequenciais de nota
    valid_hls.sort(key=lambda h: (h.start_offset, h.end_offset))

    indexed_hls: list[tuple[StudyHighlight, int | None, str]] = []
    current_note_idx = note_start_index
    footnotes: list[tuple[int, str]] = []

    for hl in valid_hls:
        note_text = (hl.note or "").strip()
        has_note = False
        footnote_desc = ""

        if hl.kind == "question":
            has_note = True
            q_text = note_text if note_text else "Pergunta de retenção"
            if fmt == ExportFormat.MARKDOWN:
                footnote_desc = f"**[Pergunta]** {q_text}"
            else:
                footnote_desc = f"[Pergunta] {q_text}"
        elif hl.kind == "hidden":
            has_note = True
            desc = note_text if note_text else "(Trecho marcado para memorização)"
            if fmt == ExportFormat.MARKDOWN:
                footnote_desc = f"**[Termo Ocluído]** {desc}"
            else:
                footnote_desc = f"[Termo Ocluído] {desc}"
        elif hl.kind == "note":
            has_note = True
            desc = note_text if note_text else "Nota de estudo"
            if fmt == ExportFormat.MARKDOWN:
                footnote_desc = f"**[Anotação]** {desc}"
            else:
                footnote_desc = f"[Anotação] {desc}"
        elif hl.kind == "quote":
            has_note = True
            desc = note_text if note_text else "Citação destacada"
            if fmt == ExportFormat.MARKDOWN:
                footnote_desc = f"**[Citação]** {desc}"
            else:
                footnote_desc = f"[Citação] {desc}"
        elif hl.kind == "highlight":
            if note_text:
                has_note = True
                if fmt == ExportFormat.MARKDOWN:
                    footnote_desc = f"**[Destaque]** {note_text}"
                else:
                    footnote_desc = f"[Destaque] {note_text}"

        assigned_num = None
        if has_note:
            assigned_num = current_note_idx
            footnotes.append((assigned_num, footnote_desc))
            current_note_idx += 1

        indexed_hls.append((hl, assigned_num, footnote_desc))

    # 2. Ordena por offset descendente para substituição de trás para frente sem descolamento
    indexed_hls.sort(key=lambda item: (item[0].start_offset, item[0].end_offset), reverse=True)

    result_text = text
    replaced_intervals: list[tuple[int, int]] = []

    for hl, note_num, _ in indexed_hls:
        target = hl.selected_text
        start = hl.start_offset
        end = hl.end_offset

        actual_slice = result_text[start:end] if 0 <= start <= end <= len(result_text) else ""
        match_start = -1
        match_end = -1

        if actual_slice == target:
            match_start = start
            match_end = end
        else:
            found_idx = result_text.find(target, max(0, start - 20))
            if found_idx == -1:
                found_idx = result_text.find(target)
            if found_idx != -1:
                match_start = found_idx
                match_end = found_idx + len(target)

        if match_start == -1 or match_end == -1:
            continue

        collides = any(not (match_end <= r_start or match_start >= r_end) for r_start, r_end in replaced_intervals)
        if collides:
            continue

        if fmt == ExportFormat.MARKDOWN:
            if note_num is not None:
                replacement = f"=={target}==[^{note_num}]"
            else:
                replacement = f"=={target}=="
        else:
            if note_num is not None:
                replacement = f"«{target}» [{note_num}]"
            else:
                replacement = f"«{target}»"

        result_text = result_text[:match_start] + replacement + result_text[match_end:]
        replaced_intervals.append((match_start, match_end))

    return result_text, footnotes, current_note_idx


def append_section_footnotes(
    content: str,
    footnotes: list[tuple[int, str]],
    fmt: ExportFormat = ExportFormat.MARKDOWN,
) -> str:
    """Anexa notas de rodapé numeradas ao final do conteúdo de uma seção."""
    if not footnotes:
        return content

    if fmt == ExportFormat.MARKDOWN:
        fn_lines = [""]
        for num, desc in footnotes:
            fn_lines.append(f"[^{num}]: {desc}")
        fn_lines.append("")
        return content + "\n".join(fn_lines)
    else:
        fn_lines = ["", "-" * 80, "NOTAS DA SEÇÃO:"]
        for num, desc in footnotes:
            fn_lines.append(f"[{num}] {desc}")
        fn_lines.append("-" * 80)
        fn_lines.append("")
        return content + "\n".join(fn_lines)


def _format_section_with_highlights(
    text: str,
    section_name: str,
    highlights: list[StudyHighlight] | None,
    options: ExportOptions,
    fmt: ExportFormat,
) -> str:
    """Aplica injeção de destaques e anotações no texto da seção se ativado."""
    cleaned = text.strip()
    if not options.include_highlights or not highlights:
        return cleaned
    section_hls = [h for h in highlights if h.section == section_name]
    if not section_hls:
        return cleaned
    modified, footnotes, _ = inject_highlights_into_text(cleaned, section_hls, fmt=fmt, note_start_index=1)
    return append_section_footnotes(modified, footnotes, fmt=fmt).strip()


def format_book_markdown(
    book: Book,
    chapters_with_studies: list[tuple[Chapter, list[Study]]],
    categories: list[str],
    options: ExportOptions,
    highlights_map: dict[int, list[StudyHighlight]] | None = None,
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
        if options.include_highlights and highlights_map:
            total_hls = sum(len(hls) for hls in highlights_map.values())
            total_qs = sum(sum(1 for h in hls if h.kind == "question") for hls in highlights_map.values())
            lines.append(f"total_highlights: {total_hls}")
            lines.append(f"total_questions: {total_qs}")
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

    hls_map = highlights_map or {}

    for chapter, studies in chapters_with_studies:
        lines.append(f"## {chapter.name}")
        lines.append("")

        for study in studies:
            st_hls = hls_map.get(study.id, [])
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
                    lines.append(_format_section_with_highlights(study.summary, "summary", st_hls, options, ExportFormat.MARKDOWN))
                    lines.append("")

                if study.explanation and study.explanation.strip():
                    lines.append("#### Explicação")
                    lines.append("")
                    lines.append(_format_section_with_highlights(study.explanation, "explanation", st_hls, options, ExportFormat.MARKDOWN))
                    lines.append("")

                if study.concepts and study.concepts.strip():
                    lines.append("#### Conceitos Principais")
                    lines.append("")
                    lines.append(_format_section_with_highlights(study.concepts, "concepts", st_hls, options, ExportFormat.MARKDOWN))
                    lines.append("")

                if study.references and study.references.strip():
                    lines.append("#### Referências e Conexões")
                    lines.append("")
                    lines.append(_format_section_with_highlights(study.references, "references", st_hls, options, ExportFormat.MARKDOWN))
                    lines.append("")

            if options.include_source and study.source_response and study.source_response.strip():
                lines.append("#### Resposta Original de Importação")
                lines.append("")
                lines.append(_format_section_with_highlights(study.source_response, "source_response", st_hls, options, ExportFormat.MARKDOWN))
                lines.append("")

    return "\n".join(lines)


def format_book_text(
    book: Book,
    chapters_with_studies: list[tuple[Chapter, list[Study]]],
    categories: list[str],
    options: ExportOptions,
    highlights_map: dict[int, list[StudyHighlight]] | None = None,
) -> str:
    """Formata os dados consolidados do livro em Texto Puro com divisores ASCII."""
    lines: list[str] = []
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    divider = "=" * 80
    section_divider = "-" * 80

    lines.append(divider)
    lines.append(book.title.upper())
    lines.append(divider)

    hls_map = highlights_map or {}

    if options.include_metadata:
        if book.subtitle:
            lines.append(f"Subtítulo: {book.subtitle}")
        if book.author:
            lines.append(f"Autor: {book.author}")
        if book.year:
            lines.append(f"Ano: {book.year}")
        if categories:
            lines.append(f"Categorias: {', '.join(categories)}")
        if options.include_highlights and hls_map:
            total_hls = sum(len(hls) for hls in hls_map.values())
            total_qs = sum(sum(1 for h in hls if h.kind == "question") for hls in hls_map.values())
            lines.append(f"Destaques: {total_hls} | Perguntas: {total_qs}")
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
            st_hls = hls_map.get(study.id, [])
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
                    lines.append(_format_section_with_highlights(study.summary, "summary", st_hls, options, ExportFormat.TEXT))
                    lines.append("")

                if study.explanation and study.explanation.strip():
                    lines.append("[EXPLICAÇÃO]")
                    lines.append(_format_section_with_highlights(study.explanation, "explanation", st_hls, options, ExportFormat.TEXT))
                    lines.append("")

                if study.concepts and study.concepts.strip():
                    lines.append("[CONCEITOS PRINCIPAIS]")
                    lines.append(_format_section_with_highlights(study.concepts, "concepts", st_hls, options, ExportFormat.TEXT))
                    lines.append("")

                if study.references and study.references.strip():
                    lines.append("[REFERÊNCIAS E CONEXÕES]")
                    lines.append(_format_section_with_highlights(study.references, "references", st_hls, options, ExportFormat.TEXT))
                    lines.append("")

            if options.include_source and study.source_response and study.source_response.strip():
                lines.append("[RESPOSTA ORIGINAL DE IMPORTAÇÃO]")
                lines.append(_format_section_with_highlights(study.source_response, "source_response", st_hls, options, ExportFormat.TEXT))
                lines.append("")

            lines.append(section_divider)

    return "\n".join(lines)


def format_study_markdown(
    book: Book,
    chapter: Chapter,
    study: Study,
    options: ExportOptions,
    highlights: list[StudyHighlight] | None = None,
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
        if options.include_highlights and highlights:
            q_cnt = sum(1 for h in highlights if h.kind == "question")
            lines.append(f"total_highlights: {len(highlights)}")
            lines.append(f"total_questions: {q_cnt}")
        lines.append(f'date_exported: "{now_iso}"')
        lines.append('app: "Leitorum"')
        lines.append("---")
        lines.append("")

    lines.append(f"# {study.title}")
    lines.append("")
    lines.append(f"*Livro: {book.title} | Capítulo: {chapter.name}*")
    if study.location:
        lines.append(f"*Localização: {study.location}*")
    if options.include_highlights and highlights:
        q_cnt = sum(1 for h in highlights if h.kind == "question")
        lines.append(f"*Destaques: {len(highlights)} | Perguntas: {q_cnt}*")
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
            lines.append(_format_section_with_highlights(study.summary, "summary", highlights, options, ExportFormat.MARKDOWN))
            lines.append("")

        if study.explanation and study.explanation.strip():
            lines.append("#### Explicação")
            lines.append("")
            lines.append(_format_section_with_highlights(study.explanation, "explanation", highlights, options, ExportFormat.MARKDOWN))
            lines.append("")

        if study.concepts and study.concepts.strip():
            lines.append("#### Conceitos Principais")
            lines.append("")
            lines.append(_format_section_with_highlights(study.concepts, "concepts", highlights, options, ExportFormat.MARKDOWN))
            lines.append("")

        if study.references and study.references.strip():
            lines.append("#### Referências e Conexões")
            lines.append("")
            lines.append(_format_section_with_highlights(study.references, "references", highlights, options, ExportFormat.MARKDOWN))
            lines.append("")

    if options.include_source and study.source_response and study.source_response.strip():
        lines.append("#### Resposta Original de Importação")
        lines.append("")
        lines.append(_format_section_with_highlights(study.source_response, "source_response", highlights, options, ExportFormat.MARKDOWN))
        lines.append("")

    return "\n".join(lines)


def format_study_text(
    book: Book,
    chapter: Chapter,
    study: Study,
    options: ExportOptions,
    highlights: list[StudyHighlight] | None = None,
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
        if options.include_highlights and highlights:
            q_cnt = sum(1 for h in highlights if h.kind == "question")
            lines.append(f"Destaques: {len(highlights)} | Perguntas: {q_cnt}")
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
            lines.append(_format_section_with_highlights(study.summary, "summary", highlights, options, ExportFormat.TEXT))
            lines.append("")

        if study.explanation and study.explanation.strip():
            lines.append("[EXPLICAÇÃO]")
            lines.append(_format_section_with_highlights(study.explanation, "explanation", highlights, options, ExportFormat.TEXT))
            lines.append("")

        if study.concepts and study.concepts.strip():
            lines.append("[CONCEITOS PRINCIPAIS]")
            lines.append(_format_section_with_highlights(study.concepts, "concepts", highlights, options, ExportFormat.TEXT))
            lines.append("")

        if study.references and study.references.strip():
            lines.append("[REFERÊNCIAS E CONEXÕES]")
            lines.append(_format_section_with_highlights(study.references, "references", highlights, options, ExportFormat.TEXT))
            lines.append("")

    if options.include_source and study.source_response and study.source_response.strip():
        lines.append("[RESPOSTA ORIGINAL DE IMPORTAÇÃO]")
        lines.append(_format_section_with_highlights(study.source_response, "source_response", highlights, options, ExportFormat.TEXT))
        lines.append("")

    lines.append(section_divider)

    return "\n".join(lines)


def format_study_digest_markdown(
    book: Book,
    chapter: Chapter,
    study: Study,
    highlights: list[StudyHighlight],
    options: ExportOptions,
) -> str:
    """Formata o Caderno de Revisão (Digest) de um estudo individual em Markdown."""
    lines: list[str] = []
    now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    questions = [h for h in highlights if h.kind == "question"]
    occlusions = [h for h in highlights if h.kind == "hidden"]
    notes_and_quotes = [h for h in highlights if h.kind in ("note", "quote", "highlight")]

    if options.include_metadata:
        lines.append("---")
        lines.append(f'title: {_yaml_quote(f"Caderno de Revisão — {study.title}")}')
        lines.append(f"book: {_yaml_quote(book.title)}")
        lines.append(f"chapter: {_yaml_quote(chapter.name)}")
        lines.append('type: "digest"')
        lines.append(f'mode: "{"exercise" if options.exercise_mode else "study"}"')
        lines.append(f"total_questions: {len(questions)}")
        lines.append(f"total_occlusions: {len(occlusions)}")
        lines.append(f"total_notes: {len(notes_and_quotes)}")
        lines.append(f'date_exported: "{now_iso}"')
        lines.append('app: "Leitorum"')
        lines.append("---")
        lines.append("")

    mode_label = "Exercício (Respostas no Gabarito Final)" if options.exercise_mode else "Estudo (Respostas Integradas)"
    lines.append(f"# Caderno de Revisão — {study.title}")
    lines.append("")
    lines.append(f"> **Livro:** {book.title} | **Capítulo:** {chapter.name}")
    if study.location:
        lines.append(f"> **Localização:** {study.location}")
    lines.append(f"> **Modo:** {mode_label}")
    lines.append(f"> **Exportado em:** {now_str} | **Perguntas:** {len(questions)} | **Termos Ocluídos:** {len(occlusions)} | **Notas & Citações:** {len(notes_and_quotes)}")
    lines.append("")

    if not highlights:
        lines.append("*Este estudo não possui destaques, perguntas ou anotações registradas até o momento.*")
        lines.append("")
        return "\n".join(lines)

    if questions:
        lines.append("---")
        lines.append("")
        lines.append("## 1. Perguntas de Retenção (Active Recall)")
        lines.append("")
        for idx, q in enumerate(questions, 1):
            q_text = q.note.strip() if q.note else "Pergunta sem enunciado"
            lines.append(f"{idx}. {q_text}")
            if options.exercise_mode:
                lines.append("   *Resposta:* __________________________________________________")
            else:
                lines.append(f"   - **Resposta:** {q.selected_text}")
            lines.append("")

    if occlusions:
        lines.append("---")
        lines.append("")
        lines.append("## 2. Termos Ocluídos (Cloze Deletion)")
        lines.append("")
        for idx, occl in enumerate(occlusions, 1):
            pref = occl.prefix.strip()
            suff = occl.suffix.strip()
            target_str = "[ _______ ]" if options.exercise_mode else f"=={occl.selected_text}=="
            context_str = f"{pref} {target_str} {suff}".strip()
            lines.append(f"{idx}. ...{context_str}...")
            if occl.note and occl.note.strip():
                lines.append(f"   *(Dica: {occl.note.strip()})*")
            lines.append("")

    if notes_and_quotes:
        lines.append("---")
        lines.append("")
        lines.append("## 3. Notas Marginais & Citações")
        lines.append("")
        for idx, item in enumerate(notes_and_quotes, 1):
            if item.kind == "quote":
                lines.append(f"{idx}. > \"{item.selected_text}\"")
                if item.note and item.note.strip():
                    lines.append(f"   *(Comentário: {item.note.strip()})*")
            elif item.kind == "note":
                lines.append(f"{idx}. **Trecho:** \"=={item.selected_text}==\"")
                if item.note and item.note.strip():
                    lines.append(f"   - **Anotação:** {item.note.strip()}")
            else:
                lines.append(f"{idx}. **Grifo:** \"=={item.selected_text}==\"")
                if item.note and item.note.strip():
                    lines.append(f"   - **Anotação:** {item.note.strip()}")
            lines.append("")

    if options.exercise_mode and (questions or occlusions):
        lines.append("---")
        lines.append("")
        lines.append("## Gabarito de Revisão")
        lines.append("")
        if questions:
            lines.append("### Perguntas de Retenção")
            lines.append("")
            for idx, q in enumerate(questions, 1):
                q_text = q.note.strip() if q.note else "Pergunta"
                lines.append(f"{idx}. **Pergunta:** {q_text}")
                lines.append(f"   - **Resposta:** {q.selected_text}")
                lines.append("")
        if occlusions:
            lines.append("### Termos Ocluídos")
            lines.append("")
            for idx, occl in enumerate(occlusions, 1):
                lines.append(f"{idx}. **Termo Ocluído:** {occl.selected_text}")
                lines.append("")

    return "\n".join(lines)


def format_study_digest_text(
    book: Book,
    chapter: Chapter,
    study: Study,
    highlights: list[StudyHighlight],
    options: ExportOptions,
) -> str:
    """Formata o Caderno de Revisão (Digest) de um estudo individual em Texto Puro."""
    lines: list[str] = []
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    divider = "=" * 80
    section_divider = "-" * 80

    questions = [h for h in highlights if h.kind == "question"]
    occlusions = [h for h in highlights if h.kind == "hidden"]
    notes_and_quotes = [h for h in highlights if h.kind in ("note", "quote", "highlight")]

    lines.append(divider)
    lines.append(f"CADERNO DE REVISÃO: {study.title.upper()}")
    lines.append(divider)

    if options.include_metadata:
        mode_label = "EXERCÍCIO (Gabarito no final)" if options.exercise_mode else "ESTUDO (Respostas integradas)"
        lines.append(f"Livro: {book.title}")
        lines.append(f"Capítulo: {chapter.name}")
        if study.location:
            lines.append(f"Localização: {study.location}")
        lines.append(f"Modo: {mode_label}")
        lines.append(f"Estatísticas: {len(questions)} perguntas, {len(occlusions)} termos ocluídos, {len(notes_and_quotes)} notas/citações")
        lines.append(f"Exportado em: {now_str}")
        lines.append(divider)

    lines.append("")

    if not highlights:
        lines.append("(Este estudo não possui destaques, perguntas ou anotações registradas até o momento.)")
        lines.append("")
        return "\n".join(lines)

    if questions:
        lines.append(section_divider)
        lines.append("1. PERGUNTAS DE RETENÇÃO (ACTIVE RECALL)")
        lines.append(section_divider)
        lines.append("")
        for idx, q in enumerate(questions, 1):
            q_text = q.note.strip() if q.note else "Pergunta sem enunciado"
            lines.append(f"{idx}. {q_text}")
            if options.exercise_mode:
                lines.append("   Resposta: __________________________________________________")
            else:
                lines.append(f"   Resposta: {q.selected_text}")
            lines.append("")

    if occlusions:
        lines.append(section_divider)
        lines.append("2. TERMOS OCLUÍDOS (CLOZE DELETION)")
        lines.append(section_divider)
        lines.append("")
        for idx, occl in enumerate(occlusions, 1):
            pref = occl.prefix.strip()
            suff = occl.suffix.strip()
            target_str = "[ _______ ]" if options.exercise_mode else f"«{occl.selected_text}»"
            context_str = f"{pref} {target_str} {suff}".strip()
            lines.append(f"{idx}. ...{context_str}...")
            if occl.note and occl.note.strip():
                lines.append(f"   (Dica: {occl.note.strip()})")
            lines.append("")

    if notes_and_quotes:
        lines.append(section_divider)
        lines.append("3. NOTAS MARGINAIS E CITAÇÕES")
        lines.append(section_divider)
        lines.append("")
        for idx, item in enumerate(notes_and_quotes, 1):
            if item.kind == "quote":
                lines.append(f"{idx}. CITAÇÃO: \"{item.selected_text}\"")
                if item.note and item.note.strip():
                    lines.append(f"   Observação: {item.note.strip()}")
            elif item.kind == "note":
                lines.append(f"{idx}. TRECHO: «{item.selected_text}»")
                if item.note and item.note.strip():
                    lines.append(f"   Anotação: {item.note.strip()}")
            else:
                lines.append(f"{idx}. GRIFO: «{item.selected_text}»")
                if item.note and item.note.strip():
                    lines.append(f"   Anotação: {item.note.strip()}")
            lines.append("")

    if options.exercise_mode and (questions or occlusions):
        lines.append(divider)
        lines.append("GABARITO DE REVISÃO")
        lines.append(divider)
        lines.append("")
        if questions:
            lines.append("[PERGUNTAS DE RETENÇÃO]")
            for idx, q in enumerate(questions, 1):
                q_text = q.note.strip() if q.note else "Pergunta"
                lines.append(f"{idx}. {q_text}")
                lines.append(f"   Resposta: {q.selected_text}")
                lines.append("")
        if occlusions:
            lines.append("[TERMOS OCLUÍDOS]")
            for idx, occl in enumerate(occlusions, 1):
                lines.append(f"{idx}. Termo Ocluído: {occl.selected_text}")
                lines.append("")

    return "\n".join(lines)


def format_book_digest_markdown(
    book: Book,
    chapters_with_studies: list[tuple[Chapter, list[Study]]],
    categories: list[str],
    options: ExportOptions,
    highlights_map: dict[int, list[StudyHighlight]] | None = None,
) -> str:
    """Formata o Caderno de Revisão (Digest) consolidado do livro em Markdown."""
    lines: list[str] = []
    now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    hls_map = highlights_map or {}
    all_highlights: list[tuple[Chapter, Study, StudyHighlight]] = []
    for ch, studies in chapters_with_studies:
        for st in studies:
            for hl in hls_map.get(st.id, []):
                all_highlights.append((ch, st, hl))

    all_questions = [(ch, st, h) for ch, st, h in all_highlights if h.kind == "question"]
    all_occlusions = [(ch, st, h) for ch, st, h in all_highlights if h.kind == "hidden"]
    all_notes = [(ch, st, h) for ch, st, h in all_highlights if h.kind in ("note", "quote", "highlight")]

    if options.include_metadata:
        cats_formatted = f'[{", ".join(_yaml_quote(c) for c in categories)}]'
        lines.append("---")
        lines.append(f'title: {_yaml_quote(f"Caderno de Revisão — {book.title}")}')
        lines.append(f"author: {_yaml_quote(book.author or '')}")
        lines.append(f"categories: {cats_formatted}")
        lines.append('type: "digest"')
        lines.append(f'mode: "{"exercise" if options.exercise_mode else "study"}"')
        lines.append(f"total_questions: {len(all_questions)}")
        lines.append(f"total_occlusions: {len(all_occlusions)}")
        lines.append(f"total_notes: {len(all_notes)}")
        lines.append(f'date_exported: "{now_iso}"')
        lines.append('app: "Leitorum"')
        lines.append("---")
        lines.append("")

    mode_label = "Exercício (Respostas no Gabarito Final)" if options.exercise_mode else "Estudo (Respostas Integradas)"
    lines.append(f"# Caderno de Revisão — {book.title}")
    lines.append("")
    if book.author:
        lines.append(f"**Autor:** {book.author}")
        lines.append("")
    lines.append(f"> **Modo:** {mode_label}")
    lines.append(f"> **Exportado em:** {now_str} | **Perguntas:** {len(all_questions)} | **Termos Ocluídos:** {len(all_occlusions)} | **Notas & Citações:** {len(all_notes)}")
    lines.append("")

    if not all_highlights:
        lines.append("*Este livro não possui destaques, perguntas ou anotações registradas até o momento.*")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Sumário da Obra")
    lines.append("")
    for ch, studies in chapters_with_studies:
        lines.append(f"- **{ch.name}**")
        for st in studies:
            st_hls = hls_map.get(st.id, [])
            q_cnt = sum(1 for h in st_hls if h.kind == "question")
            o_cnt = sum(1 for h in st_hls if h.kind == "hidden")
            lines.append(f"  - {st.title} *({q_cnt} perguntas, {o_cnt} oclusões)*")
    lines.append("")

    if all_questions:
        lines.append("---")
        lines.append("")
        lines.append("## 1. Perguntas de Retenção (Active Recall)")
        lines.append("")
        for idx, (ch, st, q) in enumerate(all_questions, 1):
            q_text = q.note.strip() if q.note else "Pergunta sem enunciado"
            lines.append(f"{idx}. **[{ch.name} / {st.title}]** {q_text}")
            if options.exercise_mode:
                lines.append("   *Resposta:* __________________________________________________")
            else:
                lines.append(f"   - **Resposta:** {q.selected_text}")
            lines.append("")

    if all_occlusions:
        lines.append("---")
        lines.append("")
        lines.append("## 2. Termos Ocluídos (Cloze Deletion)")
        lines.append("")
        for idx, (ch, st, occl) in enumerate(all_occlusions, 1):
            pref = occl.prefix.strip()
            suff = occl.suffix.strip()
            target_str = "[ _______ ]" if options.exercise_mode else f"=={occl.selected_text}=="
            context_str = f"{pref} {target_str} {suff}".strip()
            lines.append(f"{idx}. **[{ch.name} / {st.title}]** ...{context_str}...")
            if occl.note and occl.note.strip():
                lines.append(f"   *(Dica: {occl.note.strip()})*")
            lines.append("")

    if all_notes:
        lines.append("---")
        lines.append("")
        lines.append("## 3. Notas Marginais & Citações")
        lines.append("")
        for idx, (ch, st, item) in enumerate(all_notes, 1):
            if item.kind == "quote":
                lines.append(f"{idx}. **[{ch.name} / {st.title}]** > \"{item.selected_text}\"")
                if item.note and item.note.strip():
                    lines.append(f"   *(Comentário: {item.note.strip()})*")
            elif item.kind == "note":
                lines.append(f"{idx}. **[{ch.name} / {st.title}]** \"=={item.selected_text}==\"")
                if item.note and item.note.strip():
                    lines.append(f"   - **Anotação:** {item.note.strip()}")
            else:
                lines.append(f"{idx}. **[{ch.name} / {st.title}]** \"=={item.selected_text}==\"")
                if item.note and item.note.strip():
                    lines.append(f"   - **Anotação:** {item.note.strip()}")
            lines.append("")

    if options.exercise_mode and (all_questions or all_occlusions):
        lines.append("---")
        lines.append("")
        lines.append("## Gabarito de Revisão")
        lines.append("")
        if all_questions:
            lines.append("### Perguntas de Retenção")
            lines.append("")
            for idx, (ch, st, q) in enumerate(all_questions, 1):
                q_text = q.note.strip() if q.note else "Pergunta"
                lines.append(f"{idx}. **[{ch.name} / {st.title}]** {q_text}")
                lines.append(f"   - **Resposta:** {q.selected_text}")
                lines.append("")
        if all_occlusions:
            lines.append("### Termos Ocluídos")
            lines.append("")
            for idx, (ch, st, occl) in enumerate(all_occlusions, 1):
                lines.append(f"{idx}. **[{ch.name} / {st.title}]**")
                lines.append(f"   - **Termo Ocluído:** {occl.selected_text}")
                lines.append("")

    return "\n".join(lines)


def format_book_digest_text(
    book: Book,
    chapters_with_studies: list[tuple[Chapter, list[Study]]],
    categories: list[str],
    options: ExportOptions,
    highlights_map: dict[int, list[StudyHighlight]] | None = None,
) -> str:
    """Formata o Caderno de Revisão (Digest) consolidado do livro em Texto Puro."""
    lines: list[str] = []
    now_str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    divider = "=" * 80
    section_divider = "-" * 80

    hls_map = highlights_map or {}
    all_highlights: list[tuple[Chapter, Study, StudyHighlight]] = []
    for ch, studies in chapters_with_studies:
        for st in studies:
            for hl in hls_map.get(st.id, []):
                all_highlights.append((ch, st, hl))

    all_questions = [(ch, st, h) for ch, st, h in all_highlights if h.kind == "question"]
    all_occlusions = [(ch, st, h) for ch, st, h in all_highlights if h.kind == "hidden"]
    all_notes = [(ch, st, h) for ch, st, h in all_highlights if h.kind in ("note", "quote", "highlight")]

    lines.append(divider)
    lines.append(f"CADERNO DE REVISÃO: {book.title.upper()}")
    lines.append(divider)

    if options.include_metadata:
        mode_label = "EXERCÍCIO (Gabarito no final)" if options.exercise_mode else "ESTUDO (Respostas integradas)"
        if book.author:
            lines.append(f"Autor: {book.author}")
        if categories:
            lines.append(f"Categorias: {', '.join(categories)}")
        lines.append(f"Modo: {mode_label}")
        lines.append(f"Estatísticas: {len(all_questions)} perguntas, {len(all_occlusions)} termos ocluídos, {len(all_notes)} notas/citações")
        lines.append(f"Exportado em: {now_str}")
        lines.append(divider)

    lines.append("")

    if not all_highlights:
        lines.append("(Este livro não possui destaques, perguntas ou anotações registradas até o momento.)")
        lines.append("")
        return "\n".join(lines)

    lines.append("SUMÁRIO DA OBRA")
    lines.append(section_divider)
    for ch, studies in chapters_with_studies:
        lines.append(f"CAPÍTULO: {ch.name}")
        for st in studies:
            st_hls = hls_map.get(st.id, [])
            q_cnt = sum(1 for h in st_hls if h.kind == "question")
            o_cnt = sum(1 for h in st_hls if h.kind == "hidden")
            lines.append(f"  - {st.title} ({q_cnt} perguntas, {o_cnt} oclusões)")
    lines.append("")

    if all_questions:
        lines.append(section_divider)
        lines.append("1. PERGUNTAS DE RETENÇÃO (ACTIVE RECALL)")
        lines.append(section_divider)
        lines.append("")
        for idx, (ch, st, q) in enumerate(all_questions, 1):
            q_text = q.note.strip() if q.note else "Pergunta sem enunciado"
            lines.append(f"{idx}. [{ch.name} / {st.title}] {q_text}")
            if options.exercise_mode:
                lines.append("   Resposta: __________________________________________________")
            else:
                lines.append(f"   Resposta: {q.selected_text}")
            lines.append("")

    if all_occlusions:
        lines.append(section_divider)
        lines.append("2. TERMOS OCLUÍDOS (CLOZE DELETION)")
        lines.append(section_divider)
        lines.append("")
        for idx, (ch, st, occl) in enumerate(all_occlusions, 1):
            pref = occl.prefix.strip()
            suff = occl.suffix.strip()
            target_str = "[ _______ ]" if options.exercise_mode else f"«{occl.selected_text}»"
            context_str = f"{pref} {target_str} {suff}".strip()
            lines.append(f"{idx}. [{ch.name} / {st.title}] ...{context_str}...")
            if occl.note and occl.note.strip():
                lines.append(f"   (Dica: {occl.note.strip()})")
            lines.append("")

    if all_notes:
        lines.append(section_divider)
        lines.append("3. NOTAS MARGINAIS E CITAÇÕES")
        lines.append(section_divider)
        lines.append("")
        for idx, (ch, st, item) in enumerate(all_notes, 1):
            if item.kind == "quote":
                lines.append(f"{idx}. [{ch.name} / {st.title}] CITAÇÃO: \"{item.selected_text}\"")
                if item.note and item.note.strip():
                    lines.append(f"   Observação: {item.note.strip()}")
            elif item.kind == "note":
                lines.append(f"{idx}. [{ch.name} / {st.title}] TRECHO: «{item.selected_text}»")
                if item.note and item.note.strip():
                    lines.append(f"   Anotação: {item.note.strip()}")
            else:
                lines.append(f"{idx}. [{ch.name} / {st.title}] GRIFO: «{item.selected_text}»")
                if item.note and item.note.strip():
                    lines.append(f"   Anotação: {item.note.strip()}")
            lines.append("")

    if options.exercise_mode and (all_questions or all_occlusions):
        lines.append(divider)
        lines.append("GABARITO DE REVISÃO")
        lines.append(divider)
        lines.append("")
        if all_questions:
            lines.append("[PERGUNTAS DE RETENÇÃO]")
            for idx, (ch, st, q) in enumerate(all_questions, 1):
                q_text = q.note.strip() if q.note else "Pergunta"
                lines.append(f"{idx}. [{ch.name} / {st.title}] {q_text}")
                lines.append(f"   Resposta: {q.selected_text}")
                lines.append("")
        if all_occlusions:
            lines.append("[TERMOS OCLUÍDOS]")
            for idx, (ch, st, occl) in enumerate(all_occlusions, 1):
                lines.append(f"{idx}. [{ch.name} / {st.title}]")
                lines.append(f"   Termo Ocluído: {occl.selected_text}")
                lines.append("")

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
    all_study_ids: list[int] = []
    for ch in chapters:
        studies = (
            session.query(Study)
            .filter(Study.chapter_id == ch.id, Study.deleted_at.is_(None))
            .order_by(Study.id)
            .all()
        )
        chapters_with_studies.append((ch, studies))
        all_study_ids.extend(s.id for s in studies)

    categories = [c.name for c in book.categories] if book.categories else []

    highlights_map: dict[int, list[StudyHighlight]] = {}
    if all_study_ids:
        all_hls = (
            session.query(StudyHighlight)
            .filter(StudyHighlight.study_id.in_(all_study_ids))
            .order_by(StudyHighlight.study_id.asc(), StudyHighlight.start_offset.asc(), StudyHighlight.id.asc())
            .all()
        )
        for h in all_hls:
            highlights_map.setdefault(h.study_id, []).append(h)

    if options.export_type == ExportType.DIGEST:
        prefix = "caderno-revisao-exercicio" if options.exercise_mode else "caderno-revisao"
        if options.format == ExportFormat.MARKDOWN:
            content = format_book_digest_markdown(book, chapters_with_studies, categories, options, highlights_map)
            filename = sanitize_filename(f"{prefix}-{book.title}", "md")
            media_type = "text/markdown; charset=utf-8"
        else:
            content = format_book_digest_text(book, chapters_with_studies, categories, options, highlights_map)
            filename = sanitize_filename(f"{prefix}-{book.title}", "txt")
            media_type = "text/plain; charset=utf-8"
        return content, filename, media_type

    if options.format == ExportFormat.MARKDOWN:
        content = format_book_markdown(book, chapters_with_studies, categories, options, highlights_map=highlights_map)
        filename = sanitize_filename(book.title, "md")
        media_type = "text/markdown; charset=utf-8"
    else:
        content = format_book_text(book, chapters_with_studies, categories, options, highlights_map=highlights_map)
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

    highlights = (
        session.query(StudyHighlight)
        .filter(StudyHighlight.study_id == study_id)
        .order_by(StudyHighlight.start_offset.asc(), StudyHighlight.id.asc())
        .all()
    )

    if options.export_type == ExportType.DIGEST:
        prefix = "caderno-revisao-exercicio" if options.exercise_mode else "caderno-revisao"
        if options.format == ExportFormat.MARKDOWN:
            content = format_study_digest_markdown(book, chapter, study, highlights, options)
            filename = sanitize_filename(f"{prefix}-{book.title}-{study.title}", "md")
            media_type = "text/markdown; charset=utf-8"
        else:
            content = format_study_digest_text(book, chapter, study, highlights, options)
            filename = sanitize_filename(f"{prefix}-{book.title}-{study.title}", "txt")
            media_type = "text/plain; charset=utf-8"
        return content, filename, media_type

    file_title = f"{book.title}-{chapter.name}-{study.title}"

    if options.format == ExportFormat.MARKDOWN:
        content = format_study_markdown(book, chapter, study, options, highlights=highlights)
        filename = sanitize_filename(file_title, "md")
        media_type = "text/markdown; charset=utf-8"
    else:
        content = format_study_text(book, chapter, study, options, highlights=highlights)
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

