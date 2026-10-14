"""Caminhos, conjuntos e funções de medida compartilhadas pelo harness do EXP-008."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from leitorum_di.metrics.detection import detection_counts, match_detections, precision_recall_f1

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset" / "processed" / "exp-008"
EXP007_DATA = ROOT / "dataset" / "processed" / "exp-007"

# Conjuntos: calibração (preparados aqui) e teste (verdade de chão do EXP-007, só leitura).
SETS = {
    "cal-gnhk": DATA / "cal-gnhk-manifest.json",
    "cal-bressay": DATA / "cal-bressay-manifest.json",
    "test-gnhk": EXP007_DATA / "gnhk-manifest.json",
    "test-bressay": EXP007_DATA / "bressay-x3-manifest.json",
}
CALIBRATION_SETS = ("cal-gnhk", "cal-bressay")
TEST_SETS = ("test-gnhk", "test-bressay")
EXP007_DETECTED = {"test-gnhk": "detected-gnhk.json", "test-bressay": "detected-bressay-x3.json"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(name: str) -> dict[str, Any]:
    return json.loads(SETS[name].read_text(encoding="utf-8"))


def detection_path(candidate: str, name: str) -> Path:
    return DATA / f"det-{candidate}-{name}.json"


def load_detection(candidate: str, name: str) -> dict[str, Any]:
    detection = json.loads(detection_path(candidate, name).read_text(encoding="utf-8"))
    if detection["manifest_sha256"] != sha256_file(SETS[name]):
        raise SystemExit(f"{candidate}/{name}: detecção não corresponde ao manifesto atual")
    return detection


def write_json(path: Path, content: Any, indent: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(content, ensure_ascii=False, indent=indent) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def git_state() -> dict[str, object]:
    def git(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
            )
        except (OSError, subprocess.CalledProcessError):
            return None
        return out.stdout.strip()

    status = git("status", "--porcelain", "--", ".", ":(exclude)evaluation")
    return {"commit": git("rev-parse", "HEAD"), "dirty": None if status is None else bool(status)}


def _intersection(a, b) -> float:
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def _area(box) -> float:
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def ignored(box, regions) -> bool:
    """Mesma regra do avaliador: descarta a detecção com ≥ 50 % da área numa região a ignorar."""
    area = _area(box)
    return area == 0 or any(_intersection(box, region) / area >= 0.5 for region in regions)


def kept_boxes(page: dict[str, Any], lines: list[dict[str, Any]]) -> list[list[float]]:
    regions = page.get("ignore", [])
    return [line["bbox"] for line in lines if not ignored(line["bbox"], regions)]


def empty_counts() -> dict[str, float]:
    return {"tp": 0, "fp": 0, "fn": 0, "iou_sum": 0.0}


def add(total: dict[str, float], counts: dict[str, float]) -> None:
    for key in total:
        total[key] += counts[key]


def line_f1(manifest: dict[str, Any], predictions: dict[str, list[dict[str, Any]]]) -> dict:
    """Precisão, revocação e F1 de linhas por caixa (IoU ≥ 0,5), como nos EXP-002 e EXP-007."""
    total = empty_counts()
    for page in manifest["pages"]:
        truths = [line["bbox"] for line in page["lines"]]
        add(total, detection_counts(truths, kept_boxes(page, predictions.get(page["id"], [])), 0.5))
    return precision_recall_f1(total)


def classify_unmatched(truths: list[list[float]], predictions: list[list[float]]) -> Counter:
    """Classes de erro do EXP-007: ``missed``, ``merged``, ``split`` e ``misaligned``."""
    matched = {ti for ti, _, _ in match_detections(truths, predictions, 0.5)}
    kinds: Counter = Counter()
    for index, truth in enumerate(truths):
        if index in matched:
            continue
        area = _area(truth) or 1.0
        covering = [p for p in predictions if _intersection(truth, p) / area >= 0.5]
        inside = [p for p in predictions if _intersection(truth, p) / (_area(p) or 1.0) >= 0.5]
        merged = any(
            _intersection(other, p) / (_area(other) or 1.0) >= 0.5
            for p in covering
            for k, other in enumerate(truths)
            if k != index
        )
        if merged:
            kinds["merged"] += 1
        elif len(inside) >= 2:
            kinds["split"] += 1
        elif covering or inside:
            kinds["misaligned"] += 1
        else:
            kinds["missed"] += 1
    return kinds


def oracle_merge(truths: list[list[float]], predictions: list[list[float]]) -> list[list[float]]:
    """Teto de fusão: une as predições que estão mais da metade dentro da mesma linha verdadeira."""
    groups: dict[int, list[list[float]]] = {}
    rest = []
    for prediction in predictions:
        area = _area(prediction) or 1.0
        shares = [_intersection(truth, prediction) / area for truth in truths]
        best = max(range(len(truths)), key=shares.__getitem__, default=None)
        if best is None or shares[best] < 0.5:
            rest.append(prediction)
        else:
            groups.setdefault(best, []).append(prediction)
    merged = [
        [min(b[0] for b in g), min(b[1] for b in g), max(b[2] for b in g), max(b[3] for b in g)]
        for _, g in sorted(groups.items())
    ]
    return merged + rest
