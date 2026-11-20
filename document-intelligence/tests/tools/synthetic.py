"""Páginas fictícias para testar a ferramenta de anotação. Nenhum conteúdo do caderno do usuário:
"imagens" de bytes arbitrários (os testes não decodificam imagem) e textos inventados."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.anotar.paths import Paths

FAKE_TEXTS = ["Capítulo 1 de teste", "linha fictícia $x^2$", "Livro de Teste, p. 3"]


def make_dataset(root: Path, pages: int = 2, *, split_test: tuple[str, ...] = ("p01",)) -> Paths:
    """Cria a árvore de dados mínima: hashes registrados, manifesto de teste, índice preparado,
    imagem de trabalho falsa e saída do motor com 3 caixas por página."""
    paths = Paths(data_root=root / "dataset", splits=root / "splits")
    paths.splits.mkdir(parents=True)
    paths.images.mkdir(parents=True)
    paths.motor.mkdir(parents=True)
    registered, index = {}, {}
    for number in range(1, pages + 1):
        pid = f"p{number:02d}"
        original = f"foto original fictícia {pid}".encode()
        work = f"imagem de trabalho fictícia {pid}".encode()
        (paths.images / f"{pid}.jpg").write_bytes(work)
        sha = hashlib.sha256(original).hexdigest()
        registered[pid] = {"sha256": sha, "width": 1000, "height": 1400}
        index[pid] = {
            "sha256": sha,
            "work_sha256": hashlib.sha256(work).hexdigest(),
            "width": 1000,
            "height": 1400,
            "scale": 1.0,
            "motor_ok": True,
        }
        lines = [
            {"text": text, "confidence": 0.9, "bbox": [50, 100 + 120 * i, 900, 180 + 120 * i]}
            for i, text in enumerate(FAKE_TEXTS)
        ]
        (paths.motor / f"{pid}.json").write_text(
            json.dumps({"schema": "leitorum-motor/1", "lines": lines}), encoding="utf-8"
        )
    paths.registered.write_text(
        json.dumps({"schema": "exp-027-pages/1", "count": pages, "pages": registered}),
        encoding="utf-8",
    )
    (paths.splits / "test-manifest.json").write_text(
        json.dumps({"pages": {pid: {} for pid in split_test}}), encoding="utf-8"
    )
    paths.index.write_text(json.dumps({"pages": index}), encoding="utf-8")
    return paths
