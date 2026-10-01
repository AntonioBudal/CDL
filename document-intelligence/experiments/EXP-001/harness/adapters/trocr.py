"""Adaptador TrOCR (Transformer encoder-decoder) com decodificação gulosa.

Roda no ambiente ``envs/trocr`` (Python 3.14, torch 2.x, CPU), totalmente offline a partir de um
diretório local. LICENSE STATUS: NEEDS VALIDATION — uso experimental local autorizado pelo
usuário; não pode ser promovido a feature de produto.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

MAX_NEW_TOKENS = 128
# Convenção do XLMRobertaTokenizer: 0 <s>, 1 <pad>, 2 </s>, 3 <unk>; demais ids = id do
# SentencePiece + 1. O vocabulário é lido direto do arquivo .model porque o transformers 5 não
# carrega este tokenizador legado.
_FIRST_PIECE_ID = 4
_FAIRSEQ_OFFSET = 1


class TrOCRRecognizer:
    def load(self, context: dict[str, Any]) -> None:
        import sentencepiece
        import torch
        import transformers
        from transformers import AutoImageProcessor, VisionEncoderDecoderModel

        self._torch = torch
        self._transformers_version = transformers.__version__
        self._options = context["options"]
        weights_dir = self._options["weights_dir"]
        torch.manual_seed(int(self._options.get("seed", 1234)))
        torch.set_grad_enabled(False)

        self._processor = AutoImageProcessor.from_pretrained(weights_dir, local_files_only=True)
        self._pieces = sentencepiece.SentencePieceProcessor(
            model_file=str(Path(weights_dir) / "sentencepiece.bpe.model")
        )
        self._model = VisionEncoderDecoderModel.from_pretrained(
            weights_dir, local_files_only=True
        )
        self._model.eval()

    def recognize(self, image_path: str) -> str:
        from PIL import Image

        with Image.open(image_path) as image:
            pixel_values = self._processor(images=image.convert("RGB"), return_tensors="pt")
        generated = self._model.generate(
            pixel_values.pixel_values,
            max_new_tokens=MAX_NEW_TOKENS,
            num_beams=1,
            do_sample=False,
            use_cache=True,
        )
        limit = self._pieces.get_piece_size() + _FAIRSEQ_OFFSET
        ids = [
            token - _FAIRSEQ_OFFSET
            for token in generated[0].tolist()
            if _FIRST_PIECE_ID <= token < limit
        ]
        return self._pieces.decode(ids)

    def describe(self) -> dict[str, Any]:
        return {
            "id": self._options.get("id"),
            "family": "Transformer encoder-decoder",
            "library": f"transformers {self._transformers_version}",
            "torch": self._torch.__version__,
            "threads": self._torch.get_num_threads(),
            "decoding": f"greedy, max_new_tokens={MAX_NEW_TOKENS}, use_cache=True",
            "license_status": "NEEDS VALIDATION",
        }
