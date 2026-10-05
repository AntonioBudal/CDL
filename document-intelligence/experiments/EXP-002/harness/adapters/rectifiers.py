"""Retificadores de perspectiva como etapa própria do benchmark (custo medido separadamente).

Cada retificador recebe a imagem original, grava a imagem retificada em ``options["output_dir"]`` e
devolve o quadrilátero da folha e a homografia. Compatível com Python 3.10.

* ``ContourRectifier``: clássico (OpenCV), roda no ambiente do harness.
* ``DocUFCNPageRectifier``: máscara de página do Doc-UFCN, roda em ``envs/docufcn``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np
from rectify import find_page_contour, quad_from_region, rectify


class _BaseRectifier:
    def load(self, context: dict[str, Any]) -> None:
        self._options = context["options"]
        self._output = Path(self._options["output_dir"])
        self._output.mkdir(parents=True, exist_ok=True)

    def _quad(self, image_bgr: np.ndarray):
        raise NotImplementedError

    def predict(self, image_path: str) -> dict[str, Any]:
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        quad = self._quad(image)
        found = quad is not None
        if found:
            warped, homography = rectify(image, quad)
        else:
            h, w = image.shape[:2]
            quad = np.float64([[0, 0], [w, 0], [w, h], [0, h]])
            warped, homography = image, np.eye(3)
        target = self._output / (Path(image_path).stem + ".png")
        cv2.imwrite(str(target), warped)
        return {
            "lines": [],
            "blocks": [],
            "rectification": {
                "found": bool(found),
                "quad": [[float(x), float(y)] for x, y in quad],
                "homography": [[float(v) for v in row] for row in np.asarray(homography)],
                "size": [int(warped.shape[1]), int(warped.shape[0])],
                "output": str(target),
            },
        }


class ContourRectifier(_BaseRectifier):
    def _quad(self, image_bgr: np.ndarray):
        return find_page_contour(image_bgr)

    def describe(self) -> dict[str, Any]:
        return {
            "id": self._options.get("id"),
            "family": "contorno da folha (OpenCV)",
            "opencv": cv2.__version__,
        }


class DocUFCNPageRectifier(_BaseRectifier):
    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        import torch
        import yaml
        from doc_ufcn.main import DocUFCN

        weights_dir = Path(self._options["weights_dir"])
        text = (weights_dir / "parameters.yml").read_text(encoding="utf-8")
        self._params = yaml.safe_load(text)["parameters"]
        torch.manual_seed(int(self._options.get("seed", 1234)))
        torch.set_grad_enabled(False)
        self._torch = torch
        params = self._params
        self._model = DocUFCN(len(params["classes"]), params["input_size"], "cpu")
        self._model.load(str(weights_dir / "model.pth"), params["mean"], params["std"], mode="eval")

    def _quad(self, image_bgr: np.ndarray):
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        polygons, _, _, _ = self._model.predict(rgb, min_cc=self._params.get("min_cc", 50))
        regions = [
            np.asarray(item["polygon"], dtype=np.float64).reshape(-1, 2)
            for item in polygons.get(1, [])
        ]
        regions = [r for r in regions if len(r) >= 3]
        if not regions:
            return None
        largest = max(regions, key=lambda r: cv2.contourArea(r.astype(np.float32)))
        area = cv2.contourArea(largest.astype(np.float32))
        if area < 0.25 * image_bgr.shape[0] * image_bgr.shape[1]:
            return None
        return quad_from_region(largest)

    def describe(self) -> dict[str, Any]:
        return {
            "id": self._options.get("id"),
            "family": "máscara de página Doc-UFCN",
            "torch": self._torch.__version__,
            "threads": self._torch.get_num_threads(),
        }
