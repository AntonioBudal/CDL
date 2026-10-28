"""EXP-025: casos de paridade do ``organizer-v2`` para a feature do Leitorum (só dados fictícios).

- **Páginas do EXP-023 (teste):** 6 condições (CER 0, 10 e 25 %, com e sem geometria), como o
  ``parity-v1``.
- **Páginas *holdout* de teste do EXP-024:** com e sem geometria, as que trazem os formatos de
  fichamento.

O Leitorum copia ``artifacts/parity-v2.json`` e exige o mesmo resultado em cada caso.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPS = HERE.parents[1]
for path in (HERE, EXPS / "EXP-023" / "harness"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
sys.path.append(str(EXPS / "EXP-024" / "harness"))

import organizer_v2 as v2  # noqa: E402
import pages  # noqa: E402
import streams  # noqa: E402

ART = HERE.parent / "artifacts"
NOISE = EXPS.parent / "dataset" / "processed" / "exp-023" / "noise-model.json"


def case(engine, case_id: str, text: str, lines) -> dict:
    result = engine.organize(text, lines)
    return {
        "id": case_id,
        "text": text,
        "lines": lines,
        "expected": {
            "segments": [
                {
                    **{k: s[k] for k in ("start", "end", "section", "confidence", "review")},
                    "text": text[s["start"] : s["end"]],
                }
                for s in result["segments"]
            ],
            "sections": result["sections"],
            "explicit_headings": result["explicit_headings"],
        },
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    engine = v2.load()
    noise = json.loads(NOISE.read_text(encoding="utf-8"))
    cases = []
    for page in pages.build_pages()["test"]:
        for cer in (0.0, 0.10, 0.25):
            noisy = pages.with_noise(page, noise, cer)
            text, _, _ = pages.page_text(noisy)
            for geo in (True, False):
                tag = f"{page['id']}-cer{int(cer * 100):02d}-{'geo' if geo else 'sem-geo'}"
                cases.append(case(engine, tag, text, pages.layout(noisy) if geo else None))
    for st in streams.all_streams("test").values():
        for book_pages in st["holdout"].values():
            for page in book_pages[:3]:
                text, _, _ = streams.page_text(page)
                for geo in (True, False):
                    tag = f"{page['id']}-{'geo' if geo else 'sem-geo'}"
                    cases.append(case(engine, tag, text, streams.layout(page) if geo else None))
    artifact_sha = (ART / "organizer-v2.sha256").read_text(encoding="utf-8").strip()
    body = json.dumps(
        {
            "license": "MIT — páginas fictícias do EXP-023 e do EXP-024",
            "artifact_sha256": artifact_sha,
            "cases": cases,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    (ART / "parity-v2.json").write_text(body, encoding="utf-8", newline="\n")
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    (ART / "parity-v2.sha256").write_text(sha + "\n", encoding="utf-8", newline="\n")
    print(f"{len(cases)} casos; {len(body) / 1e6:.2f} MB; sha256 {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
