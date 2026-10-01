"""Adaptador PyLaia (CNN-RNN-CTC) com decodificação gulosa, sem modelo de linguagem.

Roda no ambiente ``envs/pylaia`` (Python 3.10, torch 1.13, CPU). A saída é a sequência bruta
do modelo: sem léxico, sem correção posterior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

FIXED_HEIGHT = 128  # altura usada no treino dos modelos Teklia


class PyLaiaRecognizer:
    def load(self, context: dict[str, Any]) -> None:
        import torch
        from laia.common.loader import ModelLoader
        from laia.data.transforms.vision import ToImageTensor

        self._torch = torch
        self._options = context["options"]
        weights_dir = Path(self._options["weights_dir"])
        torch.manual_seed(int(self._options.get("seed", 1234)))
        torch.set_grad_enabled(False)

        self._symbols: dict[int, str] = {}
        for line in (weights_dir / "syms.txt").read_text(encoding="utf-8").splitlines():
            if line.strip():
                symbol, index = line.rsplit(maxsplit=1)
                self._symbols[int(index)] = symbol

        loader = ModelLoader(str(weights_dir), filename="model", device="cpu")
        self._model = loader.load_by(str(weights_dir / "weights.ckpt"))
        self._model.eval()
        self._transform = ToImageTensor(invert=True, mode="L", fixed_height=FIXED_HEIGHT)

    def recognize(self, image_path: str) -> str:
        from PIL import Image

        torch = self._torch
        with Image.open(image_path) as image:
            tensor = self._transform(image).unsqueeze(0)  # N x C x H x W
        output = self._model(tensor)
        if isinstance(output, torch.nn.utils.rnn.PackedSequence):
            output, _ = torch.nn.utils.rnn.pad_packed_sequence(output)
        best = output.argmax(dim=-1).reshape(-1).tolist()  # T (N = 1)

        chars = []
        previous = None
        for index in best:
            if index != previous and index != 0:  # 0 = símbolo CTC (blank)
                symbol = self._symbols[index]
                chars.append(" " if symbol == "<space>" else symbol)
            previous = index
        return "".join(chars)

    def describe(self) -> dict[str, Any]:
        import laia

        return {
            "id": self._options.get("id"),
            "family": "CNN-RNN-CTC",
            "library": f"pylaia {laia.__version__.split('-')[0]}",
            "torch": self._torch.__version__,
            "threads": self._torch.get_num_threads(),
            "decoding": "ctc-greedy, sem modelo de linguagem",
            "fixed_height": FIXED_HEIGHT,
            "symbols": len(self._symbols),
        }
