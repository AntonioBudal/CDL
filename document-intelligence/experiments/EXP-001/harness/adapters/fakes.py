"""Reconhecedores falsos para testar os critérios de parada do supervisor. Não são modelos."""

from __future__ import annotations

import time
from typing import Any

from adapters.echo import EchoRecognizer

_CHUNK = 16 * 1024 * 1024


class MemoryHogRecognizer(EchoRecognizer):
    """Aloca memória aos poucos durante a carga (até ``total_mib``)."""

    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        total = int(context["options"].get("total_mib", 320)) * 1024 * 1024
        self._blocks = []
        while len(self._blocks) * _CHUNK < total:
            self._blocks.append(bytearray(b"\x01") * _CHUNK)
            time.sleep(0.03)


class SlowLoadRecognizer(EchoRecognizer):
    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        time.sleep(float(context["options"].get("load_seconds", 30)))


class SlowLineRecognizer(EchoRecognizer):
    def load(self, context: dict[str, Any]) -> None:
        super().load(context)
        self._delay = float(context["options"].get("line_seconds", 0.2))

    def recognize(self, image_path: str) -> str:
        time.sleep(self._delay)
        return super().recognize(image_path)


class CrashingRecognizer(EchoRecognizer):
    def load(self, context: dict[str, Any]) -> None:
        raise RuntimeError("falha simulada na carga")


class NoisyRecognizer(EchoRecognizer):
    """Devolve a referência sem acentos, para exercitar o avaliador com erros conhecidos."""

    def recognize(self, image_path: str) -> str:
        import unicodedata

        text = super().recognize(image_path)
        decomposed = unicodedata.normalize("NFD", text)
        return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
