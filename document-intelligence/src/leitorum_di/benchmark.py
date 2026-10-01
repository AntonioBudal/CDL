"""Benchmark de fundação (EXP-000): tempo por amostra, memória e seeds sobre fixtures sintéticas.

Uso: ``uv run python -m leitorum_di.benchmark [--out evaluation/benchmark-exp000.json]``
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path

from leitorum_di.metrics.base import calculate_cer, calculate_iou, calculate_wer
from leitorum_di.reproducibility import DEFAULT_SEED, environment_snapshot, freeze_seeds

SCHEMA = "leitorum-di-benchmark/1"
DEFAULT_FIXTURE = (
    Path(__file__).resolve().parents[2] / "dataset" / "fixtures" / "synthetic-line-sample.json"
)


def current_rss_bytes() -> int | None:
    """RSS (working set) do processo em bytes, ou ``None`` se não for possível medir."""
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            class _Counters(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel32.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(_Counters),
                wintypes.DWORD,
            ]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            counters = _Counters()
            counters.cb = ctypes.sizeof(_Counters)
            ok = psapi.GetProcessMemoryInfo(
                kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
            )
            return int(counters.WorkingSetSize) if ok else None

        statm = Path("/proc/self/statm")
        if statm.exists():
            pages = int(statm.read_text(encoding="utf-8").split()[1])
            return pages * os.sysconf("SC_PAGE_SIZE")
    except Exception:
        return None
    return None


def run_foundation_benchmark(
    fixture_path: Path | str = DEFAULT_FIXTURE, seed: int = DEFAULT_SEED
) -> dict[str, object]:
    """Executa CER/WER/IoU sobre a fixture e devolve o relatório (formato ``SCHEMA``)."""
    seed_record = freeze_seeds(seed)
    data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))

    rss_before = current_rss_bytes()
    tracemalloc.start()
    t_total = time.perf_counter_ns()
    samples = []
    for sample in data["samples"]:
        t0 = time.perf_counter_ns()
        cer = calculate_cer(sample["ground_truth"], sample["prediction"])
        wer = calculate_wer(sample["ground_truth"], sample["prediction"])
        iou = calculate_iou(sample["bounding_box_gt"], sample["bounding_box_pred"])
        elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
        samples.append(
            {"id": sample["id"], "cer": cer, "wer": wer, "iou": iou, "elapsed_ms": elapsed_ms}
        )
    total_ms = (time.perf_counter_ns() - t_total) / 1e6
    _, peak_py_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    rss_after = current_rss_bytes()

    return {
        "schema": SCHEMA,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "fixture": Path(fixture_path).name,
        "seed": seed_record,
        "environment": environment_snapshot(),
        "total_ms": total_ms,
        "rss_bytes_before": rss_before,
        "rss_bytes_after": rss_after,
        "python_peak_alloc_bytes": peak_py_bytes,
        "samples": samples,
    }


def write_benchmark_log(report: dict[str, object], path: Path | str) -> Path:
    """Grava o relatório como JSON UTF-8 e devolve o caminho."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark de fundação do EXP-000")
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE))
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", default=None, help="Se omitido, imprime o JSON na saída padrão")
    args = parser.parse_args(argv)

    report = run_foundation_benchmark(args.fixture, args.seed)
    if args.out:
        print(f"Relatório gravado em {write_benchmark_log(report, args.out)}")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
