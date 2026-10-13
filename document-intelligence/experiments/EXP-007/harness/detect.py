"""Roda o pipeline dos ADR-002 e ADR-003 sobre um conjunto do EXP-007 e grava o layout detectado.

Conjuntos: ``gnhk`` (fotos de celular), ``bressay-x3`` e ``bressay-native`` (páginas de redação).

Etapas, uma execução cada, com o supervisor e os limites dos experimentos anteriores:

1. só no ``gnhk``: retificação por contorno e Doc-UFCN ``norhand`` nas imagens retificadas, com as
   linhas levadas de volta às coordenadas da foto;
2. Doc-UFCN ``norhand`` nas imagens originais;
3. Docling Heron nas imagens originais.

Pesos, parâmetros e ambientes são os do EXP-002 (``candidates.json`` deste experimento repete as
entradas e os SHA-256, conferidos antes da carga). Nada é ajustado nestes dados. ``--fake`` troca os
modelos pelo detector de referência (devolve a verdade de chão), para ensaiar o fluxo sem modelos.

Saída, fora do Git: ``dataset/processed/exp-007/detected-<conjunto>.json``.
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
EXPERIMENT = Path(__file__).resolve().parents[1]
EXP002 = ROOT / "experiments" / "EXP-002"
OUT_DIR = ROOT / "dataset" / "processed" / "exp-007"
SETS = ("gnhk", "bressay-x3", "bressay-native")
REFERENCE = {"kind": "reference", "adapter": "adapters.reference:ReferenceDetector"}


def _python(environment: str) -> str:
    scripts = "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    path = EXP002 / environment / ".venv" / scripts
    if not path.is_file():
        raise SystemExit(f"Ambiente não instalado: {path}")
    return str(path)


def _candidate(candidate_id: str) -> tuple[dict[str, Any], Path]:
    registry = json.loads((EXPERIMENT / "candidates.json").read_text(encoding="utf-8"))
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


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[max(1, int(np.ceil(fraction * len(ordered)))) - 1]


def _run(name, candidate, manifest_path, python_exe, weights_dir, limits, wait_s) -> dict[str, Any]:
    _wait_for_memory(limits, wait_s)
    result = run_candidate(
        candidate,
        manifest_path,
        ROOT,
        python_exe=python_exe,
        limits=limits,
        weights_dir=weights_dir,
    )
    if result.status != "OK":
        tail = "\n".join(result.stderr_tail[-8:])
        raise SystemExit(f"{name}: {result.status} — {result.reason}\n{tail}")
    times = [p["elapsed_ms"] for p in result.predictions]
    failed = [p["id"] for p in result.predictions if "error" in p["result"]]
    print(
        f"{name}: OK, {len(times)} páginas ({len(failed)} com falha), "
        f"mediana {np.median(times):.0f} ms, p95 {_percentile(times, 0.95):.0f} ms, "
        f"pico {(result.peak_rss_bytes or 0) / 2**20:.0f} MiB, {result.wall_s:.0f} s"
    )
    return {
        "predictions": {p["id"]: p["result"] for p in result.predictions},
        "elapsed_ms": {p["id"]: p["elapsed_ms"] for p in result.predictions},
        "summary": {
            "pages": len(times),
            "failed_pages": failed,
            "median_ms": float(np.median(times)),
            "p95_ms": float(_percentile(times, 0.95)),
            "max_ms": float(max(times)),
            "peak_rss_bytes": result.peak_rss_bytes,
            "load_ms": result.load_ms,
            "wall_s": result.wall_s,
            "describe": result.describe,
        },
    }


def _back_to_photo(lines: list[dict], homography) -> list[dict]:
    """Leva linhas detectadas na imagem retificada para as coordenadas da foto original."""
    inverse = np.linalg.inv(np.array(homography, dtype=np.float64))
    mapped = []
    for line in lines:
        x0, y0, x1, y1 = line["bbox"]
        polygon = line.get("polygon") or [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
        points = map_points(polygon, inverse)
        mapped.append(
            {
                "bbox": [
                    round(float(points[:, 0].min())),
                    round(float(points[:, 1].min())),
                    round(float(points[:, 0].max())),
                    round(float(points[:, 1].max())),
                ],
                "polygon": [[round(float(x)), round(float(y))] for x, y in points],
                "score": line.get("score", 1.0),
            }
        )
    return mapped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Layout detectado para o EXP-007")
    parser.add_argument("--set", required=True, choices=SETS)
    parser.add_argument("--fake", action="store_true", help="ensaio sem modelos")
    parser.add_argument("--wait-free-s", type=float, default=900.0)
    parser.add_argument("--min-free-mib", type=int, default=1024)
    parser.add_argument("--wall-timeout-s", type=float, default=1800.0)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    manifest_path = OUT_DIR / f"{args.set}-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    limits = Limits(
        min_free_system_bytes=args.min_free_mib * 1024 * 1024, wall_timeout_s=args.wall_timeout_s
    )
    wait = args.wait_free_s

    def model(candidate_id: str, environment: str):
        if args.fake:
            fake = {**REFERENCE, "id": f"fake-{candidate_id}", "options": {"id": candidate_id}}
            return fake, sys.executable, None
        candidate, weights = _candidate(candidate_id)
        return candidate, _python(environment), weights

    stages: dict[str, Any] = {}
    rectification: dict[str, dict] = {}
    on_rectified = None
    if args.set == "gnhk":
        rectified_dir = OUT_DIR / "rectified" / args.set
        rectifier = {
            "id": "rectify-contour",
            "kind": "reference",
            "adapter": "adapters.rectifiers:ContourRectifier",
            "options": {"id": "rectify-contour", "output_dir": str(rectified_dir)},
        }
        rect = _run("rectify-contour", rectifier, manifest_path, sys.executable, None, limits, wait)
        stages["rectify-contour"] = rect["summary"]
        rectified_pages = []
        for page in manifest["pages"]:
            info = rect["predictions"][page["id"]].get("rectification")
            if info is None:  # a retificação falhou nesta foto: segue sem retificar
                rectification[page["id"]] = {"found": False, "failed": True}
                continue
            rectification[page["id"]] = {
                "found": info["found"],
                "quad": info["quad"],
                "size": info["size"],
                "homography": info["homography"],
            }
            image = Path(info["output"])
            rectified_pages.append(
                {
                    "id": page["id"],
                    "image": image.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                    "level": page["level"],
                    "lines": [],
                    "blocks": [],
                }
            )
        rectified_manifest = OUT_DIR / f"rectified-{args.set}-manifest.json"
        rectified_manifest.write_text(json.dumps({"pages": rectified_pages}), encoding="utf-8")
        if not args.fake:
            candidate, python_exe, weights = model("docufcn-norhand-line", "envs/docufcn")
            name = "docufcn-norhand-line (retificado)"
            on_rectified = _run(
                name, candidate, rectified_manifest, python_exe, weights, limits, wait
            )
            stages[name] = on_rectified["summary"]

    candidate, python_exe, weights = model("docufcn-norhand-line", "envs/docufcn")
    name = "docufcn-norhand-line (original)"
    on_original = _run(name, candidate, manifest_path, python_exe, weights, limits, wait)
    stages[name] = on_original["summary"]
    candidate, python_exe, weights = model("heron", "envs/heron")
    heron = _run("heron", candidate, manifest_path, python_exe, weights, limits, wait)
    stages["heron"] = heron["summary"]

    pages = {}
    for page in manifest["pages"]:
        pid = page["id"]
        lines = {"original": on_original["predictions"][pid]["lines"]}
        if on_rectified is not None:
            info = rectification[pid]
            predicted = on_rectified["predictions"].get(pid)
            if predicted is None or "homography" not in info:
                lines["rectified"] = lines["original"]
            else:
                lines["rectified"] = _back_to_photo(predicted["lines"], info["homography"])
        item: dict[str, Any] = {"blocks": heron["predictions"][pid]["blocks"], "lines": lines}
        if pid in rectification:
            item["rectification"] = {
                k: v for k, v in rectification[pid].items() if k != "homography"
            }
        pages[pid] = item

    output = {
        "schema": "leitorum-di-detected-layout/2",
        "set": args.set,
        "fake": args.fake,
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "pipeline": "contour → docufcn-norhand-line (linhas) + heron (blocos) — ADR-002",
        "stages": stages,
        "pages": pages,
    }
    suffix = "-fake" if args.fake else ""
    out = OUT_DIR / f"detected-{args.set}{suffix}.json"
    out.write_text(json.dumps(output, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Layout detectado gravado em {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
