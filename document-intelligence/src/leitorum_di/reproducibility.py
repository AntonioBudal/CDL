"""Congelamento de sementes aleatórias e registro de ambiente para reprodutibilidade."""

from __future__ import annotations

import os
import platform
import random
import sys

DEFAULT_SEED = 1234


def freeze_seeds(seed: int = DEFAULT_SEED) -> dict[str, object]:
    """Fixa as sementes das fontes de aleatoriedade disponíveis e devolve um registro.

    Só semeia numpy/torch se já tiverem sido importados (nunca os importa: evita
    dependência pesada). ``PYTHONHASHSEED`` só tem efeito se definido antes do início do
    interpretador; aqui é apenas relatado.
    """
    random.seed(seed)
    seeded = ["random"]

    numpy = sys.modules.get("numpy")
    if numpy is not None:
        numpy.random.seed(seed)
        seeded.append("numpy")

    torch = sys.modules.get("torch")
    if torch is not None:
        torch.manual_seed(seed)
        seeded.append("torch")
        if getattr(torch, "cuda", None) is not None and torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            seeded.append("torch.cuda")

    return {
        "seed": seed,
        "seeded": seeded,
        "pythonhashseed_effective": os.environ.get("PYTHONHASHSEED") == str(seed),
    }


def environment_snapshot() -> dict[str, object]:
    """Registro mínimo e local do ambiente de execução (sem rede)."""
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
    }
