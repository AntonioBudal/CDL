"""EXP-025, F05 (C-Q2 da feature 091): o adaptador enxuto contra o v2 estático, uma vez no teste.

Fluxos de TESTE do EXP-024 (4 perfis, 40 páginas de adaptação cada), regimes R1 (implícito) e R3
(20 % de páginas ruidosas). O leitor simulado salva cada página; o registro vira
``leitorum-feedback/1`` (sem nota, como no Leitorum) e o adaptador aprende com ele. Dois modos:

- ``raw``: o leitor sempre vê a sugestão do adaptador (o efeito do aprendizado sozinho);
- ``product``: o leitor vê o v2 até 30 páginas revisadas e, dali em diante, o adaptador só se a
  guarda deixar (a regra do produto).

No fim, Macro-F1 por caractere no *holdout* de cada perfil (régua do EXP-023), sem aprender com ele:
v2 estático, adaptador e a escolha do produto. Custos: p95 da atualização e tamanho do estado em 500
estudos. Só números.

Uso:
    uv run --frozen --project experiments/EXP-023/envs/organizer python \\
        experiments/EXP-025/harness/evaluate_adapter.py --out <json>
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import adapter_deps  # noqa: F401  (caminhos)
import adapter_v2 as av
import feedback_doc
import metrics  # EXP-023
import organizer_v2 as v2
import simulator as sim  # EXP-024
import state as st  # EXP-024
import streams  # EXP-024

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts"
PROFILES = ("P1", "P2", "P3", "P4")
REGIMES = ("R1", "R3")
ACTIVATE_AT = 30


def adapter_engine() -> av.AdapterV2:
    return av.AdapterV2(
        v2.load(), (ART / "organizer-v2.sha256").read_text(encoding="utf-8").strip()
    )


def holdout(stream: dict, organize) -> dict:
    scores = metrics.Scores()
    for book, pages in stream["holdout"].items():
        for page in pages:
            text, gold, units = streams.page_text(page)
            scores.add(text, gold, units, organize(text, streams.layout(page), book))
    report = scores.report()
    return {
        "macro_f1": report["macro_f1_chars"],
        "f1_references": report["per_section_chars"]["references"]["f1"],
    }


def run(adapter: av.AdapterV2, profile: str, regime: str, mode: str) -> dict:
    stream = streams.stream(profile, "test")
    plan = sim.noisy_plan(stream["adapt"], regime)
    state = adapter.new_state(f"u-{profile}")
    codes: Counter = Counter()
    times = []
    active_pages = 0

    def product_state():
        return state if state["reviewed"] >= ACTIVATE_AT and adapter.guard_allows(state) else None

    for page in stream["adapt"]:
        seen = {}
        shown = state if mode == "raw" else product_state()
        active_pages += shown is not None

        def organize(text, layout, book, seen=seen, shown=shown):
            seen["result"] = adapter.organize(shown, text, layout, book)
            return seen["result"]

        feedback, _truth = sim.session(page, regime, organize, noisy=plan.get(page["id"]))
        document = feedback_doc.to_document(feedback, seen["result"]["segments"])
        t0 = time.perf_counter()
        codes[adapter.learn(state, document, page["book_id"])] += 1
        times.append((time.perf_counter() - t0) * 1000)
    final_product = product_state()
    return {
        "v2": holdout(stream, lambda t, lay, b: adapter.organize(None, t, lay, b)),
        "adapter": holdout(stream, lambda t, lay, b: adapter.organize(state, t, lay, b)),
        "product": holdout(stream, lambda t, lay, b: adapter.organize(final_product, t, lay, b)),
        "product_uses_adapter": final_product is not None,
        "pages_shown_by_adapter": active_pages,
        "reviewed": state["reviewed"],
        "codes": dict(codes),
        "guard_last20": {
            k: round(statistics.mean(v[-20:]), 4) if v else None for k, v in state["guard"].items()
        },
        "update_ms_p95": round(sorted(times)[int(0.95 * len(times)) - 1], 2),
    }


def costs(adapter: av.AdapterV2, n_studies: int = 500) -> dict:
    """Atualização e tamanho do estado com 500 estudos (adaptação dos 4 perfis, em ciclo)."""
    docs = []
    for profile in PROFILES:
        stream = streams.stream(profile, "test")
        for page in stream["adapt"]:
            seen = {}

            def organize(text, layout, book, seen=seen):
                seen["result"] = adapter.organize(None, text, layout, book)
                return seen["result"]

            feedback, _truth = sim.session(page, "R1", organize)
            docs.append(
                (feedback_doc.to_document(feedback, seen["result"]["segments"]), page["book_id"])
            )
    state = adapter.new_state("u-custo")
    times = []
    for k in range(n_studies):
        doc, book = docs[k % len(docs)]
        t0 = time.perf_counter()
        adapter.learn(state, doc, f"{book}-{k // len(docs)}")
        times.append((time.perf_counter() - t0) * 1000)
    return {
        "studies": n_studies,
        "update_ms_p50": round(statistics.median(times), 2),
        "update_ms_p95": round(sorted(times)[int(0.95 * len(times)) - 1], 2),
        "state_kb": round(st.size_bytes(state) / 1024, 1),
    }


def git() -> dict:
    def out(*args):
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, cwd=HERE
        ).stdout.strip()

    return {
        "commit": out("rev-parse", "--short", "HEAD"),
        "clean": out("status", "--porcelain") == "",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    started = time.time()
    adapter = adapter_engine()
    report = {"experiment": "EXP-025", "phase": "F05", "split": "test", "git": git(), "runs": {}}
    for regime in REGIMES:
        for mode in ("raw", "product"):
            for profile in PROFILES:
                key = f"{regime}-{mode}-{profile}"
                report["runs"][key] = run(adapter, profile, regime, mode)
                r = report["runs"][key]
                print(
                    key,
                    r["v2"]["macro_f1"],
                    r["adapter"]["macro_f1"],
                    r["product"]["macro_f1"],
                    flush=True,
                )
            runs = [report["runs"][f"{regime}-{mode}-{p}"] for p in PROFILES]
            report[f"mean-{regime}-{mode}"] = {
                k: round(statistics.mean(r[k]["macro_f1"] for r in runs), 4)
                for k in ("v2", "adapter", "product")
            }
            print(f"media {regime}-{mode}", report[f"mean-{regime}-{mode}"], flush=True)
    report["costs"] = costs(adapter)
    report["elapsed_s"] = round(time.time() - started, 1)
    text = json.dumps(report, indent=1, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(json.dumps(report["costs"]), report["elapsed_s"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
