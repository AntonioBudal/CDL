"""Fase 1 do EXP-014: o reconhecedor PP-OCRv6 small pode ser ajustado em PyTorch nesta máquina?

1. Lê o modelo ONNX embutido no ``rapidocr`` (SHA-256 conferido) e o dicionário de caracteres dos
   metadados.
2. Converte para PyTorch com ``onnx2torch`` e compara a saída com o ONNX Runtime em imagens
   fictícias.
3. Cronometra ida e volta (forward + backward, perda CTC) em lotes de 16 linhas de 48×320.
4. Estima o tempo por época para um número dado de linhas de treino.

Só imagens fictícias (ruído e traços sintéticos). Roda em ``experiments/EXP-014/envs/ft``.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import torch
from onnx2torch import convert
from onnx_fix import fix

ROOT = Path(__file__).resolve().parents[3]
MODEL = (
    ROOT / "experiments" / "EXP-008" / "envs" / "ppocr" / ".venv" / "Lib" / "site-packages"
    / "rapidocr" / "models" / "PP-OCRv6_rec_small.onnx"
)  # fmt: skip
SHA256 = "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884"
TRAIN_LINES = 19_000


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if hashlib.sha256(MODEL.read_bytes()).hexdigest() != SHA256:
        raise SystemExit("SHA-256 do modelo não confere")
    graph = onnx.load(str(MODEL))
    meta = {p.key: p.value for p in graph.metadata_props}
    characters = meta.get("character", "").splitlines()
    last = graph.graph.node[-1]
    print("metadados:", sorted(meta), "| caracteres no dicionário:", len(characters))
    print("última operação:", last.op_type, "| entradas:", [i.name for i in graph.graph.input])
    accents = sum(1 for c in characters if c in "áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ")
    print("letras acentuadas do português no dicionário:", accents, "de 24")

    graph, fixed = fix(graph)
    print("convoluções com SAME_UPPER reescritas:", fixed)
    model = convert(graph).eval()
    session = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])  # original
    rng = np.random.default_rng(1234)
    batch = rng.random((4, 3, 48, 320), dtype=np.float32) * 2 - 1
    reference = session.run(None, {session.get_inputs()[0].name: batch})[0]
    with torch.no_grad():
        ours = model(torch.from_numpy(batch)).numpy()
    print(
        "saída:",
        reference.shape,
        "| maior diferença absoluta:",
        float(np.abs(reference - ours).max()),
    )

    model.train()
    for parameter in model.parameters():
        parameter.requires_grad_(True)
    parameters = sum(p.numel() for p in model.parameters())
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
    ctc = torch.nn.CTCLoss(blank=0, zero_infinity=True)
    torch.set_num_threads(max(1, torch.get_num_threads()))
    timings = []
    for step in range(4):
        images = torch.from_numpy(rng.random((16, 3, 48, 320), dtype=np.float32) * 2 - 1)
        targets = torch.randint(1, len(characters) + 1, (16, 20))
        started = time.perf_counter()
        probabilities = model(images)  # (N, T, C), já com softmax
        log_probs = torch.log(probabilities.clamp_min(1e-8)).permute(1, 0, 2)
        lengths = torch.full((16,), log_probs.shape[0], dtype=torch.long)
        loss = ctc(log_probs, targets, lengths, torch.full((16,), 20, dtype=torch.long))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        timings.append(time.perf_counter() - started)
        print(f"passo {step}: perda {loss.item():.3f}, {timings[-1]:.2f} s")
    per_batch = float(np.median(timings[1:]))
    epoch_min = per_batch * TRAIN_LINES / 16 / 60
    result = {
        "parameters": parameters,
        "characters": len(characters),
        "portuguese_accents_in_dictionary": accents,
        "max_abs_difference": float(np.abs(reference - ours).max()),
        "seconds_per_batch_16": per_batch,
        "estimated_minutes_per_epoch": epoch_min,
        "train_lines_assumed": TRAIN_LINES,
        "threads": torch.get_num_threads(),
    }
    print(json.dumps(result, ensure_ascii=False))
    out = ROOT / "dataset" / "processed" / "exp-014"
    out.mkdir(parents=True, exist_ok=True)
    (out / "feasibility.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
