"""EXP-024 (F03): sinais implícitos do diff de revisão. Só textos fictícios."""

from __future__ import annotations

import diff_signal as ds
import streams

TEXT = (
    "O capítulo trata da leitura ativa.\n"
    "Leitura ativa: ler fazendo perguntas.\n"
    "Isso importa porque fixa as ideias.\n"
    "- A margem e o centro — Lúcia Pereira Dantas"
)


def segments(sections: list[str]) -> list[dict]:
    out, pos = [], 0
    for k, (line, section) in enumerate(zip(TEXT.split("\n"), sections, strict=False)):
        out.append({"index": k, "start": pos, "end": pos + len(line), "section": section})
        pos += len(line) + 1
    return out


def test_units_kept_moved_edited_and_deleted():
    suggested = segments(["summary", "explanation", "explanation", "explanation"])
    saved = {
        "summary": "O capítulo trata da leitura ativa.",
        "explanation": "Isso importa porque fixa as ideias.",
        "concepts": "Leitura ativa: ler fazendo perguntas.",
        "references": "",
    }
    outcomes = ds.align_units(TEXT, suggested, saved)
    assert [o.outcome for o in outcomes] == ["kept", "moved", "kept", "deleted"]
    assert outcomes[1].final == "concepts"

    saved["references"] = "- A margem e o centro — Lucia P. Dantas"
    edited = ds.align_units(TEXT, suggested, saved)[3]
    assert edited.outcome == "edited" and edited.final == "references"


def test_repeated_text_is_found_once_each():
    text = "Rever depois.\nRever depois."
    segs = [
        {"index": 0, "start": 0, "end": 13, "section": "explanation"},
        {"index": 1, "start": 14, "end": 27, "section": "explanation"},
    ]
    saved = {
        "summary": "",
        "explanation": "Rever depois.\nRever depois.",
        "concepts": "",
        "references": "",
    }
    assert [o.outcome for o in ds.align_units(text, segs, saved)] == ["kept", "kept"]


def test_reading_correction_is_ocr_and_rewrite_is_not():
    kind, distance = ds.classify_edit(
        "A leitura ativa nuda a forrna de ler.", "A leitura ativa muda a forma de ler."
    )
    assert kind == "ocr" and distance < 0.2
    rewrite = streams.load()["rewrites"][0]
    assert ds.classify_edit("A leitura ativa muda a forma de ler.", rewrite)[0] == "rewrite"
    assert ds.classify_edit("igual", "igual") == ("same", 0.0)


def test_levenshtein_ops_capture_accent_and_digraph_confusions():
    distance, ops = ds.levenshtein_ops("acao", "ação")
    assert distance == 2 and all(len(r) <= 2 and len(t) <= 2 for r, t in ops)
    assert "".join(t for _r, t in ops).count("ç") == 1
    distance, ops = ds.levenshtein_ops("forrna", "forma")
    assert distance == 2 and ops  # "rn" lido como "m": dois alinhamentos de mesmo custo


def test_align_reading_matches_lines_and_word_pairs():
    source = ["O capitulo trata da leitura atíva.", "Isso irnporta porque fixa as ideias."]
    saved = {
        "summary": "O capítulo trata da leitura ativa.",
        "explanation": "Isso importa porque fixa as ideias.",
    }
    edits = ds.align_reading(source, saved)
    assert [e.kind for e in edits] == ["ocr", "ocr"]
    assert ("capitulo", "capítulo") in edits[0].word_pairs
    assert ("irnporta", "importa") in edits[1].word_pairs


def test_organizer_patch_lists_only_moves():
    suggested = segments(["summary", "explanation", "explanation", "references"])
    saved = {
        "summary": "O capítulo trata da leitura ativa.",
        "explanation": "Isso importa porque fixa as ideias.",
        "concepts": "Leitura ativa: ler fazendo perguntas.",
        "references": "- A margem e o centro — Lúcia Pereira Dantas",
    }
    patch = ds.to_organizer_patch(ds.align_units(TEXT, suggested, saved))
    assert patch == [{"op": "replace", "path": "/segments/1/section", "value": "concepts"}]
