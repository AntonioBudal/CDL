"""EXP-031P — ajuste fino do PP-OCRv6 small com a lista de uma condição, pela receita do EXP-014/018
(392 passos de 16 linhas, taxa 5e-5, margem 640, normalização em lote congelada). Roda no
ambiente do EXP-014 (``envs/ft``), importando o ``model.py`` dele sem alterá-lo.

Retomável: grava modelo, otimizador e passo a cada ``--ckpt-every`` passos; a ordem dos lotes de
cada época vem da semente, então a retomada pula exatamente o que já foi feito. Espera memória
livre antes de começar e pausa (gravando) se a memória apertar.

Uso: ``python train.py --cond C1``
"""

from __future__ import annotations

import argparse
import ctypes
import json
import random
import sys
import time
from pathlib import Path

EXP014 = Path("C:/Users/User/caderno/document-intelligence/experiments/EXP-014/harness")
sys.path.insert(0, str(EXP014))

import cv2  # noqa: E402
import torch  # noqa: E402
from model import batch, encode, freeze_batchnorm, load, preprocess  # noqa: E402

WORK = Path("D:/Leitorum-DI/trabalho/exp-031p")
MODELS = Path("D:/Leitorum-DI/modelos/exp-031p")
MIN_FREE_START = 1.5e9
MIN_FREE_RUN = 0.6e9


class _Mem(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong)] + [
        (name, ctypes.c_ulonglong)
        for name in ("total", "avail", "pf_total", "pf_avail", "v_total", "v_avail", "ext")
    ]


def free_ram() -> float:
    mem = _Mem()
    mem.dwLength = ctypes.sizeof(_Mem)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    return float(mem.avail)


def wait_ram(minimum: float) -> None:
    waited = False
    while free_ram() < minimum:
        if not waited:
            print(f"esperando memória livre (≥ {minimum / 1e9:.1f} GB)…", flush=True)
            waited = True
        time.sleep(60)


def tensors(items, extra):
    return batch([preprocess(cv2.imread(it["image"], cv2.IMREAD_COLOR), extra) for it in items])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cond", required=True)
    parser.add_argument("--steps", type=int, default=392)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--extra", type=int, default=640)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--ckpt-every", type=int, default=50)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    torch.set_num_threads(4)
    MODELS.mkdir(parents=True, exist_ok=True)
    final = MODELS / f"{args.cond}.pt"
    if final.is_file():
        print(f"{args.cond}: já treinado ({final})")
        return 0
    wait_ram(MIN_FREE_START)

    model, characters = load()
    index = {c: i for i, c in enumerate(characters) if i > 0}
    items = json.loads((WORK / "listas" / f"{args.cond}.json").read_text(encoding="utf-8"))
    kept, dropped = [], 0
    for item in items:
        target, lost = encode(item["text"], index)
        if lost or not target:
            dropped += 1
            continue
        image = cv2.imread(item["image"], cv2.IMREAD_GRAYSCALE)
        if image is None:
            dropped += 1
            continue
        h, w = image.shape[:2]
        kept.append({**item, "target": target, "width": 48 * w / max(1, h)})
    print(f"{args.cond}: {len(kept)} linhas ({dropped} descartadas)", flush=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    ckpt_path = MODELS / f"{args.cond}.ckpt"
    step = 0
    log = []
    if ckpt_path.is_file():
        state = torch.load(ckpt_path, weights_only=False)
        model.load_state_dict(state["model"])
        optimizer.load_state_dict(state["optimizer"])
        step, log = state["step"], state["log"]
        print(f"retomando do passo {step}", flush=True)
    model.train()
    freeze_batchnorm(model)
    ctc = torch.nn.CTCLoss(blank=0, zero_infinity=True)
    order = sorted(range(len(kept)), key=lambda i: kept[i]["width"])
    base_batches = [order[i : i + args.batch] for i in range(0, len(order), args.batch)]
    started = time.monotonic()
    done = 0  # passos já contados nas épocas anteriores
    epoch = 0
    while step < args.steps:
        epoch += 1
        batches = list(base_batches)
        random.Random(f"{args.seed}-{epoch}").shuffle(batches)
        for position, chunk_ids in enumerate(batches):
            global_step = done + position
            if global_step < step:
                continue  # já feito antes da retomada
            if step >= args.steps:
                break
            if step % 10 == 0 and free_ram() < MIN_FREE_RUN:
                torch.save(
                    {
                        "model": model.state_dict(),
                        "optimizer": optimizer.state_dict(),
                        "step": step,
                        "log": log,
                    },
                    ckpt_path,
                )
                wait_ram(MIN_FREE_START)
            torch.manual_seed(args.seed + step)
            chunk = [kept[i] for i in chunk_ids]
            log_probs = torch.log(model(tensors(chunk, args.extra)).clamp_min(1e-8)).permute(
                1, 0, 2
            )
            targets = torch.tensor([t for it in chunk for t in it["target"]], dtype=torch.long)
            target_lengths = torch.tensor([len(it["target"]) for it in chunk], dtype=torch.long)
            input_lengths = torch.full((len(chunk),), log_probs.shape[0], dtype=torch.long)
            loss = ctc(log_probs, targets, input_lengths, target_lengths)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            step += 1
            if step % 25 == 0:
                minutes = (time.monotonic() - started) / 60
                log.append({"step": step, "epoch": epoch, "loss": round(loss.item(), 4)})
                print(
                    f"{args.cond} passo {step}/{args.steps}: perda {loss.item():.3f} "
                    f"({minutes:.1f} min)",
                    flush=True,
                )
            if step % args.ckpt_every == 0:
                torch.save(
                    {
                        "model": model.state_dict(),
                        "optimizer": optimizer.state_dict(),
                        "step": step,
                        "log": log,
                    },
                    ckpt_path,
                )
        done += len(batches)
    torch.save(model.state_dict(), final)
    (MODELS / f"{args.cond}.json").write_text(
        json.dumps(
            {
                "cond": args.cond,
                "steps": step,
                "lines": len(kept),
                "dropped": dropped,
                "args": vars(args),
                "log": log,
            },
            indent=1,
        ),
        "utf-8",
    )
    if ckpt_path.is_file():
        ckpt_path.unlink()
    print(f"{args.cond}: pronto", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
