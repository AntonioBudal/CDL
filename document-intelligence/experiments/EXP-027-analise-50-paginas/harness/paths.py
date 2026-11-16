"""Caminhos do EXP-027. Os dados ficam fora do Git, em ``dataset/raw/exp-027`` e
``dataset/processed/exp-027``; a raiz pode ser trocada por ``EXP027_DATA_ROOT`` (quando o código
roda numa worktree e os dados estão no checkout principal)."""

from __future__ import annotations

import os
from pathlib import Path

EXPERIMENT = Path(__file__).resolve().parents[1]
DI_ROOT = EXPERIMENT.parents[1]
DATA_ROOT = Path(os.environ.get("EXP027_DATA_ROOT") or DI_ROOT / "dataset")
RAW = DATA_ROOT / "raw" / "exp-027"
PROCESSED = DATA_ROOT / "processed" / "exp-027"

PHOTOS = RAW / "fotos"
EXPORT = RAW / "export"
REFERENCE = RAW / "referencia"  # pNN.txt escritos pelo usuário (ground truth)
CLASSIFICATION = RAW / "classificacao"  # pNN.json: classes manuais por página

MANIFEST = PROCESSED / "manifest.json"
MOTOR_OUT = PROCESSED / "motor"  # pNN.json do leitorum_motor
TOOL = PROCESSED / "transcrever"  # imagens e recortes da ferramenta de transcrição
EXAMPLES = PROCESSED / "exemplos"
SPLITS = EXPERIMENT / "splits"  # versionado: só hashes e categorias

MOTOR_DIR = Path(
    os.environ.get("EXP027_MOTOR_DIR") or DI_ROOT.parent / "caderno-leitura-0.1" / "motor"
)
MOTOR_PYTHON = MOTOR_DIR / ".venv" / "Scripts" / "python.exe"
MOTOR_CONFIG = MOTOR_DIR / "config.json"


def page_id(index: int) -> str:
    return f"p{index:02d}"
