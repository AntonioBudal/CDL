"""Configuração dos testes do harness do EXP-018 (rodam sem nenhum modelo instalado)."""

import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1] / "harness"
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))
