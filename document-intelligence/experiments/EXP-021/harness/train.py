"""Ajuste fino com degradações de foto (EXP-021): o treino do EXP-018, retomável, com aumento.

Roda no ambiente ``EXP-014/envs/ft``. Com todas as páginas (padrão), a ordem dos lotes é a mesma do
EXP-014; a única mudança é que cada linha é degradada com probabilidade ``--augment``
(``augment.degrade_line``), com gerador próprio semeado pelo passo, para não alterar essa ordem.

Pesos em ``models/exp-021/aug.pt`` (fora do Git; BRESSAY ``NEEDS VALIDATION``, só experimento);
registro em ``experiments/EXP-021/runs/aug.json``.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "experiments" / "EXP-018" / "harness"))
sys.path.insert(0, str(ROOT / "experiments" / "EXP-014" / "harness"))
from augment import degrade_line  # noqa: E402
from model import batch, encode, freeze_batchnorm, load, preprocess  # noqa: E402
from subset import page_of, pick_pages  # noqa: E402
from train import evaluate, load_items  # noqa: E402

OUT = ROOT / "models" / "exp-021"
RUNS = Path(__file__).resolve().parents[1] / "runs"


def augmented(items: list[dict], extra: int, p: float, rng: np.random.Generator) -> torch.Tensor:
    """Lê as linhas do lote, degrada cada uma com probabilidade ``p`` e pré-processa."""
    images = []
    for item in items:
        image = cv2.imread(str(ROOT / item["image"]), cv2.IMREAD_COLOR)
        if rng.uniform() < p:
            image = degrade_line(image, rng)
        images.append(preprocess(image, extra))
    return batch(images)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ajuste fino com degradações de foto (EXP-021)")
    parser.add_argument("--pages", type=int, default=10_000, help="padrão: todas")
    parser.add_argument("--augment", type=float, default=0.5)
    parser.add_argument("--steps", type=int, default=392)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--extra", type=int, default=640)
    parser.add_argument("--eval-every", type=int, default=98)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--val-limit", type=int, default=None, help="só para teste rápido")
    parser.add_argument("--stop-after", type=int, default=None, help="só para testar a retomada")
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
    history, step, epoch, epoch_start, skip, previous_minutes = [], 0, 0, 0, 0, 0.0
    checkpoint = OUT / "aug-retomada.pt"
    if checkpoint.exists():
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        model.load_state_dict(saved["model"])
        optimizer.load_state_dict(saved["optimizer"])
        torch.set_rng_state(saved["torch_rng"])
        random.setstate(saved["epoch_random"])
        history, step, epoch = saved["history"], saved["step"], saved["epoch"] - 1
        skip, previous_minutes = step - saved["epoch_start"], saved["minutes"]
        print(f"retomando no passo {step} (época {saved['epoch']})", flush=True)
    while step < args.steps:
        epoch += 1
        epoch_random, epoch_start = random.getstate(), step - skip
        order = sorted(range(len(train)), key=lambda i: train[i]["width"])
        batches = [order[i : i + args.batch] for i in range(0, len(order), args.batch)]
        random.shuffle(batches)
        for chunk_ids in batches[skip:]:
            if step >= args.steps:
                break
            chunk = [train[i] for i in chunk_ids]
            rng = np.random.default_rng([args.seed, step])
            probs = model(augmented(chunk, args.extra, args.augment, rng))
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
                state = {
                    "model": model.state_dict(),
                    "optimizer": optimizer.state_dict(),
                    "torch_rng": torch.get_rng_state(),
                    "epoch_random": epoch_random,
                    "epoch_start": epoch_start,
                    "epoch": epoch,
                    "step": step,
                    "history": history,
                    "minutes": previous_minutes + (time.monotonic() - started) / 60,
                }
                torch.save(state, checkpoint.with_suffix(".tmp"))
                checkpoint.with_suffix(".tmp").replace(checkpoint)
                if step == args.stop_after:
                    print(f"interrompido no passo {step} (teste de retomada)", flush=True)
                    return 3
        skip = 0
    OUT.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), OUT / "aug.pt")
    checkpoint.unlink(missing_ok=True)
    RUNS.mkdir(exist_ok=True)
    summary = {
        "pages": pages,
        "train_lines": len(train),
        "steps": step,
        "epochs_started": epoch,
        "lines_seen": step * args.batch,
        "final_val_cer": history[-1]["val_cer"],
        "minutes": round(previous_minutes + (time.monotonic() - started) / 60, 1),
        "resumed": previous_minutes > 0,
        "args": vars(args),
        "history": history,
    }
    (RUNS / "aug.json").write_text(
        json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print("CER de validação no último passo:", round(summary["final_val_cer"], 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
