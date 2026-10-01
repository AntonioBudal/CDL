"""Medição de memória de processos (o próprio ou um filho) sem dependências externas."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_PROCESS_VM_READ = 0x0010


def _win_api():
    import ctypes
    from ctypes import wintypes

    class Counters(ctypes.Structure):
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

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("dwLength", wintypes.DWORD),
            ("dwMemoryLoad", wintypes.DWORD),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    kernel32.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MemoryStatus)]
    kernel32.GlobalMemoryStatusEx.restype = wintypes.BOOL
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(Counters),
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    return ctypes, kernel32, psapi, Counters, MemoryStatus


class ProcessMemoryProbe:
    """Lê o pico de RSS (working set) de um processo identificado pelo PID.

    No Windows mantém um handle aberto, de modo que o pico continua legível depois que o
    processo termina. Em Linux lê ``VmHWM`` de ``/proc``; após o término devolve o último
    valor observado. Em qualquer falha devolve ``None`` em vez de lançar exceção.
    """

    def __init__(self, pid: int | None = None) -> None:
        self.pid = os.getpid() if pid is None else pid
        self._handle = None
        self._last: int | None = None
        if sys.platform == "win32":
            try:
                _, kernel32, _, _, _ = _win_api()
                access = _PROCESS_QUERY_LIMITED_INFORMATION | _PROCESS_VM_READ
                self._handle = kernel32.OpenProcess(access, False, self.pid) or None
            except Exception:
                self._handle = None

    def _read(self) -> int | None:
        try:
            if sys.platform == "win32":
                if self._handle is None:
                    return None
                ctypes, _, psapi, counters_type, _ = _win_api()
                counters = counters_type()
                counters.cb = ctypes.sizeof(counters_type)
                ok = psapi.GetProcessMemoryInfo(self._handle, ctypes.byref(counters), counters.cb)
                return int(counters.PeakWorkingSetSize) if ok else None

            status = Path(f"/proc/{self.pid}/status")
            if status.exists():
                for line in status.read_text(encoding="utf-8").splitlines():
                    if line.startswith("VmHWM:"):
                        return int(line.split()[1]) * 1024
        except Exception:
            return None
        return None

    def peak_rss_bytes(self) -> int | None:
        """Maior pico observado até agora, em bytes (``None`` se nunca foi possível medir)."""
        value = self._read()
        if value is not None:
            self._last = value if self._last is None else max(self._last, value)
        return self._last

    def close(self) -> None:
        if self._handle is not None:
            try:
                _, kernel32, _, _, _ = _win_api()
                kernel32.CloseHandle(self._handle)
            finally:
                self._handle = None

    def __enter__(self) -> ProcessMemoryProbe:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def available_system_memory_bytes() -> int | None:
    """Memória física livre do sistema em bytes, ou ``None`` se não for possível medir."""
    try:
        if sys.platform == "win32":
            ctypes, kernel32, _, _, status_type = _win_api()
            status = status_type()
            status.dwLength = ctypes.sizeof(status_type)
            ok = kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
            return int(status.ullAvailPhys) if ok else None

        meminfo = Path("/proc/meminfo")
        if meminfo.exists():
            for line in meminfo.read_text(encoding="utf-8").splitlines():
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
    except Exception:
        return None
    return None
