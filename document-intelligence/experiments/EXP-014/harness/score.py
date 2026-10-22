"""CER/WER de um arquivo de predições do EXP-014 (ambiente do harness, com ``leitorum_di``).

Uso: ``uv run --frozen --project experiments/EXP-002/envs/harness python
experiments/EXP-014/harness/score.py <predições.json> [<conjunto>]``. Só números na saída.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "EXP-009" / "harness"))
from evaluate import line_metrics  # noqa: E402

DATA = ROOT / "dataset" / "processed" / "exp-014"


def score(predictions_path: Path) -> dict:
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    items = json.loads((DATA / f"{predictions['set']}.json").read_text(encoding="utf-8"))
    refs = {it["id"]: it["text"] for it in items if it["id"] in predictions["items"]}
    metrics = line_metrics(refs, predictions["items"])
    metrics["ms_per_line"] = predictions.get("ms_per_line")
    metrics["checkpoint"] = predictions.get("checkpoint")
    return metrics


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    metrics = score(Path(sys.argv[1]))
    accents = metrics["cer_by_class"].get("letra acentuada", {}).get("cer")
    print(json.dumps({"lines": metrics["lines"], "cer": round(metrics["cer_micro"], 4),
                      "wer": round(metrics["wer_micro"], 4),
                      "accents": None if accents is None else round(accents, 4)}))  # fmt: skip
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
