"""EXP-044 — leitura de PAGE XML (qualquer versão do esquema): imagem da página e linhas com
polígono e texto da própria linha (o ``TextEquiv`` filho direto de ``TextLine``, não o das
palavras)."""

from __future__ import annotations

import xml.etree.ElementTree as ET


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(element, name):
    return next((c for c in element if _local(c.tag) == name), None)


def parse(data: bytes) -> dict:
    root = ET.fromstring(data)
    page_el = next(e for e in root.iter() if _local(e.tag) == "Page")
    lines = []
    for line in (e for e in page_el.iter() if _local(e.tag) == "TextLine"):
        coords = _child(line, "Coords")
        equiv = _child(line, "TextEquiv")
        unicode_el = _child(equiv, "Unicode") if equiv is not None else None
        text = (unicode_el.text or "").strip() if unicode_el is not None else ""
        if coords is None or not text:
            continue
        points = [
            tuple(int(float(v)) for v in pair.split(","))
            for pair in coords.get("points", "").split()
        ]
        if len(points) < 2:
            continue
        lines.append({"id": line.get("id"), "points": points, "text": text})
    return {"image": page_el.get("imageFilename"), "lines": lines}


def box(points) -> tuple[int, int, int, int]:
    """Caixa do polígono, como no EXP-031P/043 (início limitado a 0, fim inclusivo)."""
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return max(0, int(min(xs))), max(0, int(min(ys))), int(max(xs)) + 1, int(max(ys)) + 1
