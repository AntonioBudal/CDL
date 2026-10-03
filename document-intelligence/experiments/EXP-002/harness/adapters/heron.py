"""Adaptador Docling Heron (RT-DETRv2, detector de layout). Roda em ``envs/heron``.

Produz só blocos. Correspondência de classes (plan.md): ``title``/``section_header`` → ``title``;
``text``/``list_item`` → ``paragraph``; ``picture`` → ``graphic_box``;
``footnote``/``page_header``/``page_footer`` → ``margin_note`` (aproximação).
As demais são descartadas.
"""

from __future__ import annotations

from typing import Any

CLASS_MAP = {
    "title": "title",
    "section_header": "title",
    "text": "paragraph",
    "list_item": "paragraph",
    "picture": "graphic_box",
    "footnote": "margin_note",
    "page_header": "margin_note",
    "page_footer": "margin_note",
}
SCORE_THRESHOLD = 0.3


class HeronDetector:
    def load(self, context: dict[str, Any]) -> None:
        import torch
        import transformers
        from transformers import AutoImageProcessor, RTDetrV2ForObjectDetection

        options = context["options"]
        weights_dir = options["weights_dir"]
        torch.manual_seed(int(options.get("seed", 1234)))
        torch.set_grad_enabled(False)
        self._torch = torch
        self._version = transformers.__version__
        self._id = options.get("id")
        self._processor = AutoImageProcessor.from_pretrained(weights_dir, local_files_only=True)
        self._model = RTDetrV2ForObjectDetection.from_pretrained(weights_dir, local_files_only=True)
        self._model.eval()
        self._labels = self._model.config.id2label

    def predict(self, image_path: str) -> dict[str, Any]:
        from PIL import Image

        with Image.open(image_path) as image:
            rgb = image.convert("RGB")
            inputs = self._processor(images=rgb, return_tensors="pt")
            outputs = self._model(**inputs)
            results = self._processor.post_process_object_detection(
                outputs, target_sizes=[(rgb.height, rgb.width)], threshold=SCORE_THRESHOLD
            )[0]
        blocks = []
        for score, label, box in zip(
            results["scores"], results["labels"], results["boxes"], strict=True
        ):
            mapped = CLASS_MAP.get(self._labels[int(label)])
            if mapped is None:
                continue
            blocks.append(
                {"type": mapped, "bbox": [round(float(v)) for v in box], "score": float(score)}
            )
        return {"lines": [], "blocks": blocks}

    def describe(self) -> dict[str, Any]:
        return {
            "id": self._id,
            "family": "RT-DETRv2 (Docling Heron)",
            "library": f"transformers {self._version}",
            "torch": self._torch.__version__,
            "threads": self._torch.get_num_threads(),
            "score_threshold": SCORE_THRESHOLD,
            "class_map": CLASS_MAP,
        }
