"""EXP-043 — dificuldade de cada fonte para o leitor atual do produto: lê até ``--per-source``
linhas amostradas (as mesmas peças do motor: ``prepare_line`` e a leitura direta pelo ONNX com
margem) e calcula o CER contra a transcrição da fonte (NFC, espaços colapsados). Não diz se a
fonte ajuda a treinar; diz o quanto o leitor de hoje está longe dela. Roda no ambiente do motor.

Uso: ``python reader_cer.py [--per-source 100]``
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import unicodedata
from pathlib import Path

import common

MOTOR_DIR = Path(
    os.environ.get("EXP043_MOTOR_DIR") or "C:/Users/User/caderno/caderno-leitura-0.1/motor"
)


def norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def levenshtein(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def main(argv: list[str] | None = None) -> int:
    import numpy as np
    from PIL import Image

    parser = argparse.ArgumentParser()
    parser.add_argument("--per-source", type=int, default=100)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(MOTOR_DIR))
    from leitorum_motor import pipeline as motor

    reader = motor.PagePipeline(motor.load_config(MOTOR_DIR / "config.json"))
    rng = random.Random("exp-043-cer")
    results = {}
    for manifest in sorted(common.ROOT.glob("*/manifesto.jsonl")):
        source = manifest.parent.name
        rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
        rows = [r for r in rows if r.get("usable") and r.get("text")]
        picked = rng.sample(rows, min(args.per_source, len(rows)))
        distance = chars = 0
        per_line = []
        for row in picked:
            path = manifest.parent / "arquivos" / row["file"]
            with Image.open(path) as image:
                crop = np.asarray(image.convert("RGB"))[
                    :, :, ::-1
                ].copy()  # BGR, como o OpenCV do motor
            text, _ = reader._read(motor.prepare_line(crop))
            ref = norm(row["text"])
            d = levenshtein(ref, norm(text))
            distance += d
            chars += len(ref)
            per_line.append(d / max(1, len(ref)))
        per_line.sort()
        results[source] = {
            "lines": len(picked),
            "cer_micro": round(distance / chars, 4) if chars else None,
            "cer_median": round(per_line[len(per_line) // 2], 4) if per_line else None,
        }
        print(source, results[source], flush=True)
    (common.ROOT / "resumo-cer-leitor.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), "utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
