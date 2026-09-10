import pytest

from app.services.import_parser import parse_response


def warning_keys(parsed):
    return {(warning.code, warning.section) for warning in parsed.warnings}


def test_standard_response_preserves_original_and_section_bodies():
    source = (
        "## Resumo\n  Ideia com ação, atenção e café.  \n\n"
        "## Explicação\nPrimeiro parágrafo.\n\nSegundo parágrafo.\n\n"
        "## Conceitos\n- **Atenção**: significado.\n- Outro termo.\n\n"
        "## Referências\nNenhuma referência externa verificada."
    )
    parsed = parse_response(source)
    assert parsed.source_response == source
    assert parsed.sections == {
        "summary": "  Ideia com ação, atenção e café.  \n\n",
        "explanation": "Primeiro parágrafo.\n\nSegundo parágrafo.\n\n",
        "concepts": "- **Atenção**: significado.\n- Outro termo.\n\n",
        "references": "Nenhuma referência externa verificada.",
    }
    assert parsed.unassigned_text == ""
    assert parsed.warnings == ()


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_plain_titles_case_accents_and_line_endings(newline):
    source = newline.join([
        "", "   RESUMO  ", "Resumo com café.", "explicacao", "Explicação com ação.",
        "## CoNcEiToS ##", "Conceito.", "  REFERE\u0302NCIAS\t", "Referência.", "",
    ])
    parsed = parse_response(source)
    assert parsed.source_response == source
    assert parsed.unassigned_text == newline
    assert parsed.sections == {
        "summary": "Resumo com café." + newline,
        "explanation": "Explicação com ação." + newline,
        "concepts": "Conceito." + newline,
        "references": "Referência." + newline,
    }
    assert not parsed.warnings


def test_preamble_repeats_and_out_of_order_sections_keep_every_body():
    source = (
        "Introdução para revisar.\n\n"
        "## Conceitos\nConceito original.\n"
        "## Resumo\nPrimeiro resumo.\n"
        "## Explicação\nExplicação original.\n"
        "## RESUMO\nSegundo resumo.\n"
        "Resumo\nTerceiro resumo.\n"
        "## Referências\nSem fontes externas."
    )
    parsed = parse_response(source)
    assert parsed.source_response == source
    assert parsed.unassigned_text == "Introdução para revisar.\n\n"
    assert parsed.sections == {
        "summary": "Primeiro resumo.\nSegundo resumo.\nTerceiro resumo.\n",
        "explanation": "Explicação original.\n",
        "concepts": "Conceito original.\n",
        "references": "Sem fontes externas.",
    }
    assert [(w.code, w.section, w.line) for w in parsed.warnings] == [
        ("unassigned_text", None, 1),
        ("repeated_section", "summary", 9),
        ("repeated_section", "summary", 11),
    ]


def test_missing_and_empty_sections_are_distinct_and_never_filled():
    parsed = parse_response("## Resumo\nTexto.\n## Explicação\n \t\n## Referências")
    assert parsed.sections == {"summary": "Texto.\n", "explanation": " \t\n", "concepts": "", "references": ""}
    assert warning_keys(parsed) == {
        ("missing_section", "concepts"),
        ("empty_section", "explanation"),
        ("empty_section", "references"),
    }


def test_unrecognized_response_is_returned_entirely_for_manual_review():
    source = "  Uma resposta livre.\n\nResumo: ainda é uma frase.\n## Conclusão\nTexto final.\n"
    parsed = parse_response(source)
    assert parsed.source_response == parsed.unassigned_text == source
    assert not any(parsed.sections.values())
    assert warning_keys(parsed) == {
        ("no_sections_found", None),
        ("missing_section", "summary"), ("missing_section", "explanation"),
        ("missing_section", "concepts"), ("missing_section", "references"),
    }


@pytest.mark.parametrize("opening,inside,closing", [
    ("```markdown", "## Resumo\nExplicação\n", "```"),
    ("~~~texto", "## Conceitos\nReferências\n", "~~~"),
    ("  ````python", "```\n~~~\n## Referências\n```` com texto\n", "   `````\t"),
    ("~~~~", "~~~\n```\n## Explicação\n", "~~~~~"),
])
def test_fences_protect_internal_headings_and_require_matching_close(opening, inside, closing):
    body = f"Exemplo:\n{opening}\n{inside}{closing}\nDepois do código.\n"
    source = (
        f"## Resumo\n{body}## Explicação\nExplicação real.\n"
        "## Conceitos\nConceito real.\n## Referências\nFonte real."
    )
    parsed = parse_response(source)
    assert parsed.sections["summary"] == body
    assert parsed.sections["explanation"] == "Explicação real.\n"
    assert parsed.sections["concepts"] == "Conceito real.\n"
    assert parsed.sections["references"] == "Fonte real."
    assert parsed.source_response == source
    assert not parsed.warnings


def test_unclosed_fence_preserves_rest_and_reports_opening_line():
    body = "Texto.\n```markdown\n## Explicação\nDentro do código.\n## Referências\nTambém dentro."
    parsed = parse_response("## Resumo\n" + body)
    assert parsed.sections["summary"] == body
    assert parsed.sections["explanation"] == parsed.sections["references"] == ""
    warning = next(w for w in parsed.warnings if w.code == "unclosed_code_block")
    assert (warning.section, warning.line) == ("summary", 3)


def test_response_wrapped_in_code_remains_unassigned():
    source = "```markdown\n## Resumo\nTexto.\n## Explicação\nTexto.\n```\n"
    parsed = parse_response(source)
    assert parsed.source_response == parsed.unassigned_text == source
    assert not any(parsed.sections.values())
    assert ("no_sections_found", None) in warning_keys(parsed)
    assert ("unclosed_code_block", None) not in warning_keys(parsed)


def test_inline_subheadings_quotes_lists_and_indented_code_are_preserved():
    body = (
        "A frase contém ## Explicação, mas não é um título.\n"
        "### Conceitos\n**Referências**\n# Resumo\n## Conclusão\n"
        "> ## Explicação\n- Resumo\n1. Referências\n"
        "    ## Explicação\n\tConceitos\n"
        "<script>alert('texto, sem execução')</script>\n"
        "Parágrafo com separador Unicode: \u2028Resumo\u2028continuação.\n"
    )
    parsed = parse_response("## Resumo\n" + body + "## Referências\nFonte.")
    assert parsed.sections["summary"] == body
    assert parsed.sections["references"] == "Fonte."
    assert warning_keys(parsed) == {("missing_section", "explanation"), ("missing_section", "concepts")}


def test_inline_backticks_are_not_an_open_fence_and_initial_bom_is_preserved():
    source = "\ufeff## Resumo\n```texto `inline`\n## Explicação\nTexto."
    parsed = parse_response(source)
    assert parsed.source_response == source
    assert parsed.sections["summary"] == "```texto `inline`\n"
    assert parsed.sections["explanation"] == "Texto."
    assert not any(w.code == "unclosed_code_block" for w in parsed.warnings)
