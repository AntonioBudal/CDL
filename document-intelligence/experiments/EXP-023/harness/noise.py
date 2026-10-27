"""EXP-023: modelo de erro de leitura por caractere, tirado das leituras do EXP-015 (só
estatísticas).

``build``: alinha a leitura bruta do leitor original (pipeline do ADR-008, sem correção lexical)
com a referência de cada página do BRESSAY e conta substituições, apagamentos e inserções por
caractere. Grava ``dataset/processed/exp-023/noise-model.json`` (fora do Git; nenhum texto, só
contagens).

``corrupt``: aplica o modelo a um texto com rótulos por caractere, escalando as taxas para um
CER-alvo. As quebras de linha nunca são alteradas (o leitor não junta nem separa linhas).
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP015 = ROOT / "dataset" / "processed" / "exp-015"
OUT = ROOT / "dataset" / "processed" / "exp-023" / "noise-model.json"


def reading_order(lines: list[dict]) -> list[int]:
    """Cópia de ``EXP-019/harness/crop.py``: de cima para baixo, faixa da esquerda à direita."""
    if not lines:
        return []
    heights = sorted(max(1, ln["bbox"][3] - ln["bbox"][1]) for ln in lines)
    tolerance = heights[len(heights) // 2] / 2
    centers = [((ln["bbox"][1] + ln["bbox"][3]) / 2, ln["bbox"][0]) for ln in lines]
    order = sorted(range(len(lines)), key=lambda i: centers[i][0])
    rows: list[list[int]] = []
    for index in order:
        if rows and abs(centers[index][0] - centers[rows[-1][0]][0]) <= tolerance:
            rows[-1].append(index)
        else:
            rows.append([index])
    return [i for row in rows for i in sorted(row, key=lambda k: centers[k][1])]


def build() -> dict:
    from rapidfuzz.distance import Levenshtein

    refs = json.loads((EXP015 / "test-bressay-refs.json").read_text(encoding="utf-8"))["refs"]
    read = json.loads((EXP015 / "read-test-bressay-t80.json").read_text(encoding="utf-8"))["items"]
    occurrences: Counter = Counter()
    deletions: Counter = Counter()
    substitutions: dict[str, Counter] = defaultdict(Counter)
    insertions: Counter = Counter()
    total = errors = 0
    for pid, lines in read.items():
        ref = " ".join(refs[pid].split())
        hyp = " ".join(" ".join(lines[i]["text"] for i in reading_order(lines)).split())
        occurrences.update(ref)
        total += len(ref)
        for op in Levenshtein.editops(ref, hyp):
            errors += 1
            if op.tag == "delete":
                deletions[ref[op.src_pos]] += 1
            elif op.tag == "replace":
                substitutions[ref[op.src_pos]][hyp[op.dest_pos]] += 1
            else:
                insertions[hyp[op.dest_pos]] += 1
    model = {
        "source": "EXP-015, leitor original, 185 páginas de teste do BRESSAY (só contagens)",
        "characters": total,
        "cer": errors / total,
        "p_delete": {c: deletions[c] / n for c, n in occurrences.items() if deletions[c]},
        "p_substitute": {
            c: sum(subs.values()) / occurrences[c]
            for c, subs in substitutions.items()
            if occurrences[c]
        },
        "substitute_to": {c: dict(subs.most_common(12)) for c, subs in substitutions.items()},
        "p_insert": sum(insertions.values()) / total,
        "insert_chars": dict(insertions.most_common(30)),
    }
    return model


def corrupt(
    text: str, labels: list, model: dict, target_cer: float, rng: random.Random
) -> tuple[str, list]:
    """Aplica erros de leitura com CER esperado ~``target_cer``; devolve texto e rótulos."""
    if target_cer <= 0:
        return text, list(labels)
    scale = target_cer / model["cer"]
    insert_pool = list(model["insert_chars"].items())
    ins_chars, ins_weights = [c for c, _ in insert_pool], [w for _, w in insert_pool]
    out_text, out_labels = [], []
    for ch, lab in zip(text, labels, strict=False):
        if ch == "\n":
            out_text.append(ch)
            out_labels.append(lab)
            continue
        r = rng.random()
        p_del = min(0.9, model["p_delete"].get(ch, 0.0) * scale)
        p_sub = min(0.9 - p_del, model["p_substitute"].get(ch, 0.0) * scale)
        if r < p_del:
            pass
        elif r < p_del + p_sub and model["substitute_to"].get(ch):
            targets = model["substitute_to"][ch]
            out_text.append(rng.choices(list(targets), weights=list(targets.values()))[0])
            out_labels.append(lab)
        else:
            out_text.append(ch)
            out_labels.append(lab)
        if rng.random() < min(0.5, model["p_insert"] * scale):
            out_text.append(rng.choices(ins_chars, weights=ins_weights)[0])
            out_labels.append(lab)
    return "".join(out_text), out_labels


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    model = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")
    print(f"modelo de ruído: {model['characters']} caracteres, CER medido {model['cer']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
