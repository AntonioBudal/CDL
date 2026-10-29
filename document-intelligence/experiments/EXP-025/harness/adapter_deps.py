"""EXP-025, F05: o que o ``adapter_v2`` usa de fora, num só lugar (o produto troca só este módulo).

Tudo vem do EXP-023 e do EXP-024 sem alteração: o motor e as utilidades do Organizador, o diff de
revisão, o gating, a projeção e o estado por usuário.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPS = HERE.parents[1]
for path in (EXPS / "EXP-023" / "harness", HERE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
sys.path.append(str(EXPS / "EXP-024" / "harness"))

from adaptive_organizer import line_shape, normalized, softmax, top  # noqa: E402,F401
from diff_signal import align_units  # noqa: E402,F401
from organizer import Options, cosine  # noqa: E402,F401
from safety_gate import page_weights, project  # noqa: E402,F401
from state import BOOK_KEEP, USER_KEEP, add_vector, book_scope, new_state  # noqa: E402,F401
