"""Testes da medição de memória de processos (próprio e filho)."""

import subprocess
import sys
import time

from leitorum_di.procmem import ProcessMemoryProbe, available_system_memory_bytes

MIB = 1024 * 1024


def test_probe_of_own_process_is_positive_int_or_none():
    with ProcessMemoryProbe() as probe:
        peak = probe.peak_rss_bytes()
    assert peak is None or (isinstance(peak, int) and peak > 0)


def test_probe_sees_allocation_of_child_process_even_after_exit():
    # No Windows o python.exe de um venv é um lançador: o interpretador real é outro processo.
    # Por isso o filho informa o próprio PID, que é o que deve ser medido.
    code = (
        "import os, time; print(os.getpid(), flush=True); "
        "data = bytearray(b'\\x01') * (64 * 1024 * 1024); time.sleep(0.5)"
    )
    child = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
    try:
        with ProcessMemoryProbe(int(child.stdout.readline())) as probe:
            deadline = time.monotonic() + 10
            while child.poll() is None and time.monotonic() < deadline:
                probe.peak_rss_bytes()
                time.sleep(0.02)
            child.wait(timeout=10)
            peak = probe.peak_rss_bytes()
    finally:
        if child.poll() is None:
            child.kill()
    if peak is not None:
        assert peak >= 64 * MIB


def test_probe_of_missing_pid_returns_none():
    with ProcessMemoryProbe(2**22 + 12345) as probe:
        assert probe.peak_rss_bytes() is None


def test_available_system_memory_is_positive_int_or_none():
    free = available_system_memory_bytes()
    assert free is None or (isinstance(free, int) and free > 0)
