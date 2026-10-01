"""Testes do benchmark de fundação (tempo, memória, seeds, formato de log)."""

import json
import tempfile
from pathlib import Path

from leitorum_di.benchmark import (
    DEFAULT_FIXTURE,
    SCHEMA,
    current_rss_bytes,
    run_foundation_benchmark,
    write_benchmark_log,
)


def test_benchmark_report_structure():
    report = run_foundation_benchmark()
    fixture = json.loads(DEFAULT_FIXTURE.read_text(encoding="utf-8"))
    assert report["schema"] == SCHEMA
    assert report["seed"]["seed"] == 1234
    assert len(report["samples"]) == len(fixture["samples"])
    assert report["total_ms"] >= 0
    assert report["python_peak_alloc_bytes"] >= 0
    for item in report["samples"]:
        assert item["elapsed_ms"] >= 0
        assert set(item) == {"id", "cer", "wer", "iou", "elapsed_ms"}


def test_benchmark_metrics_are_deterministic_across_runs():
    def strip(report):
        return [{k: v for k, v in s.items() if k != "elapsed_ms"} for s in report["samples"]]

    assert strip(run_foundation_benchmark(seed=7)) == strip(run_foundation_benchmark(seed=7))


def test_rss_is_int_or_none():
    rss = current_rss_bytes()
    assert rss is None or (isinstance(rss, int) and rss > 0)


def test_write_benchmark_log_roundtrip():
    report = run_foundation_benchmark()
    with tempfile.TemporaryDirectory() as tmp:
        out = write_benchmark_log(report, Path(tmp) / "sub" / "bench.json")
        loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["schema"] == SCHEMA
    assert loaded["samples"] == report["samples"]
