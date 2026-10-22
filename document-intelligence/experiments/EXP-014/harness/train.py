"""Ajuste fino experimental do PP-OCRv6 small rec com linhas de TREINO do BRESSAY (EXP-014).

* Modelo: conversão PyTorch do ONNX (``model.py``), normalização em lote congelada.
* Perda: CTC sobre o log das probabilidades (o grafo termina em softmax).
* Lotes de linhas de largura parecida; margem à direita igual à da leitura (``--extra``).
* A cada ``--eval-every`` passos, CER no subconjunto de validação; guarda o melhor em
  ``models/exp-014/best.pt`` (fora do Git). Para pelo orçamento de tempo (``--minutes``).

Os pesos ajustados no BRESSAY são só para experimento (licença ``NEEDS VALIDATION``); nunca para
produto.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import cv2
import torch
from model import batch, decode, encode, freeze_batchnorm, load, preprocess

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "dataset" / "processed" / "exp-014"
OUT = ROOT / "models" / "exp-014"


def levenshtein(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def load_items(name: str) -> list[dict]:
    """Itens com a largura que a linha terá a 48 px (para agrupar larguras parecidas no lote)."""
    items = json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))
    for item in items:
        h, w = cv2.imread(str(ROOT / item["image"]), cv2.IMREAD_GRAYSCALE).shape[:2]
        item["width"] = 48 * w / h
    return items


def tensors(items: list[dict], extra: int) -> torch.Tensor:
    """Lê e pré-processa as linhas do lote na hora (não cabem todas na memória)."""
    images = [cv2.imread(str(ROOT / it["image"]), cv2.IMREAD_COLOR) for it in items]
    return batch([preprocess(image, extra) for image in images])


def evaluate(model, characters, items, extra, batch_size=16) -> float:
    model.eval()
    edits = total = 0
    order = sorted(range(len(items)), key=lambda i: items[i]["width"])
    with torch.no_grad():
        for start in range(0, len(order), batch_size):
            chunk = [items[i] for i in order[start : start + batch_size]]
            texts = decode(model(tensors(chunk, extra)), characters)
            for item, text in zip(chunk, texts, strict=True):
                edits += levenshtein(item["text"], text)
                total += len(item["text"])
    model.train()
    freeze_batchnorm(model)
    return edits / max(1, total)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ajuste fino (EXP-014)")
    parser.add_argument("--minutes", type=float, default=180)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--extra", type=int, default=640)
    parser.add_argument("--eval-every", type=int, default=300)
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    torch.set_num_threads(4)
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    model, characters = load()
    index = {c: i for i, c in enumerate(characters) if i > 0}
    train = load_items("train")
    val = load_items("val-sub")
    dropped = 0
    for item in train:
        item["target"], lost = encode(item["text"], index)
        dropped += lost
    train = [it for it in train if it["target"]]
    print(f"treino: {len(train)} linhas; caracteres fora do dicionário descartados: {dropped}")

    OUT.mkdir(parents=True, exist_ok=True)
    best = evaluate(model, characters, val, args.extra)
    print(f"passo 0: CER de validação {best:.4f} (sem ajuste)")
    torch.save(model.state_dict(), OUT / "best.pt")
    history = [{"step": 0, "val_cer": best}]

    model.train()
    freeze_batchnorm(model)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    ctc = torch.nn.CTCLoss(blank=0, zero_infinity=True)
    started = time.monotonic()
    step = 0
    epoch = 0
    while time.monotonic() - started < args.minutes * 60:
        epoch += 1
        order = sorted(range(len(train)), key=lambda i: train[i]["width"])
        batches = [order[i : i + args.batch] for i in range(0, len(order), args.batch)]
        random.shuffle(batches)
        for chunk_ids in batches:
            if time.monotonic() - started >= args.minutes * 60:
                break
            chunk = [train[i] for i in chunk_ids]
            images = tensors(chunk, args.extra)
            log_probs = torch.log(model(images).clamp_min(1e-8)).permute(1, 0, 2)
            targets = torch.tensor([t for it in chunk for t in it["target"]], dtype=torch.long)
            target_lengths = torch.tensor([len(it["target"]) for it in chunk], dtype=torch.long)
            input_lengths = torch.full((len(chunk),), log_probs.shape[0], dtype=torch.long)
            loss = ctc(log_probs, targets, input_lengths, target_lengths)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            step += 1
            if step % 50 == 0:
                minutes = (time.monotonic() - started) / 60
                print(f"época {epoch} passo {step}: perda {loss.item():.3f} ({minutes:.1f} min)")
            if step % args.eval_every == 0:
                cer = evaluate(model, characters, val, args.extra)
                history.append({"step": step, "epoch": epoch, "val_cer": cer})
                marker = ""
                if cer < best:
                    best = cer
                    torch.save(model.state_dict(), OUT / "best.pt")
                    marker = " (melhor)"
                print(f"passo {step}: CER de validação {cer:.4f}{marker}")
    cer = evaluate(model, characters, val, args.extra)
    history.append({"step": step, "epoch": epoch, "val_cer": cer})
    if cer < best:
        best = cer
        torch.save(model.state_dict(), OUT / "best.pt")
    summary = {"best_val_cer": best, "steps": step, "epochs_started": epoch, "args": vars(args),
               "history": history, "train_lines": len(train), "dropped_chars": dropped}  # fmt: skip
    (ROOT / "experiments" / "EXP-014" / "training.json").write_text(
        json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print("melhor CER de validação:", round(best, 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
