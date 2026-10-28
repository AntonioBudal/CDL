"""EXP-025, F03 (H4): latência por página do v1 e do v2, com repetições intercaladas.

A medida da ``evaluate.py`` roda cada modelo uma vez, em sequência, e é sensível ao ruído da
máquina. Aqui cada página é organizada 5 vezes por modelo, alternando v1 e v2, e o p95 sai de todas
as medidas.
A latência não depende dos rótulos: repetir a medida não contamina o teste.

Mede também o custo direto das 4 pistas novas (``organizer_v2.cue_values``) em todas as unidades das
páginas, a parte do v2 que o v1 não executa.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPS = HERE.parents[1]
for path in (HERE, EXPS / "EXP-023" / "harness"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
sys.path.append(str(EXPS / "EXP-024" / "harness"))

import organizer as org  # noqa: E402
import organizer_v2 as v2  # noqa: E402
import pages  # noqa: E402

V1 = EXPS / "EXP-023" / "artifacts" / "organizer-v1.json"
NOISE = EXPS.parent / "dataset" / "processed" / "exp-023" / "noise-model.json"
REPS = 5


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    return round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))], 2)


def cue_cost(engine, noise) -> dict:
    texts = []
    for page in pages.build_pages()["test"]:
        text, _gold, _units = pages.page_text(pages.with_noise(page, noise, 0.0))
        texts.append([u.text for u in engine.analyse(text, None)[0]])
    units = sum(len(t) for t in texts)
    t0 = time.perf_counter()
    for _ in range(100):
        for unit_texts in texts:
            for text in unit_texts:
                v2.cue_values(text)
    total_ms = (time.perf_counter() - t0) * 1000 / 100
    return {
        "pages": len(texts),
        "units": units,
        "ms_per_page": round(total_ms / len(texts), 4),
        "us_per_unit": round(total_ms * 1000 / units, 2),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    engines = {
        "v1": org.Organizer(org.Model.from_json(json.loads(V1.read_text(encoding="utf-8")))),
        "v2": v2.load(),
    }
    noise = json.loads(NOISE.read_text(encoding="utf-8"))
    out = {}
    for cer in (0.0, 0.10, 0.25):
        for geo in (True, False):
            times = {name: [] for name in engines}
            for page in pages.build_pages()["test"]:
                noisy = pages.with_noise(page, noise, cer)
                text, _gold, _units = pages.page_text(noisy)
                layout = pages.layout(noisy) if geo else None
                for _ in range(REPS):
                    for name, engine in engines.items():
                        t0 = time.perf_counter()
                        engine.organize(text, layout)
                        times[name].append((time.perf_counter() - t0) * 1000)
            key = f"cer{int(cer * 100):02d}_{'geo' if geo else 'sem_geo'}"
            out[key] = {name: p95(v) for name, v in times.items()}
            out[key]["delta"] = round(out[key]["v2"] - out[key]["v1"], 2)
            print(key, out[key], flush=True)
    out["cue_cost"] = cue_cost(engines["v2"], noise)
    text = json.dumps(out, indent=1)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
