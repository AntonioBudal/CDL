"""EXP-023: exporta os casos de paridade para a feature 089 do Leitorum (só dados fictícios).

Para as 24 páginas de teste em 6 condições (CER 0, 10 e 25 %, com e sem geometria), roda a
implementação de referência com ``organizer-v1.json`` e grava texto, linhas e resultado esperado em
``artifacts/parity-v1.json``. O Leitorum copia o arquivo e exige o mesmo resultado em cada caso.
"""

from __future__ import annotations

import hashlib
import json
import sys

import organizer as org
from evaluate import load_model
from pages import build_pages, layout, page_text, with_noise
from train import ART, CERS, NOISE


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    noise_model = json.loads(NOISE.read_text(encoding="utf-8"))
    model, _ = load_model()
    engine = org.Organizer(model)
    cases = []
    for page in build_pages()["test"]:
        for cer in CERS:
            noisy = with_noise(page, noise_model, cer)
            text, _, _ = page_text(noisy)
            for geo in (True, False):
                lines = layout(noisy) if geo else None
                result = engine.organize(text, lines)
                cases.append(
                    {
                        "id": f"{page['id']}-cer{int(cer * 100):02d}-{'geo' if geo else 'sem-geo'}",
                        "text": text,
                        "lines": lines,
                        "expected": {
                            "segments": [
                                {
                                    **{
                                        k: s[k]
                                        for k in ("start", "end", "section", "confidence", "review")
                                    },
                                    "text": text[s["start"] : s["end"]],
                                }
                                for s in result["segments"]
                            ],
                            "sections": result["sections"],
                            "explicit_headings": result["explicit_headings"],
                        },
                    }
                )
    artifact_sha = (ART / "organizer-v1.sha256").read_text(encoding="utf-8").strip()
    body = json.dumps(
        {
            "license": "MIT — páginas fictícias do EXP-023",
            "artifact_sha256": artifact_sha,
            "cases": cases,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    (ART / "parity-v1.json").write_text(body, encoding="utf-8")
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    (ART / "parity-v1.sha256").write_text(sha + "\n", encoding="utf-8")
    print(f"{len(cases)} casos; {len(body) / 1e6:.2f} MB; sha256 {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
