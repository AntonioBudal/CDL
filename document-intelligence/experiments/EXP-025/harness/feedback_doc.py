"""EXP-025, F05: pacote do simulador do EXP-024 → registro ``leitorum-feedback/1`` do Leitorum.

O Leitorum (feature 091-B) guarda a sugestão (texto, trechos, linhas com posição), as 4 seções
salvas e, na digitalização, as contagens do diff de leitura. Não guarda nota (``rating``).
"""

from __future__ import annotations

import adapter_deps  # noqa: F401  (caminhos do EXP-023 e do EXP-024)
import diff_signal as ds


def to_document(feedback: dict, segments: list[dict]) -> dict:
    """``segments`` são os trechos que o organizador devolveu (com ``confidence``), na ordem."""
    organizer = feedback["organizer"]
    saved = feedback["saved"]
    reverted = bool(organizer.get("reverted"))
    part = {
        "outcome": "reverted" if reverted else "saved",
        "text": organizer["text"],
        "segments": [
            {k: s[k] for k in ("index", "start", "end", "section", "confidence", "review")}
            for s in segments
        ],
        "lines": organizer.get("layout"),
    }
    if not reverted:
        part["saved_sections"] = saved
    edits = ds.align_reading(feedback["reading"]["source_lines"], saved)
    kinds = dict.fromkeys(("same", "ocr", "rewrite", "ambiguous"), 0)
    for edit in edits:
        kinds[edit.kind] += 1
    return {
        "schema": "leitorum-feedback/1",
        "origin": "digitize",
        "organizer": part,
        "reading": {"lines": len(edits), "kinds": kinds},
    }
