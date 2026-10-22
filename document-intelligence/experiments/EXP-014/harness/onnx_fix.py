"""Torna o grafo ONNX do reconhecedor convertível pelo ``onnx2torch``.

O ``onnx2torch`` não aceita convoluções e agrupamentos (pooling) com ``auto_pad = SAME_UPPER``. Com
a entrada fixada em 48×320, as
dimensões de cada convolução são conhecidas (inferência de formas do ONNX) e o preenchimento pode
ser escrito
explicitamente, com a mesma regra do ONNX: total = max((ceil(n/s) − 1)·s + (k − 1)·d + 1 − n, 0),
metade no
início e o resto no fim.
"""

from __future__ import annotations

import math

import onnx
from onnx import helper, shape_inference

HEIGHT, WIDTH = 48, 320


def same_upper_pads(size: int, kernel: int, stride: int, dilation: int) -> tuple[int, int]:
    """Preenchimento (início, fim) de uma dimensão sob ``SAME_UPPER``."""
    out = math.ceil(size / stride)
    total = max((out - 1) * stride + (kernel - 1) * dilation + 1 - size, 0)
    return total // 2, total - total // 2


def fix(model: onnx.ModelProto) -> tuple[onnx.ModelProto, int]:
    """Fixa a entrada em (N, 3, 48, 320) e troca ``SAME_UPPER`` por preenchimento explícito."""
    dims = model.graph.input[0].type.tensor_type.shape.dim
    dims[2].dim_value, dims[3].dim_value = HEIGHT, WIDTH
    inferred = shape_inference.infer_shapes(model)
    shapes = {}
    for value in list(inferred.graph.value_info) + list(inferred.graph.input):
        shape = [d.dim_value for d in value.type.tensor_type.shape.dim]
        shapes[value.name] = shape
    fixed = 0
    for node in model.graph.node:
        if node.op_type not in ("Conv", "MaxPool", "AveragePool"):
            continue
        attrs = {a.name: a for a in node.attribute}
        if "auto_pad" not in attrs or attrs["auto_pad"].s.decode() != "SAME_UPPER":
            continue
        shape = shapes.get(node.input[0])
        if not shape or len(shape) != 4 or not shape[2] or not shape[3]:
            raise ValueError(f"forma desconhecida na entrada de {node.name}")
        kernel = list(attrs["kernel_shape"].ints)
        strides = list(attrs["strides"].ints) if "strides" in attrs else [1, 1]
        dilations = list(attrs["dilations"].ints) if "dilations" in attrs else [1, 1]
        begin, end = [], []
        for axis in range(2):
            b, e = same_upper_pads(shape[2 + axis], kernel[axis], strides[axis], dilations[axis])
            begin.append(b)
            end.append(e)
        node.attribute.remove(attrs["auto_pad"])
        node.attribute.append(helper.make_attribute("pads", begin + end))
        fixed += 1
    return model, fixed
