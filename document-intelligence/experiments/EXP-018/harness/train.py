"""Curva de aprendizado do ajuste fino (EXP-018): treino do EXP-014 com N páginas e passos fixos.

Roda no ambiente ``EXP-014/envs/ft``. Reaproveita leitura, pré-processamento e avaliação do
``EXP-014/harness/train.py``; muda só o conjunto de treino (``--pages``, páginas inteiras sorteadas)
e o orçamento (``--steps``). O CER de validação principal é o do **último passo**.

Pesos em ``models/exp-018/p<N>.pt`` (fora do Git; BRESSAY ``NEEDS VALIDATION``, só experimento);
registro em ``experiments/EXP-018/runs/p<N>.json``.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "experiments" / "EXP-014" / "harness"))
from model import encode, freeze_batchnorm, load  # noqa: E402
from subset import page_of, pick_pages  # noqa: E402
from train import evaluate, load_items, tensors  # noqa: E402

OUT = ROOT / "models" / "exp-018"
RUNS = Path(__file__).resolve().parents[1] / "runs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Curva de aprendizado (EXP-018)")
    parser.add_argument("--pages", type=int, required=True)
    parser.add_argument("--steps", type=int, default=392)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--extra", type=int, default=640)
    parser.add_argument("--eval-every", type=int, default=98)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--val-limit", type=int, default=None, help="só para teste rápido")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    torch.set_num_threads(4)
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    model, characters = load()
    index = {c: i for i, c in enumerate(characters) if i > 0}
    train = pick_pages(load_items("train"), args.pages, args.seed)
    val = load_items("val-sub")[: args.val_limit]
    for item in train:
        item["target"], _ = encode(item["text"], index)
    train = [it for it in train if it["target"]]
    pages = len({page_of(it["id"]) for it in train})
    print(f"treino: {pages} páginas, {len(train)} linhas", flush=True)

    model.train()
    freeze_batchnorm(model)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    ctc = torch.nn.CTCLoss(blank=0, zero_infinity=True)
    started = time.monotonic()
    history, step, epoch = [], 0, 0
    while step < args.steps:
        epoch += 1
        order = sorted(range(len(train)), key=lambda i: train[i]["width"])
        batches = [order[i : i + args.batch] for i in range(0, len(order), args.batch)]
        random.shuffle(batches)
        for chunk_ids in batches:
            if step >= args.steps:
                break
            chunk = [train[i] for i in chunk_ids]
            probs = model(tensors(chunk, args.extra))
            log_probs = torch.log(probs.clamp_min(1e-8)).permute(1, 0, 2)
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
                print(f"época {epoch} passo {step}: perda {loss.item():.3f} ({minutes:.1f} min)",
                      flush=True)  # fmt: skip
            if step % args.eval_every == 0 or step == args.steps:
                cer = evaluate(model, characters, val, args.extra)
                history.append({"step": step, "epoch": epoch, "val_cer": cer})
                print(f"passo {step}: CER de validação {cer:.4f}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), OUT / f"p{args.pages}.pt")
    RUNS.mkdir(exist_ok=True)
    summary = {
        "pages": pages,
        "train_lines": len(train),
        "steps": step,
        "epochs_started": epoch,
        "lines_seen": step * args.batch,
        "final_val_cer": history[-1]["val_cer"],
        "minutes": round((time.monotonic() - started) / 60, 1),
        "args": vars(args),
        "history": history,
    }
    (RUNS / f"p{args.pages}.json").write_text(
        json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print("CER de validação no último passo:", round(summary["final_val_cer"], 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
