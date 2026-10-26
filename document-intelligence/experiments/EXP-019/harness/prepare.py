"""EXP-019, T001: páginas de teste do BRESSAY degradadas como fotos (níveis do EXP-002).

Usa ``experiments/EXP-002/harness/pages/degrade.py`` sem alteração, com semente fixa por página e
nível. Saída fora do Git: ``dataset/processed/exp-019/<nível>/<id>.jpg``, manifestos do worker e
cópia das referências de texto (o texto da página não muda com a degradação).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "EXP-002" / "harness" / "pages"))
from degrade import degrade  # noqa: E402

SOURCE = ROOT / "dataset" / "processed" / "exp-017"
OUT = ROOT / "dataset" / "processed" / "exp-019"
LEVELS = ("light", "strong")


def page_seed(page_id: str, level: str) -> int:
    """Semente estável por página e nível (não depende da ordem nem do Python)."""
    return int(hashlib.sha256(f"exp-019/{level}/{page_id}".encode()).hexdigest()[:8], 16)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    pages = json.loads((SOURCE / "test-bressay-worker.json").read_text(encoding="utf-8"))["pages"]
    refs = (SOURCE / "test-bressay-refs.json").read_text(encoding="utf-8")
    for level in LEVELS:
        target = OUT / level
        target.mkdir(parents=True, exist_ok=True)
        manifest = []
        for page in pages:
            image = Image.open(ROOT / page["image"]).convert("RGB")
            result = degrade(image, level, page_seed(page["id"], level))
            path = target / f"{page['id']}{result.extension}"
            path.write_bytes(result.image_bytes)
            manifest.append(
                {
                    "id": page["id"],
                    "image": path.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(result.image_bytes).hexdigest(),
                    "width": result.size[0],
                    "height": result.size[1],
                }
            )
        name = f"test-bressay-{level}"
        (OUT / f"{name}-worker.json").write_text(
            json.dumps({"pages": manifest}, ensure_ascii=False), encoding="utf-8"
        )
        (OUT / f"{name}-refs.json").write_text(refs, encoding="utf-8")
        print(name, len(manifest), "páginas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
