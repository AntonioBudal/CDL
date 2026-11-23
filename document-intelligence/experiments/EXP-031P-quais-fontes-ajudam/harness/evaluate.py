"""EXP-031P — mede C0 (leitor sem ajuste) e C1–C5 nos conjuntos de medida: CER, WER e erro nas
letras acentuadas, com a mesma leitura para todos (PyTorch, lotes de larguras parecidas, margem
640). Ambiente do EXP-014. Só números na saída.

Uso: ``python evaluate.py [--conds C0,C1,...]``
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

EXP014 = Path("C:/Users/User/caderno/document-intelligence/experiments/EXP-014/harness")
sys.path.insert(0, str(EXP014))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cv2  # noqa: E402
import torch  # noqa: E402
from model import decode, freeze_batchnorm, load  # noqa: E402
from train import tensors, wait_ram  # noqa: E402

WORK = Path("D:/Leitorum-DI/trabalho/exp-031p")
MODELS = Path("D:/Leitorum-DI/modelos/exp-031p")
ACCENTED = set("áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ")


def norm(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def align(ref: str, hyp: str) -> tuple[int, int]:
    """Distância de edição e quantos caracteres acentuados da referência saíram errados."""
    n, m = len(ref), len(hyp)
    d = [list(range(m + 1))] + [[i] + [0] * m for i in range(1, n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(
                d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1])
            )
    wrong_accents = 0
    i, j = n, m
    while i > 0 and j > 0:
        if d[i][j] == d[i - 1][j - 1] + (ref[i - 1] != hyp[j - 1]):
            if ref[i - 1] in ACCENTED and ref[i - 1] != hyp[j - 1]:
                wrong_accents += 1
            i, j = i - 1, j - 1
        elif d[i][j] == d[i - 1][j] + 1:
            wrong_accents += ref[i - 1] in ACCENTED
            i -= 1
        else:
            j -= 1
    wrong_accents += sum(1 for c in ref[:i] if c in ACCENTED)
    return d[n][m], wrong_accents


def word_distance(ref: list[str], hyp: list[str]) -> int:
    previous = list(range(len(hyp) + 1))
    for i, a in enumerate(ref, 1):
        current = [i]
        for j, b in enumerate(hyp, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def measure(model, characters, items) -> dict:
    model.eval()
    for item in items:
        h, w = cv2.imread(item["image"], cv2.IMREAD_GRAYSCALE).shape[:2]
        item["width"] = 48 * w / max(1, h)
    order = sorted(range(len(items)), key=lambda i: items[i]["width"])
    chars = edits = words = word_edits = accents = wrong_accents = 0
    with torch.no_grad():
        for start in range(0, len(order), 16):
            chunk = [items[i] for i in order[start : start + 16]]
            for item, text in zip(
                chunk, decode(model(tensors(chunk, 640)), characters), strict=True
            ):
                ref, hyp = norm(item["text"]), norm(text)
                distance, bad = align(ref, hyp)
                chars += len(ref)
                edits += distance
                accents += sum(1 for c in ref if c in ACCENTED)
                wrong_accents += bad
                words += len(ref.split())
                word_edits += word_distance(ref.split(), hyp.split())
    return {
        "lines": len(items),
        "cer": round(edits / max(1, chars), 4),
        "wer": round(word_edits / max(1, words), 4),
        "accent_error": round(wrong_accents / accents, 4) if accents else None,
        "accented_chars": accents,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--conds", default="C0,C1,C2,C3,C4,C5")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    torch.set_num_threads(4)
    sets = {
        name: json.loads((WORK / "medida" / f"{name}.json").read_text(encoding="utf-8"))
        for name in ("bressay", "gnhk", "autor")
    }
    out_path = WORK / "resultados.json"
    results = json.loads(out_path.read_text(encoding="utf-8")) if out_path.is_file() else {}
    for cond in args.conds.split(","):
        if cond in results:
            continue
        wait_ram(1.5e9)
        model, characters = load()
        if cond != "C0":
            weights = MODELS / f"{cond}.pt"
            if not weights.is_file():
                print(f"{cond}: modelo ainda não treinado")
                continue
            model.load_state_dict(torch.load(weights, weights_only=True))
        freeze_batchnorm(model)
        results[cond] = {name: measure(model, characters, items) for name, items in sets.items()}
        out_path.write_text(json.dumps(results, indent=1), "utf-8")
        print(cond, json.dumps(results[cond]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
