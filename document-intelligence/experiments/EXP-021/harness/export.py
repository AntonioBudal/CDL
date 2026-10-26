"""EXP-021, T002: exporta o leitor treinado com degradações para ONNX e confere a paridade.

Igual à exportação do EXP-017, com outra entrada e saída: ``models/exp-021/aug.pt`` →
``models/exp-021/rec-aug-bressay.onnx`` (fora do Git; BRESSAY ``NEEDS VALIDATION``, só experimento).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import torch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "EXP-014" / "harness"))
from model import ONNX_MODEL, load  # noqa: E402

CHECKPOINT = ROOT / "models" / "exp-021" / "aug.pt"
OUT = ROOT / "models" / "exp-021" / "rec-aug-bressay.onnx"
WIDTHS = (320, 640, 960, 1280, 1600, 2240)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    model, _ = load()
    model.load_state_dict(torch.load(CHECKPOINT, map_location="cpu"))
    model.eval()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dummy = torch.zeros(1, 3, 48, 640)
    torch.onnx.export(
        model,
        (dummy,),
        str(OUT),
        input_names=["x"],
        output_names=["probs"],
        dynamic_axes={"x": {0: "batch", 3: "width"}, "probs": {0: "batch", 1: "steps"}},
        opset_version=17,
        dynamo=False,
    )
    graph = onnx.load(str(OUT))
    original = {p.key: p.value for p in onnx.load(str(ONNX_MODEL)).metadata_props}
    entry = graph.metadata_props.add()
    entry.key, entry.value = "character", original["character"]
    onnx.save(graph, str(OUT))

    session = ort.InferenceSession(str(OUT), providers=["CPUExecutionProvider"])
    rng = np.random.default_rng(17)
    gaps = {}
    for width in WIDTHS:
        x = rng.uniform(-1, 1, (2, 3, 48, width)).astype(np.float32)
        x[:, :, :, width // 2 :] = 0  # metade com margem vazia, como na leitura
        with torch.no_grad():
            expected = model(torch.from_numpy(x)).numpy()
        got = session.run(None, {"x": x})[0]
        gaps[width] = float(np.abs(expected - got).max())
    report = {
        "checkpoint_sha256": hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest(),
        "onnx_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "onnx_bytes": OUT.stat().st_size,
        "torch": torch.__version__,
        "onnxruntime": ort.__version__,
        "max_abs_diff_by_width": gaps,
        "parity_ok": max(gaps.values()) <= 1e-4,
    }
    (Path(__file__).resolve().parents[1] / "export.json").write_text(
        json.dumps(report, indent=1) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
