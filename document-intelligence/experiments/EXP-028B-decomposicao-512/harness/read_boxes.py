"""T002 — três leituras das mesmas páginas com o leitor do produto, mudando só as caixas. Roda no
**ambiente do motor** (só importa ``leitorum_motor``; nada no motor é alterado):

* **A** — o produto inteiro (``PagePipeline.read``): detecção, escala, fusão, leitura e ordem;
* **B** — as caixas do autor (``di-annotation/1``), na ordem dele, com a mesma escala de página do
  produto (calculada pela altura mediana das caixas) e o mesmo recorte e leitor;
* **C** — o mesmo texto de B, na ordem que a regra do produto (``reading_order``) daria às caixas do
  autor (a leitura de cada caixa não muda; só a ordem).

Grava ``processed/exp-028b/{a,b,c}/pNN.json`` (fora do Git). Imprime só contagens.

Uso (a partir de ``document-intelligence/``)::

    ..\\caderno-leitura-0.1\\motor\\.venv\\Scripts\\python.exe \\
        experiments\\EXP-028B-decomposicao-512\\harness\\read_boxes.py --pages p10,p11,p14,p15
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

DI_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = Path(os.environ.get("EXP028B_DATA_ROOT") or DI_ROOT / "dataset")
MOTOR_DIR = Path(
    os.environ.get("EXP028B_MOTOR_DIR") or DI_ROOT.parent / "caderno-leitura-0.1" / "motor"
)
IMAGES = DATA_ROOT / "processed" / "anotacao" / "imagens"
INDEX = DATA_ROOT / "processed" / "anotacao" / "pages.json"
ANNOTATIONS = DATA_ROOT / "raw" / "anotacao"
OUT = DATA_ROOT / "processed" / "exp-028b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox(polygon: list[list[float]]) -> list[int]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))]


def read_author_boxes(pipeline, pipeline_module, geometry, image_path: Path, lines: list[dict]):
    """Leitura B: caixas do autor, escala e leitor do produto. Devolve textos na ordem do autor e a
    ordem que o produto daria a essas caixas (leitura C)."""
    import cv2

    original = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if original is None:
        raise ValueError("imagem ilegível")
    boxes = [{"bbox": bbox(line["polygon"])} for line in lines]
    scale = pipeline_module.scale_factor(
        pipeline_module.median_height(boxes), pipeline._config.get("target")
    )
    image = original
    if scale > 1:
        image = cv2.resize(original, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    texts = []
    for line in lines:
        polygon = [[x * scale, y * scale] for x, y in line["polygon"]]
        crop = pipeline_module.prepare_line(geometry.crop_line(image, polygon))
        text, confidence = pipeline._read(crop)
        texts.append({"line_id": line["line_id"], "text": text, "confidence": round(confidence, 4)})
    motor_order = geometry.reading_order(boxes)
    return texts, motor_order, scale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Leituras A, B e C do EXP-028B")
    parser.add_argument("--pages", required=True)
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(MOTOR_DIR))
    from leitorum_motor import geometry
    from leitorum_motor import pipeline as pipeline_module

    config = pipeline_module.load_config(MOTOR_DIR / "config.json")
    pipeline = pipeline_module.PagePipeline(config)
    index = json.loads(INDEX.read_text(encoding="utf-8"))["pages"]
    out = Path(args.out)
    report = {"pages": 0, "lines_b": 0, "lines_a": 0, "blocked": []}
    for pid in [p.strip() for p in args.pages.split(",") if p.strip()]:
        image_path = IMAGES / f"{pid}.jpg"
        if not image_path.is_file() or sha256(image_path) != index.get(pid, {}).get("work_sha256"):
            report["blocked"].append(pid)
            continue
        annotation = json.loads((ANNOTATIONS / f"{pid}.json").read_text(encoding="utf-8"))
        lines = sorted(annotation["lines"], key=lambda line: line["order"])
        product = pipeline.read(image_path)
        texts, motor_order, scale = read_author_boxes(
            pipeline, pipeline_module, geometry, image_path, lines
        )
        results = {
            "a": {"lines": [{"text": ln["text"], "bbox": ln["bbox"]} for ln in product["lines"]],
                  "page_scale": product["page_scale"]},
            "b": {"lines": texts, "page_scale": scale},
            "c": {"lines": [texts[i] for i in motor_order], "page_scale": scale,
                  "order_changes": sum(1 for k, i in enumerate(motor_order) if k != i)},
        }
        for name, payload in results.items():
            folder = out / name
            folder.mkdir(parents=True, exist_ok=True)
            payload = {"schema": "exp-028b-reading/1", "page_id": pid, "condition": name,
                       "engine": product["engine"], **payload}
            (folder / f"{pid}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        report["pages"] += 1
        report["lines_b"] += len(texts)
        report["lines_a"] += len(product["lines"])
    print(json.dumps(report, ensure_ascii=False))
    return 0 if not report["blocked"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
