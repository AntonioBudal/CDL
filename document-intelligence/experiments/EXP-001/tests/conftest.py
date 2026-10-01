"""Configuração dos testes do harness do EXP-001 (rodam sem nenhum modelo instalado)."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1] / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

TEXTS = [
    "Capítulo 1: a lógica formal",
    "ATENÇÃO: as funções inversas.",
    "O que é o pêndulo simples?",
    "Exemplo 2: somar 10 e 32 dá 42.",
    '"Não há atalho", disse o tutor Zózimo.',
]


@pytest.fixture
def tiny_manifest(tmp_path):
    """Manifesto com 25 linhas fictícias; os "arquivos de imagem" são bytes arbitrários."""
    lines = []
    for index in range(25):
        image = tmp_path / "lines" / f"line-{index:02d}.bin"
        image.parent.mkdir(exist_ok=True)
        image.write_bytes(f"imagem sintética {index}".encode())
        lines.append(
            {
                "id": f"t-{index:02d}",
                "image": image.relative_to(tmp_path).as_posix(),
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                "text": TEXTS[index % len(TEXTS)],
            }
        )
    manifest = {"schema": "leitorum-di-lines/1", "dataset": "tiny", "origin": "synthetic"}
    manifest["lines"] = lines
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return path, tmp_path, manifest
