"""Caminhos e importações comuns do EXP-028A. Reaproveita o harness do EXP-027 (``align``,
``textnorm``, ``delatex``, ``split``) e a ferramenta F-DI-13.01 (``tools.anotar``) por importação,
sem copiar código. Os dados ficam fora do Git, em ``dataset/``; a raiz pode ser trocada por
``EXP028A_DATA_ROOT`` (worktree ou testes), e a pasta de divisões por ``EXP028A_SPLITS_DIR``."""

from __future__ import annotations

import os
import sys
from pathlib import Path

EXPERIMENT = Path(__file__).resolve().parents[1]
DI_ROOT = EXPERIMENT.parents[1]
EXP027 = DI_ROOT / "experiments" / "EXP-027-analise-50-paginas"

for folder in (EXP027 / "harness", DI_ROOT):
    if str(folder) not in sys.path:
        sys.path.append(str(folder))

DATA_ROOT = Path(os.environ.get("EXP028A_DATA_ROOT") or DI_ROOT / "dataset")
# Divisões versionadas: no mesmo lugar que a ferramenta lê (test-manifest, dev-val, 2ª passada)
SPLITS = Path(os.environ.get("EXP028A_SPLITS_DIR") or EXP027 / "splits")

RAW027 = DATA_ROOT / "raw" / "exp-027"
GEMINI_REFERENCE = RAW027 / "referencia"  # pNN.txt: referência v2 (Gemini), em parágrafos
CLASSIFICATION = RAW027 / "classificacao"
PRODUCT_READING = DATA_ROOT / "processed" / "exp-027" / "motor"  # leitura do produto (originais)
RAW = DATA_ROOT / "raw" / "exp-028a"
REFERENCE_V3 = RAW / "referencia-v3"
PROCESSED = DATA_ROOT / "processed" / "exp-028a"

SEED = "exp-028a"
DRAFT_LABEL = "gemini-alinhado"


def anotar_paths():
    from tools.anotar.paths import Paths

    return Paths(data_root=DATA_ROOT, splits=SPLITS)
