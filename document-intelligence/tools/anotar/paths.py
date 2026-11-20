"""Caminhos da ferramenta de anotação. Os dados ficam fora do Git, em ``dataset/``; a raiz pode ser
trocada por ``ANOTAR_DATA_ROOT`` (para rodar numa worktree com os dados no checkout principal, ou
nos testes, com uma pasta temporária)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DI_ROOT = Path(__file__).resolve().parents[2]
STATIC = Path(__file__).resolve().parent / "static"
SCHEMA_FILE = Path(__file__).resolve().parent / "schema" / "di-annotation-1.schema.json"
EXP027_SPLITS = DI_ROOT / "experiments" / "EXP-027-analise-50-paginas" / "splits"


@dataclass(frozen=True)
class Paths:
    data_root: Path
    splits: Path

    @property
    def photos(self) -> Path:
        """Fotos originais do celular (as mesmas do EXP-027)."""
        return self.data_root / "raw" / "exp-027" / "fotos"

    @property
    def annotations(self) -> Path:
        """``pNN.json`` no formato ``di-annotation/1``: dado do autor, como a referência."""
        return self.data_root / "raw" / "anotacao"

    @property
    def prepared(self) -> Path:
        return self.data_root / "processed" / "anotacao"

    @property
    def images(self) -> Path:
        return self.prepared / "imagens"

    @property
    def motor(self) -> Path:
        return self.prepared / "motor"

    @property
    def index(self) -> Path:
        return self.prepared / "pages.json"

    @property
    def registered(self) -> Path:
        """Hashes das fotos registrados pelo EXP-027 (versionado; só hashes e tamanhos)."""
        return self.splits / "pages-sha256.json"


def default_paths() -> Paths:
    data_root = Path(os.environ.get("ANOTAR_DATA_ROOT") or DI_ROOT / "dataset")
    splits = Path(os.environ.get("ANOTAR_SPLITS_DIR") or EXP027_SPLITS)
    return Paths(data_root=data_root, splits=splits)


MOTOR_DIR = Path(
    os.environ.get("ANOTAR_MOTOR_DIR") or DI_ROOT.parent / "caderno-leitura-0.1" / "motor"
)
MOTOR_PYTHON = MOTOR_DIR / ".venv" / "Scripts" / "python.exe"
MOTOR_CONFIG = MOTOR_DIR / "config.json"
