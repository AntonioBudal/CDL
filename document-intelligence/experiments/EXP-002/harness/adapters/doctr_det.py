"""Adaptador docTR: detecção de palavras (FAST base) + agrupamento em linhas do próprio docTR.

Roda em ``envs/doctr``. LICENSE STATUS: NEEDS VALIDATION — pesos sem licença declarada; uso
experimental local autorizado pelo usuário; não pode ser promovido a produto. Os pesos são lidos de
arquivo local (sem download), e o backbone não é baixado (``pretrained_backbone=False``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

WEIGHTS_FILE = "fast_base-688a8b34.pt"


class DocTRDetector:
    def load(self, context: dict[str, Any]) -> None:
        import torch
        from doctr.models import detection, detection_predictor
        from doctr.models.builder import DocumentBuilder
        from doctr.models.utils import load_pretrained_params

        options = context["options"]
        torch.manual_seed(int(options.get("seed", 1234)))
        torch.set_grad_enabled(False)
        self._torch = torch
        self._id = options.get("id")
        model = detection.fast_base(pretrained=False, pretrained_backbone=False)
        load_pretrained_params(model, str(Path(options["weights_dir"]) / WEIGHTS_FILE))
        model = detection.zoo.reparameterize(model)
        model.eval()
        self._predictor = detection_predictor(arch=model, pretrained=False, batch_size=1)
        self._builder = DocumentBuilder()

    def predict(self, image_path: str) -> dict[str, Any]:
        from PIL import Image

        with Image.open(image_path) as image:
            page = np.asarray(image.convert("RGB"))
        height, width = page.shape[:2]
        output = self._predictor([page])[0]
        words = output["words"] if isinstance(output, dict) else output
        words = np.asarray(words, dtype=np.float64).reshape(-1, 5)
        if len(words) == 0:
            return {"lines": [], "blocks": []}
        groups = self._builder._resolve_lines(words[:, :4])
        lines = []
        for group in groups:
            boxes = words[group]
            x0, y0 = boxes[:, 0].min() * width, boxes[:, 1].min() * height
            x1, y1 = boxes[:, 2].max() * width, boxes[:, 3].max() * height
            bbox = [round(x0), round(y0), round(x1), round(y1)]
            polygon = [
                [bbox[0], bbox[1]],
                [bbox[2], bbox[1]],
                [bbox[2], bbox[3]],
                [bbox[0], bbox[3]],
            ]
            lines.append({"bbox": bbox, "polygon": polygon, "score": float(boxes[:, 4].mean())})
        return {"lines": lines, "blocks": []}

    def describe(self) -> dict[str, Any]:
        import doctr

        return {
            "id": self._id,
            "family": "docTR FAST base + agrupamento em linhas (DocumentBuilder)",
            "library": f"python-doctr {doctr.__version__}",
            "torch": self._torch.__version__,
            "threads": self._torch.get_num_threads(),
            "weights_file": WEIGHTS_FILE,
            "license_status": "NEEDS VALIDATION",
        }
