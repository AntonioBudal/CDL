"""Supervisor do benchmark de layout (derivado do EXP-001).

Subprocesso, medição e critérios de parada.

O supervisor nunca importa bibliotecas de modelo. Ele lança ``worker.py`` com o interpretador do
ambiente isolado do candidato, acompanha o pico de memória do processo filho e o encerra se
algum limite de ``plan.md`` for violado.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import queue
import signal
import statistics
import subprocess
import sys
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from leitorum_di.procmem import ProcessMemoryProbe, available_system_memory_bytes

WORKER = Path(__file__).resolve().parent / "worker.py"
PREFIX = "@@EXP002 "
GIB = 1024**3


@dataclass(frozen=True)
class Limits:
    """Critérios de parada (valores padrão de ``plan.md``)."""

    memory_bytes: int = 2 * GIB
    load_timeout_s: float = 120.0
    latency_probe_lines: int = 10  # páginas
    latency_abort_ms: float = 20_000.0
    wall_timeout_s: float = 1800.0
    min_free_system_bytes: int = 1 * GIB
    poll_interval_s: float = 0.05


@dataclass
class RunResult:
    candidate_id: str
    status: str  # OK | ABORTED | REFUSED | SKIPPED | FAILED
    reason: str = ""
    license_status: str = ""
    load_ms: float | None = None
    peak_rss_bytes: int | None = None
    wall_s: float = 0.0
    exit_code: int | None = None
    describe: dict[str, Any] = field(default_factory=dict)
    predictions: list[dict[str, Any]] = field(default_factory=list)
    stderr_tail: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def license_gate(candidate: dict[str, Any]) -> tuple[bool, str]:
    """Decide se o candidato pode ser executado. Reconhecedores de referência não são modelos."""
    if candidate.get("kind") == "reference":
        return True, "reconhecedor de referência (sem modelo)"
    status = candidate.get("license_status", "")
    if candidate.get("benchmark_allowed") is not True:
        return False, f"benchmark não autorizado (LICENSE STATUS: {status or 'ausente'})"
    if status == "VERIFIED":
        return True, "LICENSE STATUS: VERIFIED"
    if status == "NEEDS VALIDATION" and candidate.get("user_exception"):
        return True, "LICENSE STATUS: NEEDS VALIDATION — exceção experimental do usuário"
    return False, f"LICENSE STATUS: {status or 'ausente'} sem exceção do usuário"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_weights(candidate: dict[str, Any], weights_dir: Path) -> list[str]:
    """Confere os arquivos de pesos contra os SHA-256 declarados; devolve a lista de problemas."""
    problems = []
    for name, expected in candidate.get("weights", {}).get("files", {}).items():
        path = Path(weights_dir) / name
        if not path.is_file():
            problems.append(f"{name}: arquivo ausente")
        elif sha256_file(path) != expected["sha256"]:
            problems.append(f"{name}: SHA-256 divergente")
    return problems


def _terminate(proc: subprocess.Popen, worker_pid: int | None) -> None:
    # No Windows o python.exe de um venv pode ser um lançador; o interpretador real é o worker_pid.
    if worker_pid is not None and worker_pid != proc.pid:
        with contextlib.suppress(OSError):
            os.kill(worker_pid, signal.SIGTERM)
    with contextlib.suppress(OSError):
        proc.kill()
    with contextlib.suppress(subprocess.TimeoutExpired):
        proc.wait(timeout=10)


def run_candidate(
    candidate: dict[str, Any],
    manifest_path: Path,
    root: Path,
    python_exe: str | None = None,
    limits: Limits | None = None,
    warmup: int = 2,
    seed: int = 1234,
    weights_dir: Path | None = None,
) -> RunResult:
    """Executa um candidato sobre o manifesto e devolve predições, medições e status."""
    limits = limits or Limits()
    result = RunResult(
        candidate_id=candidate["id"],
        status="OK",
        license_status=candidate.get("license_status", ""),
    )

    allowed, reason = license_gate(candidate)
    if not allowed:
        result.status, result.reason = "REFUSED", reason
        return result
    if weights_dir is not None:
        problems = check_weights(candidate, weights_dir)
        if problems:
            result.status, result.reason = "REFUSED", "pesos não conferem: " + "; ".join(problems)
            return result

    free = available_system_memory_bytes()
    if free is not None and free < limits.min_free_system_bytes:
        result.status = "SKIPPED"
        result.reason = f"memória livre do sistema insuficiente ({free} bytes)"
        return result

    env = dict(os.environ)
    env.update(
        {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "HF_DATASETS_OFFLINE": "1",
        }
    )
    command = [
        python_exe or sys.executable,
        str(WORKER),
        "--adapter",
        candidate["adapter"],
        "--manifest",
        str(manifest_path),
        "--root",
        str(root),
        "--options",
        json.dumps(candidate.get("options", {})),
        "--warmup",
        str(warmup),
        "--seed",
        str(seed),
    ]
    started = time.monotonic()
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(root),
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    events: queue.Queue[str | None] = queue.Queue()
    stderr_tail: deque[str] = deque(maxlen=40)

    def pump_stdout() -> None:
        for line in proc.stdout:
            events.put(line)
        events.put(None)

    def pump_stderr() -> None:
        for line in proc.stderr:
            stderr_tail.append(line.rstrip())

    threads = [
        threading.Thread(target=pump_stdout, daemon=True),
        threading.Thread(target=pump_stderr, daemon=True),
    ]
    for thread in threads:
        thread.start()

    probe: ProcessMemoryProbe | None = None
    worker_pid: int | None = None
    loaded = done = stdout_closed = False
    abort_reason = ""

    def handle(raw: str) -> None:
        nonlocal probe, worker_pid, loaded, done
        if not raw.startswith(PREFIX):
            return  # saída avulsa de bibliotecas; ignorada
        event = json.loads(raw[len(PREFIX) :])
        kind = event["event"]
        if kind == "start":
            worker_pid = event["pid"]
            probe = ProcessMemoryProbe(worker_pid)
        elif kind == "loaded":
            loaded = True
            result.load_ms = event["load_ms"]
            result.describe = event["describe"]
        elif kind == "page":
            result.predictions.append(
                {"id": event["id"], "result": event["result"], "elapsed_ms": event["elapsed_ms"]}
            )
        elif kind == "done":
            done = True

    try:
        while True:
            while True:
                try:
                    raw = events.get_nowait()
                except queue.Empty:
                    break
                if raw is None:
                    stdout_closed = True
                else:
                    handle(raw)

            elapsed = time.monotonic() - started
            peak = probe.peak_rss_bytes() if probe is not None else None
            if peak is not None:
                result.peak_rss_bytes = peak

            if peak is not None and peak > limits.memory_bytes:
                abort_reason = f"memory: pico {peak} bytes > limite {limits.memory_bytes}"
            elif not loaded and elapsed > limits.load_timeout_s:
                abort_reason = f"load timeout: carga > {limits.load_timeout_s} s"
            elif elapsed > limits.wall_timeout_s:
                abort_reason = f"wall time: execução > {limits.wall_timeout_s} s"
            elif len(result.predictions) >= limits.latency_probe_lines and not done:
                probe_lines = result.predictions[: limits.latency_probe_lines]
                median = statistics.median(p["elapsed_ms"] for p in probe_lines)
                if median > limits.latency_abort_ms:
                    abort_reason = (
                        f"latency: mediana {median:.1f} ms nas {limits.latency_probe_lines} "
                        f"primeiras páginas > {limits.latency_abort_ms} ms"
                    )
            if abort_reason:
                _terminate(proc, worker_pid)
                break
            if stdout_closed and proc.poll() is not None:
                break
            time.sleep(limits.poll_interval_s)
    finally:
        if proc.poll() is None:
            _terminate(proc, worker_pid)
        for thread in threads:
            thread.join(timeout=5)
        if probe is not None:
            final_peak = probe.peak_rss_bytes()
            if final_peak is not None:
                result.peak_rss_bytes = final_peak
            probe.close()

    result.wall_s = time.monotonic() - started
    result.exit_code = proc.returncode
    result.stderr_tail = list(stderr_tail)

    if abort_reason:
        result.status, result.reason = "ABORTED", abort_reason
    elif not done:
        result.status = "FAILED"
        result.reason = f"worker terminou sem concluir (código {proc.returncode})"
    elif result.peak_rss_bytes is not None and result.peak_rss_bytes > limits.memory_bytes:
        result.status = "ABORTED"
        result.reason = (
            f"memory: pico {result.peak_rss_bytes} bytes > limite {limits.memory_bytes} "
            "(detectado ao final)"
        )
    else:
        result.reason = reason
    return result
