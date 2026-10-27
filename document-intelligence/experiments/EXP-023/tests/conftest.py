"""Configuração dos testes do harness do EXP-023 (só dados fictícios do próprio experimento)."""

import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1] / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))
