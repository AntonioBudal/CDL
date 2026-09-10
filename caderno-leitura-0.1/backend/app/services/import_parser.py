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

# Apenas CR/LF delimitam linhas. Os terminadores continuam no conteúdo devolvido.
_LINES = re.compile(r"[^\r\n]*(?:\r\n|\r|\n|$)")
_HEADING = re.compile(r"##[ \t]+(.+)")
_CLOSING_HASHES = re.compile(r"[ \t]+#+[ \t]*$")
_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")


def _normalize_label(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


_SECTION_KEYS = {_normalize_label(label): key for key, label in SECTION_LABELS.items()}


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


def _section_heading(line: str) -> str | None:
    indentation = len(line) - len(line.lstrip(" "))
    # Títulos recuados como código, em citações ou em listas não são separadores.
    if indentation > 3 or line[indentation:].startswith("\t"):
        return None
    label = line[indentation:].rstrip(" \t")
    heading = _HEADING.fullmatch(label)
    if heading is not None:
        label = _CLOSING_HASHES.sub("", heading.group(1)).strip(" \t")
    return _SECTION_KEYS.get(_normalize_label(label))


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
