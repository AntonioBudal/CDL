"""Divisão do formato de importação; sem dependências de HTTP ou de banco."""

from dataclasses import dataclass
import re
import unicodedata


SECTION_LABELS = {
    "summary": "Resumo",
    "explanation": "Explicação",
    "concepts": "Conceitos",
    "references": "Referências",
}

SECTION_SYNONYMS = {
    "summary": (
        "resumo",
        "visao geral",
        "visao-geral",
        "sintese",
        "ideia central",
        "introducao",
    ),
    "explanation": (
        "explicacao",
        "aprofundamento",
        "desenvolvimento",
        "analise",
        "compreensao",
        "detalhamento",
    ),
    "concepts": (
        "conceitos",
        "conceitos-chave",
        "termos",
        "termos-chave",
        "vocabulario",
        "glossario",
        "glossario e termos",
        "definicoes",
    ),
    "references": (
        "referencias",
        "fontes",
        "fontes consultadas",
        "bibliografia",
        "leituras complementares",
        "obras citadas",
    ),
}

# Apenas CR/LF delimitam linhas. Os terminadores continuam no conteúdo devolvido.
_LINES = re.compile(r"[^\r\n]*(?:\r\n|\r|\n|$)")
_HEADING_MARKDOWN = re.compile(r"#{1,4}[ \t]+(.+)")
_CLOSING_HASHES = re.compile(r"[ \t]+#+[ \t]*$")
_ORDINAL_PREFIX = re.compile(
    r"^(?:(?:secao|seção|parte|capitulo|capítulo)\s+)?(?:[0-9]+|[ivxlcdm]+)[\.\-\:\)][ \t]*(.*)",
    re.IGNORECASE,
)
_BOLD_WRAP = re.compile(r"^(\*\*|__)(.+?)\1$")
_TRAILING_PUNCT = re.compile(r"[\s\:\-]+$")
_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")


def _normalize_label(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn").strip()


_SECTION_KEYS = {
    _normalize_label(synonym): key
    for key, synonyms in SECTION_SYNONYMS.items()
    for synonym in synonyms
}


@dataclass(frozen=True)
class ImportWarning:
    code: str
    message: str
    section: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class ParsedResponse:
    source_response: str
    sections: dict[str, str]
    unassigned_text: str
    warnings: tuple[ImportWarning, ...]


@dataclass(frozen=True)
class _CodeFence:
    marker: str
    length: int
    line: int


def _clean_heading(raw: str) -> str:
    m = _HEADING_MARKDOWN.fullmatch(raw)
    if m:
        raw = _CLOSING_HASHES.sub("", m.group(1)).strip(" \t")
    else:
        raw = _CLOSING_HASHES.sub("", raw).strip(" \t")

    raw = _TRAILING_PUNCT.sub("", raw).strip(" \t")

    bm = _BOLD_WRAP.fullmatch(raw)
    if bm:
        raw = bm.group(2).strip(" \t")

    om = _ORDINAL_PREFIX.fullmatch(raw)
    if om:
        raw = om.group(1).strip(" \t")

    bm = _BOLD_WRAP.fullmatch(raw)
    if bm:
        raw = bm.group(2).strip(" \t")

    raw = _TRAILING_PUNCT.sub("", raw).strip(" \t")
    return raw


def _section_heading(line: str) -> str | None:
    indentation = len(line) - len(line.lstrip(" "))
    # Títulos recuados > 3 espaços (código), com tab, em citação (>) ou itens de lista não-ordenada (- , * , + ) não são separadores.
    stripped = line[indentation:]
    if (
        indentation > 3
        or stripped.startswith(("\t", ">"))
        or (len(stripped) >= 2 and stripped[0] in "-*+" and stripped[1] in " \t")
    ):
        return None
    raw = stripped.rstrip(" \t")
    if not raw:
        return None
    cleaned = _clean_heading(raw)
    normalized = _normalize_label(cleaned)
    return _SECTION_KEYS.get(normalized)


def parse_response(source_response: str) -> ParsedResponse:
    """Reconhece títulos fixos, preservando literalmente os corpos e a origem.

    Ocorrências repetidas são concatenadas na seção correspondente, em ordem.
    Só as linhas de títulos reconhecidos são retiradas dos corpos; elas continuam
    em source_response. A função não preenche, renderiza nem salva conteúdo.
    """
    parts: dict[str, list[str]] = {key: [] for key in SECTION_LABELS}
    unassigned: list[str] = []
    first_heading_lines: dict[str, int] = {}
    occurrence_warnings: list[ImportWarning] = []
    current_section: str | None = None
    fence: _CodeFence | None = None

    for line_number, match in enumerate(_LINES.finditer(source_response), start=1):
        original_line = match.group()
        if not original_line:
            continue
        line = original_line.rstrip("\r\n")
        # Um BOM inicial pode vir de um arquivo UTF-8; apenas a comparação o ignora.
        if line_number == 1:
            line = line.removeprefix("\ufeff")
        destination = unassigned if current_section is None else parts[current_section]
        fence_match = _FENCE.fullmatch(line)

        if fence is not None:
            destination.append(original_line)
            if fence_match is not None:
                marker, suffix = fence_match.groups()
                if (
                    marker[0] == fence.marker
                    and len(marker) >= fence.length
                    and not suffix.strip(" \t")
                ):
                    fence = None
            continue

        if fence_match is not None:
            marker, suffix = fence_match.groups()
            if marker[0] == "~" or "`" not in suffix:
                fence = _CodeFence(marker[0], len(marker), line_number)
                destination.append(original_line)
                continue

        heading = _section_heading(line)
        if heading is None:
            destination.append(original_line)
            continue

        if heading in first_heading_lines:
            occurrence_warnings.append(ImportWarning(
                code="repeated_section",
                message=(
                    f"Título '{SECTION_LABELS[heading]}' repetido. Os conteúdos foram "
                    "reunidos nesta seção, na ordem em que apareceram. Revise a divisão."
                ),
                section=heading,
                line=line_number,
            ))
        else:
            first_heading_lines[heading] = line_number
        current_section = heading

    sections = {key: "".join(chunks) for key, chunks in parts.items()}
    unassigned_text = "".join(unassigned)
    warnings: list[ImportWarning] = []
    if not first_heading_lines:
        warnings.append(ImportWarning(
            code="no_sections_found",
            message="Nenhum título reconhecido. Todo o texto está em 'Texto não associado' para revisão.",
        ))
    elif unassigned_text.strip():
        warnings.append(ImportWarning(
            code="unassigned_text",
            message="Há texto antes da primeira seção. Revise 'Texto não associado' antes de salvar.",
            line=1,
        ))
    warnings.extend(occurrence_warnings)
    if fence is not None:
        warnings.append(ImportWarning(
            code="unclosed_code_block",
            message=(
                "Bloco de código sem fechamento. O texto a partir da abertura foi preservado "
                "como código; confira se algum título ficou dentro dele."
            ),
            section=current_section,
            line=fence.line,
        ))
    for key, label in SECTION_LABELS.items():
        if key not in first_heading_lines:
            warnings.append(ImportWarning(
                code="missing_section", message=f"Seção '{label}' não encontrada.", section=key,
            ))
        elif not sections[key].strip():
            warnings.append(ImportWarning(
                code="empty_section", message=f"Seção '{label}' sem conteúdo.",
                section=key, line=first_heading_lines[key],
            ))
    return ParsedResponse(source_response, sections, unassigned_text, tuple(warnings))
