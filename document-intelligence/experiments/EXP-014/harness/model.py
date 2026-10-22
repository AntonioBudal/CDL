"""Reconhecedor PP-OCRv6 small em PyTorch (convertido do ONNX) e o pré-processamento do
``rapidocr``.

Convenções do ``rapidocr`` reproduzidas:

* lista de caracteres = ``["blank"] + dicionário dos metadados do ONNX + [" "]``; índice 0 é o
  branco do CTC;
* a linha é redimensionada para 48 px de altura mantendo a proporção (largura mínima de 320 px),
  normalizada para [-1, 1] e completada com zeros à direita;
* aqui a largura é completada até múltiplo de 32 (o grafo convertido tem o preenchimento das
  convoluções
  fixado para larguras pares nas camadas com passo 2).
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path

import cv2
import numpy as np
import onnx
import torch
from onnx2torch import convert
from onnx_fix import fix

ROOT = Path(__file__).resolve().parents[3]
ONNX_MODEL = (
    ROOT / "experiments" / "EXP-008" / "envs" / "ppocr" / ".venv" / "Lib" / "site-packages"
    / "rapidocr" / "models" / "PP-OCRv6_rec_small.onnx"
)  # fmt: skip
ONNX_SHA256 = "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884"
HEIGHT, MIN_WIDTH, MULTIPLE, MAX_WIDTH = 48, 320, 32, 1600


def load() -> tuple[torch.nn.Module, list[str]]:
    """Modelo PyTorch e lista de caracteres (índice 0 = branco)."""
    if hashlib.sha256(ONNX_MODEL.read_bytes()).hexdigest() != ONNX_SHA256:
        raise SystemExit("SHA-256 do modelo não confere")
    graph = onnx.load(str(ONNX_MODEL))
    characters = {p.key: p.value for p in graph.metadata_props}["character"].splitlines()
    graph, _ = fix(graph)
    return convert(graph), ["blank", *characters, " "]


def preprocess(image: np.ndarray, extra: int = 0) -> np.ndarray:
    """Linha BGR → tensor (3, 48, W) normalizado, como no ``rapidocr``.

    ``extra`` acrescenta essa margem vazia (zeros) à direita; o EXP-014 mediu que ela melhora a
    leitura.
    """
    h, w = image.shape[:2]
    resized_w = min(MAX_WIDTH, max(1, math.ceil(HEIGHT * w / h)))
    resized = cv2.resize(image, (resized_w, HEIGHT)).astype(np.float32)
    resized = (resized.transpose(2, 0, 1) / 255 - 0.5) / 0.5
    width = max(MIN_WIDTH, math.ceil((resized_w + extra) / MULTIPLE) * MULTIPLE)
    out = np.zeros((3, HEIGHT, width), dtype=np.float32)
    out[:, :, :resized_w] = resized
    return out


def batch(images: list[np.ndarray]) -> torch.Tensor:
    """Empilha linhas pré-processadas, completando todas até a maior largura do lote."""
    width = max(image.shape[2] for image in images)
    out = np.zeros((len(images), 3, HEIGHT, width), dtype=np.float32)
    for index, image in enumerate(images):
        out[index, :, :, : image.shape[2]] = image
    return torch.from_numpy(out)


def encode(text: str, index: dict[str, int]) -> tuple[list[int], int]:
    """Texto → índices (sem os caracteres fora do dicionário) e quantos caracteres foram
    descartados."""
    ids = [index[c] for c in text if c in index]
    return ids, len(text) - len(ids)


def decode(probabilities: torch.Tensor, characters: list[str]) -> list[str]:
    """Decodificação gulosa do CTC (colapsa repetições e remove o branco)."""
    out = []
    for row in probabilities.argmax(dim=-1).tolist():
        text, previous = [], None
        for token in row:
            if token != previous and token != 0:
                text.append(characters[token])
            previous = token
        out.append("".join(text))
    return out


def freeze_batchnorm(model: torch.nn.Module) -> None:
    """Mantém as estatísticas da normalização em lote fixas (lotes pequenos e larguras
    variáveis)."""
    for module in model.modules():
        if isinstance(module, torch.nn.modules.batchnorm._BatchNorm):
            module.eval()
