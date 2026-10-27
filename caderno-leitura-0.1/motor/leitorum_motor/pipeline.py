"""Leitura de uma página: detecção, escala automática, recorte e leitura das linhas.

Promovido de ``document-intelligence/experiments/EXP-019/harness/pipeline.py`` (commit ``3b695c5``,
pipeline do ADR-008) sem mudança de lógica de leitura. Diferenças em relação ao experimento:

* configuração vem de ``config.json`` (leitor, SHA-256, licença, alvo, fusão, margem);
* os modelos são conferidos **antes** de criar o RapidOCR, para que a biblioteca nunca tente baixá-los;
* o leitor só é carregado com ``license_status == "VERIFIED"``;
* as linhas saem já em ordem de leitura, com ``text``, ``confidence`` e ``bbox``.

Sem rede e sem correção lexical (research R6 da feature 086).
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from importlib import metadata
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from .geometry import box_points, crop_line, reading_order
from .merge import MergeParams, merge_lines

PACKAGE = Path(__file__).resolve().parent
DEFAULT_CONFIG = PACKAGE.parent / "config.json"  # motor/config.json (instalação editável)
SCHEMA = "leitorum-motor/1"
MIN_HEIGHT = 32
MAX_SCALE = 4


class IntegrityError(Exception):
    """Modelo ausente, SHA-256 diferente ou leitor sem licença verificada."""


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else DEFAULT_CONFIG
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["_base"] = str(config_path.parent)
    return config


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rec_input(image: np.ndarray, extra: int) -> np.ndarray:
    """Linha → tensor (1, 3, 48, W): altura 48, proporção mantida, [-1, 1], margem à direita."""
    h, w = image.shape[:2]
    resized_w = max(1, math.ceil(48 * w / h))
    resized = cv2.resize(image, (resized_w, 48)).astype(np.float32)
    resized = (resized.transpose(2, 0, 1) / 255 - 0.5) / 0.5
    width = math.ceil(max(320, resized_w + extra) / 32) * 32
    out = np.zeros((1, 3, 48, width), dtype=np.float32)
    out[0, :, :, :resized_w] = resized
    return out


def ctc_greedy(probs: np.ndarray, characters: list[str]) -> tuple[str, float]:
    """Decodificação gulosa do CTC; confiança = média das probabilidades dos símbolos mantidos."""
    tokens = probs.argmax(-1)
    text, confidences, previous = [], [], None
    for position, token in enumerate(tokens):
        if token != previous and token != 0:
            text.append(characters[token])
            confidences.append(float(probs[position, token]))
        previous = token
    return "".join(text), float(np.mean(confidences)) if confidences else 0.0


def median_height(lines: list[dict[str, Any]]) -> float | None:
    """Altura mediana (px) das linhas detectadas, ou ``None`` se não houver linha."""
    heights = sorted(ln["bbox"][3] - ln["bbox"][1] for ln in lines)
    return float(heights[len(heights) // 2]) if heights else None


def scale_factor(height: float | None, target: float | None) -> int:
    """Fator inteiro de ampliação da página para as linhas chegarem perto de ``target`` px."""
    if not target or not height or height <= 0:
        return 1
    return int(max(1, min(MAX_SCALE, round(target / height))))


def to_original(line: dict[str, Any], scale: int) -> dict[str, Any]:
    """Leva caixa e contorno de volta às coordenadas da imagem recebida."""
    if scale == 1:
        return dict(line)
    return {
        **line,
        "bbox": [round(v / scale) for v in line["bbox"]],
        "polygon": [[round(x / scale, 1), round(y / scale, 1)] for x, y in line["polygon"]]
        if line.get("polygon")
        else None,
    }


def prepare_line(image: np.ndarray, min_height: int = MIN_HEIGHT) -> np.ndarray:
    """Amplia 2× o recorte baixo demais (regra do EXP-010)."""
    if image.shape[0] < min_height:
        return cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return image


def model_paths(config: dict[str, Any]) -> tuple[Path, Path]:
    """Caminhos do detector e do leitor; o leitor ``file: null`` é o embutido no wheel do rapidocr."""
    import rapidocr

    bundled = Path(rapidocr.__file__).parent / "models"
    detector = bundled / config["detector"]["file"]
    reader_file = config["reader"].get("file")
    if reader_file:
        reader = Path(reader_file)
        if not reader.is_absolute():
            reader = Path(config["_base"]) / reader
    else:
        reader = bundled / "PP-OCRv6_rec_small.onnx"
    return detector, reader


def verify(config: dict[str, Any]) -> tuple[Path, Path]:
    """Confere licença, existência e SHA-256 dos modelos; levanta ``IntegrityError``."""
    if config["reader"].get("license_status") != "VERIFIED":
        raise IntegrityError("leitor sem licença verificada")
    detector, reader = model_paths(config)
    for path, expected in ((detector, config["detector"]["sha256"]), (reader, config["reader"]["sha256"])):
        if not path.is_file():
            raise IntegrityError(f"modelo ausente: {path.name}")
        if sha256(path) != expected:
            raise IntegrityError(f"SHA-256 não confere: {path.name}")
    return detector, reader


def describe(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": "leitorum-motor",
        "version": metadata.version("leitorum-motor"),
        "detector": "PP-OCRv6 small (rapidocr " + metadata.version("rapidocr") + ")",
        "reader": config["reader"]["name"],
        "reader_sha256": config["reader"]["sha256"],
        "license_status": config["reader"]["license_status"],
    }


class PagePipeline:
    def __init__(self, config: dict[str, Any]) -> None:
        _, reader = verify(config)
        import onnxruntime as ort
        from rapidocr import RapidOCR

        logging.getLogger("RapidOCR").setLevel(logging.ERROR)
        self._config = config
        self._merge = MergeParams(**config["merge"])
        self._engine = RapidOCR()
        self._rec = ort.InferenceSession(str(reader), providers=["CPUExecutionProvider"])
        meta = self._rec.get_modelmeta().custom_metadata_map
        self._characters = ["blank", *meta["character"].splitlines(), " "]
        self._extra = int(config.get("right_margin", 640))

    def _read(self, crop: np.ndarray) -> tuple[str, float]:
        """Leitura direta pelo ONNX Runtime, com a margem à direita do EXP-014."""
        feed = {self._rec.get_inputs()[0].name: rec_input(crop, self._extra)}
        probs = self._rec.run(None, feed)[0][0]
        return ctc_greedy(probs, self._characters)

    def _detect(self, image: np.ndarray) -> list[dict[str, Any]]:
        detected = self._engine(image, use_det=True, use_cls=False, use_rec=False)
        boxes = getattr(detected, "boxes", None)
        scores = getattr(detected, "scores", None)
        lines = []
        if boxes is not None:
            for index, box in enumerate(np.asarray(boxes, dtype=np.float64).reshape(-1, 4, 2)):
                x0, y0 = box.min(axis=0)
                x1, y1 = box.max(axis=0)
                if x1 > x0 and y1 > y0:
                    lines.append(
                        {
                            "bbox": [round(x0), round(y0), round(x1), round(y1)],
                            "polygon": [[round(x), round(y)] for x, y in box],
                            "score": float(scores[index]) if scores is not None else 1.0,
                        }
                    )
        return lines

    def read(self, image_path: str | Path) -> dict[str, Any]:
        """Lê a página; levanta ``ValueError`` se o OpenCV não conseguir abrir a imagem."""
        started = time.perf_counter()
        original = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if original is None:
            raise ValueError("imagem ilegível")
        lines = self._detect(original)
        scale = scale_factor(median_height(lines), self._config.get("target"))
        image = original
        if scale > 1:
            image = cv2.resize(original, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            lines = self._detect(image)
        out = []
        for line in merge_lines(lines, self._merge):
            crop = prepare_line(crop_line(image, line.get("polygon") or box_points(line["bbox"])))
            text, confidence = self._read(crop)
            out.append({**to_original(line, scale), "text": text, "confidence": confidence})
        ordered = [out[i] for i in reading_order(out)]
        height, width = original.shape[:2]
        return {
            "schema": SCHEMA,
            "image": {"width": int(width), "height": int(height)},
            "lines": [
                {"text": ln["text"], "confidence": round(ln["confidence"], 4), "bbox": ln["bbox"]}
                for ln in ordered
            ],
            "page_scale": scale,
            "engine": describe(self._config),
            "elapsed_ms": round((time.perf_counter() - started) * 1000),
        }
