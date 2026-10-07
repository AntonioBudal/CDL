"""Produz o layout detectado das páginas do EXP-003 com a combinação do ADR-002.

Etapas (uma execução cada, com o supervisor e os limites do EXP-002):

1. retificação por contorno (OpenCV) → imagens retificadas e homografias;
2. Doc-UFCN ``norhand`` nas imagens retificadas → linhas, levadas de volta às coordenadas originais;
3. Doc-UFCN ``norhand`` nas imagens originais → linhas sem retificação (comparação da Fase 4);
4. Docling Heron nas imagens originais → blocos.

Reutiliza os ambientes ``uv`` e os pesos do EXP-002 (revisões e SHA-256 em
``experiments/EXP-002/candidates.json``, conferidos antes da carga). Saída fora do Git:
``dataset/processed/exp-003/detected-<conjunto>.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from rectify import map_points
from supervisor import Limits, run_candidate

from leitorum_di.procmem import available_system_memory_bytes

ROOT = Path(__file__).resolve().parents[3]
EXP002 = ROOT / "experiments" / "EXP-002"
OUT_DIR = ROOT / "dataset" / "processed" / "exp-003"


def _python(environment: str) -> str:
    scripts = "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    path = EXP002 / environment / ".venv" / scripts
    if not path.is_file():
        raise SystemExit(f"Ambiente não instalado: {path}")
    return str(path)


def _candidate(candidate_id: str) -> tuple[dict[str, Any], Path]:
    registry = json.loads((EXP002 / "candidates.json").read_text(encoding="utf-8"))
    candidate = next(c for c in registry["candidates"] if c["id"] == candidate_id)
    weights_dir = ROOT / candidate["weights"]["local_dir"]
    candidate["options"] = {"id": candidate_id, "weights_dir": str(weights_dir), "seed": 1234}
    return candidate, weights_dir


def _wait_for_memory(limits: Limits, timeout_s: float) -> None:
    started = time.monotonic()
    while time.monotonic() - started < timeout_s:
        free = available_system_memory_bytes()
        if free is None or free >= limits.min_free_system_bytes:
            return
        time.sleep(2.0)


def _run(candidate, manifest_path, python_exe, weights_dir, limits, wait_s) -> dict[str, Any]:
    _wait_for_memory(limits, wait_s)
    result = run_candidate(candidate, manifest_path, ROOT, python_exe=python_exe, limits=limits,
                           weights_dir=weights_dir)  # fmt: skip
    if result.status != "OK":
        tail = "\n".join(result.stderr_tail[-8:])
        raise SystemExit(f"{candidate['id']}: {result.status} — {result.reason}\n{tail}")
    times = [p["elapsed_ms"] for p in result.predictions]
    print(f"{candidate['id']}: OK, {len(times)} páginas, mediana {np.median(times):.0f} ms, "
          f"pico {(result.peak_rss_bytes or 0) / 2**20:.0f} MiB")  # fmt: skip
    return {
        "predictions": {p["id"]: p["result"] for p in result.predictions},
        "median_ms": float(np.median(times)),
        "peak_rss_bytes": result.peak_rss_bytes,
        "load_ms": result.load_ms,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Layout detectado para o EXP-003 (ADR-002)")
    parser.add_argument("--set", default="test", choices=["dev", "test"])
    parser.add_argument("--wait-free-s", type=float, default=600.0)
    args = parser.parse_args(argv)

    manifest_path = ROOT / "dataset" / "fixtures" / "exp-003" / f"{args.set}-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    limits = Limits()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rectified_dir = OUT_DIR / "rectified" / args.set
    rectifier = {
        "id": "rectify-contour",
        "kind": "reference",
        "adapter": "adapters.rectifiers:ContourRectifier",
        "options": {"id": "rectify-contour", "output_dir": str(rectified_dir)},
    }
    rect = _run(rectifier, manifest_path, sys.executable, None, limits, args.wait_free_s)
    rectified_pages = []
    homographies = {}
    for page in manifest["pages"]:
        info = rect["predictions"][page["id"]]["rectification"]
        image = Path(info["output"])
        homographies[page["id"]] = info["homography"]
        rectified_pages.append(
            {
                "id": page["id"],
                "image": image.relative_to(ROOT).as_posix(),
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                "level": page["level"],
            }
        )
    rectified_manifest = OUT_DIR / f"rectified-{args.set}-manifest.json"
    rectified_manifest.write_text(json.dumps({"pages": rectified_pages}), encoding="utf-8")

    lines_candidate, lines_weights = _candidate("docufcn-norhand-line")
    docufcn_python = _python("envs/docufcn")
    on_rectified = _run(lines_candidate, rectified_manifest, docufcn_python, lines_weights, limits,
                        args.wait_free_s)  # fmt: skip
    on_original = _run(lines_candidate, manifest_path, docufcn_python, lines_weights, limits,
                       args.wait_free_s)  # fmt: skip
    blocks_candidate, blocks_weights = _candidate("heron")
    heron = _run(blocks_candidate, manifest_path, _python("envs/heron"), blocks_weights, limits,
                 args.wait_free_s)  # fmt: skip

    pages = {}
    for page in manifest["pages"]:
        pid = page["id"]
        inverse = np.linalg.inv(np.array(homographies[pid]))
        mapped = []
        for line in on_rectified["predictions"][pid]["lines"]:
            x0, y0, x1, y1 = line["bbox"]
            polygon = line.get("polygon") or [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
            points = map_points(polygon, inverse)
            mapped.append(
                {
                    "bbox": [round(float(points[:, 0].min())), round(float(points[:, 1].min())),
                             round(float(points[:, 0].max())), round(float(points[:, 1].max()))],
                    "polygon": [[round(float(x)), round(float(y))] for x, y in points],
                    "score": line.get("score", 1.0),
                }
            )  # fmt: skip
        pages[pid] = {
            "blocks": heron["predictions"][pid]["blocks"],
            "lines": {"rectified": mapped, "original": on_original["predictions"][pid]["lines"]},
        }

    output = {
        "schema": "leitorum-di-detected-layout/1",
        "set": args.set,
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "pipeline": "contour → docufcn-norhand-line (linhas) + heron (blocos) — ADR-002",
        "stages": {
            "rectify-contour": {k: v for k, v in rect.items() if k != "predictions"},
            "docufcn-norhand-line (retificado)": {
                k: v for k, v in on_rectified.items() if k != "predictions"
            },
            "docufcn-norhand-line (original)": {
                k: v for k, v in on_original.items() if k != "predictions"
            },
            "heron": {k: v for k, v in heron.items() if k != "predictions"},
        },
        "pages": pages,
    }
    out = OUT_DIR / f"detected-{args.set}.json"
    out.write_text(json.dumps(output, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Layout detectado gravado em {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
