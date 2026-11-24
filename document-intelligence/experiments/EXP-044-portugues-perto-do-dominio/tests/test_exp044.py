"""EXP-044 — testes com dados fictícios: PAGE XML, alinhamento forçado do texto fixo, filtro de
aceitação, seleção com cota por chave (documento ou pessoa) e troca de caminhos dos scripts do
EXP-031P. Rodar a partir de ``document-intelligence/``:
``uv run pytest experiments/EXP-044-portugues-perto-do-dominio/tests -q``"""

from __future__ import annotations

import sys
import types
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1] / "harness"
sys.path.insert(0, str(HARNESS))

import align  # noqa: E402
import page  # noqa: E402
import pick  # noqa: E402
import run  # noqa: E402

PAGE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">
  <Metadata><Creator>teste</Creator></Metadata>
  <Page imageFilename="folha_001.jpg" imageWidth="1000" imageHeight="800">
    <TextRegion id="r1">
      <Coords points="0,0 1000,0 1000,800 0,800"/>
      <TextLine id="l1">
        <Coords points="10,20 300,20 300,60 10,60"/>
        <Word id="w1"><TextEquiv><Unicode>Livro</Unicode></TextEquiv></Word>
        <TextEquiv><Unicode>Livro de Teste</Unicode></TextEquiv>
      </TextLine>
      <TextLine id="l2">
        <Coords points="10,70 320,72 318,110 12,108"/>
        <TextEquiv><Unicode>Capítulo 1</Unicode></TextEquiv>
      </TextLine>
      <TextLine id="l3">
        <Coords points="10,120 30,120 30,140 10,140"/>
      </TextLine>
    </TextRegion>
  </Page>
</PcGts>""".encode()


def test_page_lines_with_text_and_points():
    doc = page.parse(PAGE_XML)
    assert doc["image"] == "folha_001.jpg"
    assert [ln["id"] for ln in doc["lines"]] == ["l1", "l2"]  # linha sem texto fica de fora
    assert doc["lines"][0]["text"] == "Livro de Teste"  # o texto da linha, não o da palavra
    assert doc["lines"][1]["points"][1] == (320, 72)


def test_page_box_is_clamped():
    assert page.box([(-5, 3), (40, 10), (38, 30)]) == (0, 3, 41, 31)


LETTER = "Livro de teste para o leitor. Capítulo um começa aqui e segue até o fim da página."


def test_align_splits_reference_at_word_boundaries():
    hyps = [
        "Livro de teste para",
        "o leitor. Capitulo um",
        "começa aqui e segue",
        "ate o fim da pagina.",
    ]
    parts = align.align(LETTER, hyps)
    assert parts == [
        "Livro de teste para",
        "o leitor. Capítulo um",
        "começa aqui e segue",
        "até o fim da página.",
    ]


def test_align_with_skipped_word_and_extra_line():
    hyps = [
        "Livro de teste para",
        "o leitor. Capítulo um",
        "xx",
        "começa e segue até",
        "o fim da página.",
    ]
    parts = align.align(LETTER, hyps)
    assert len(parts) == 5
    assert parts[0] == "Livro de teste para"
    assert parts[3].startswith("começa") and parts[3].endswith("até")
    assert parts[4] == "o fim da página."
    assert len(parts[2].split()) <= 1  # a linha a mais recebe pouco ou nada


def test_align_flags_line_that_splits_a_word():
    hyps = [
        "Livro de teste para o lei-",
        "tor. Capitulo um começa aqui",
        "e segue até o fim da página.",
    ]
    detail = align.align_detail(LETTER, hyps)
    assert [split for _, split in detail] == [True, True, False]
    whole = ["Livro de teste para", "o leitor. Capitulo um", "começa aqui e segue", "ate o fim."]
    assert not any(split for _, split in align.align_detail(LETTER, whole))


def test_accept_rules():
    assert align.accept("o leitor Capitulo um", "o leitor. Capítulo um")
    assert not align.accept("zzzz qqqq wwww", "o leitor. Capítulo um")
    assert not align.accept("um", "um")  # menos de 3 palavras
    assert align.page_ok(12) and not align.page_ok(3) and not align.page_ok(40)


def test_accept_ignores_case_and_label_follows_capitals():
    assert align.accept("O LEITOR. CAPITULO UM", "o leitor. Capítulo um")
    assert align.label("O LEITOR. CAPITULO UM", "o leitor. Capítulo um") == "O LEITOR. CAPÍTULO UM"
    assert align.label("o leitor. Capitulo um", "o leitor. Capítulo um") == "o leitor. Capítulo um"


def test_cer():
    assert align.cer("abc", "abc") == 0
    assert align.cer("abd", "abc") == 1 / 3
    assert align.cer("", "") == 0


def test_pick_equal_quota_per_key_and_deterministic():
    rows = [(f"s:{k}-{n}", k) for k in ("a", "b", "c") for n in range(10 if k != "c" else 2)]
    first = pick.by_key(rows, 12, seed="x")
    assert first == pick.by_key(rows, 12, seed="x")
    keys = [item.split(":")[1][0] for item in first]
    assert keys.count("c") == 2 and keys.count("a") == 5 and keys.count("b") == 5
    assert len(pick.by_key(rows, 100, seed="x")) == 22


def test_pick_by_priority_takes_recent_tiers_first():
    rows = [(f"s:a{n}", "a", 0) for n in range(4)] + [(f"s:b{n}", "b", 1) for n in range(10)]
    rows += [(f"s:c{n}", "c", 1) for n in range(10)] + [(f"s:d{n}", "d", 2) for n in range(10)]
    chosen = pick.by_priority(rows, 12, seed="x")
    assert all(f"s:a{n}" in chosen for n in range(4))  # camada 0 inteira
    assert (
        sum(c.startswith("s:b") for c in chosen) == 4
        and sum(c.startswith("s:c") for c in chosen) == 4
    )
    assert not any(c.startswith("s:d") for c in chosen)
    assert chosen == pick.by_priority(rows, 12, seed="x")


def test_century_from_document_name():
    assert pick.century("1406206/IL-2747_(1651-1653)") == 17
    assert pick.century("1266513/IL_13436_(1796)") == 18
    assert pick.century("1255349/IL_7772-257") is None


def test_run_swaps_paths(tmp_path):
    module = types.SimpleNamespace(WORK=Path("velho"), MODELS=Path("velho"))
    run.configure(module, tmp_path / "w", tmp_path / "m")
    assert module.WORK == tmp_path / "w" and module.MODELS == tmp_path / "m"
