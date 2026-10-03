"""Configuração dos testes do harness do EXP-002 (rodam sem nenhum modelo instalado)."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1] / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

FONTS = Path(__file__).resolve().parents[3] / "dataset" / "fixtures" / "exp-002" / "fonts"


@pytest.fixture
def fonts():
    return sorted(FONTS.glob("*.ttf"))


@pytest.fixture
def tiny_manifest(tmp_path):
    """Manifesto com 12 "páginas" fictícias (bytes arbitrários) e geometria conhecida."""
    pages = []
    for index in range(12):
        image = tmp_path / "pages" / f"p{index:02d}.bin"
        image.parent.mkdir(exist_ok=True)
        image.write_bytes(f"página {index}".encode())
        lines = [
            {
                "id": "l1",
                "block_id": "b1",
                "text": "a",
                "bbox": [100, 100, 300, 140],
                "polygon": [[100, 100], [300, 100], [300, 140], [100, 140]],
            },
            {
                "id": "l2",
                "block_id": "b2",
                "text": "b",
                "bbox": [100, 200, 300, 240],
                "polygon": [[100, 200], [300, 200], [300, 240], [100, 240]],
            },
        ]
        blocks = [
            {"id": "b1", "type": "title", "bbox": [100, 100, 300, 140], "line_ids": ["l1"]},
            {"id": "b2", "type": "paragraph", "bbox": [100, 200, 300, 240], "line_ids": ["l2"]},
            {"id": "b3", "type": "graphic_box", "bbox": [400, 400, 600, 500], "line_ids": []},
        ]
        pages.append(
            {
                "id": f"p{index:02d}",
                "image": image.relative_to(tmp_path).as_posix(),
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                "width": 800,
                "height": 1000,
                "level": ("clean", "light", "strong")[index % 3],
                "lines": lines,
                "blocks": blocks,
                "ignore": [[400, 400, 600, 500]],
                "page_corners": [[0, 0], [800, 0], [800, 1000], [0, 1000]],
            }
        )
    path = tmp_path / "manifest.json"
    manifest = {"schema": "leitorum-di-pages/1", "dataset": "tiny", "pages": pages}
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return path, tmp_path, manifest
