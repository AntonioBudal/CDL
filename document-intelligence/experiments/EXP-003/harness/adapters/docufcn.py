"""Adaptador Doc-UFCN (segmentação de linhas ou de página). Roda em ``envs/docufcn`` (Python 3.10).

Os pesos e o ``parameters.yml`` são lidos de ``options["weights_dir"]`` (revisão fixada, SHA-256
conferido pelo supervisor antes da carga). Todas as classes que não são fundo viram linhas (o modelo
``norhand`` separa linhas horizontais e verticais).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np


class DocUFCNDetector:
    def load(self, context: dict[str, Any]) -> None:
        import torch
        import yaml
        from doc_ufcn.main import DocUFCN

        options = context["options"]
        weights_dir = Path(options["weights_dir"])
        params = yaml.safe_load((weights_dir / "parameters.yml").read_text(encoding="utf-8"))[
            "parameters"
        ]
        torch.manual_seed(int(options.get("seed", 1234)))
        torch.set_grad_enabled(False)
        self._torch = torch
        self._params = params
        self._id = options.get("id")
        self._model = DocUFCN(len(params["classes"]), params["input_size"], "cpu")
        self._model.load(str(weights_dir / "model.pth"), params["mean"], params["std"], mode="eval")

    def predict(self, image_path: str) -> dict[str, Any]:
        image = cv2.cvtColor(cv2.imread(image_path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        polygons, _, _, _ = self._model.predict(image, min_cc=self._params.get("min_cc", 50))
        lines = []
        for channel in range(1, len(self._params["classes"])):
            for item in polygons.get(channel, []):
                points = np.asarray(item["polygon"], dtype=np.float64).reshape(-1, 2)
                if len(points) < 3:
                    continue
                x0, y0 = points.min(axis=0)
                x1, y1 = points.max(axis=0)
                lines.append(
                    {
                        "bbox": [round(x0), round(y0), round(x1), round(y1)],
                        "polygon": [[round(x), round(y)] for x, y in points],
                        "score": float(item.get("confidence", 1.0)),
                    }
                )
        return {"lines": lines, "blocks": []}

    def describe(self) -> dict[str, Any]:
        import doc_ufcn

        return {
            "id": self._id,
            "family": "Doc-UFCN",
            "library": f"doc-ufcn {getattr(doc_ufcn, '__version__', '0.1.9')}",
            "torch": self._torch.__version__,
            "threads": self._torch.get_num_threads(),
            "input_size": self._params["input_size"],
            "classes": self._params["classes"],
        }
