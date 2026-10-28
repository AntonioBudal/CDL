"""Configuração dos testes do EXP-024 (só dados fictícios do próprio experimento e do EXP-023)."""

import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1] / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))
