"""G01-Probe: Kann dieses Windows-Python eine ConPTY-Sitzung besitzen?

Die Probe startet `cmd.exe /c echo ...` in einer Pseudokonsole, liest den rohen VT-Strom
zurück und meldet Exit-Code und Bytes. Sie ändert nichts am System und sendet nichts ins Netz.
Ergebnis auf stdout als eine JSON-Zeile.
"""

from __future__ import annotations

import ctypes
import json
import os
import sys
import time
from ctypes import wintypes

MARKER = "BRIDGE-CONPTY-OK"
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
PROC_THREAD_ATTRIBUTE_PSEUDOCONSOLE = 0x00020016
INFINITE = 0xFFFFFFFF


class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.c_void_p),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class STARTUPINFOEXW(ctypes.Structure):
    _fields_ = [("StartupInfo", STARTUPINFOW), ("lpAttributeList", ctypes.c_void_p)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


def probe() -> dict:
    if os.name != "nt":
        return {"status": "unavailable", "reason": "not_windows"}
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    if not hasattr(k32, "CreatePseudoConsole"):
        return {"status": "unavailable", "reason": "CreatePseudoConsole_missing"}

    k32.CreatePipe.argtypes = [ctypes.POINTER(wintypes.HANDLE), ctypes.POINTER(wintypes.HANDLE), ctypes.c_void_p, wintypes.DWORD]
    k32.CreatePipe.restype = wintypes.BOOL
    k32.CreatePseudoConsole.argtypes = [COORD, wintypes.HANDLE, wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p)]
    k32.CreatePseudoConsole.restype = ctypes.c_long
    k32.ClosePseudoConsole.argtypes = [ctypes.c_void_p]
    k32.InitializeProcThreadAttributeList.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.c_size_t)]
    k32.InitializeProcThreadAttributeList.restype = wintypes.BOOL
    k32.UpdateProcThreadAttribute.argtypes = [ctypes.c_void_p, wintypes.DWORD, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p]
    k32.UpdateProcThreadAttribute.restype = wintypes.BOOL
    k32.CreateProcessW.argtypes = [
        wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, wintypes.BOOL, wintypes.DWORD,
        ctypes.c_void_p, wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFOEXW), ctypes.POINTER(PROCESS_INFORMATION),
    ]
    k32.CreateProcessW.restype = wintypes.BOOL
    k32.ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
    k32.ReadFile.restype = wintypes.BOOL
    k32.PeekNamedPipe.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p, ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p]
    k32.PeekNamedPipe.restype = wintypes.BOOL
    k32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k32.WaitForSingleObject.restype = wintypes.DWORD
    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k32.GetExitCodeProcess.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = [wintypes.HANDLE]

    in_read, in_write = wintypes.HANDLE(), wintypes.HANDLE()
    out_read, out_write = wintypes.HANDLE(), wintypes.HANDLE()
    if not k32.CreatePipe(ctypes.byref(in_read), ctypes.byref(in_write), None, 0):
        return {"status": "failed", "step": "CreatePipe_in", "error": ctypes.get_last_error()}
    if not k32.CreatePipe(ctypes.byref(out_read), ctypes.byref(out_write), None, 0):
        return {"status": "failed", "step": "CreatePipe_out", "error": ctypes.get_last_error()}

    hpc = ctypes.c_void_p()
    hr = k32.CreatePseudoConsole(COORD(100, 30), in_read, out_write, 0, ctypes.byref(hpc))
    if hr != 0:
        return {"status": "failed", "step": "CreatePseudoConsole", "hresult": hr & 0xFFFFFFFF}

    size = ctypes.c_size_t(0)
    k32.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
    attr_buf = ctypes.create_string_buffer(size.value)
    if not k32.InitializeProcThreadAttributeList(attr_buf, 1, 0, ctypes.byref(size)):
        return {"status": "failed", "step": "InitializeProcThreadAttributeList", "error": ctypes.get_last_error()}
    if not k32.UpdateProcThreadAttribute(attr_buf, 0, PROC_THREAD_ATTRIBUTE_PSEUDOCONSOLE, hpc, ctypes.sizeof(ctypes.c_void_p), None, None):
        return {"status": "failed", "step": "UpdateProcThreadAttribute", "error": ctypes.get_last_error()}

    si = STARTUPINFOEXW()
    si.StartupInfo.cb = ctypes.sizeof(STARTUPINFOEXW)
    si.lpAttributeList = ctypes.cast(attr_buf, ctypes.c_void_p)
    pi = PROCESS_INFORMATION()
    cmdline = ctypes.create_unicode_buffer(f"cmd.exe /c echo {MARKER}")
    if not k32.CreateProcessW(None, cmdline, None, None, False, EXTENDED_STARTUPINFO_PRESENT, None, None, ctypes.byref(si), ctypes.byref(pi)):
        return {"status": "failed", "step": "CreateProcessW", "error": ctypes.get_last_error()}

    k32.CloseHandle(in_read)
    k32.CloseHandle(out_write)

    collected = b""
    deadline = time.time() + 15.0
    exited = False
    while time.time() < deadline:
        available = wintypes.DWORD(0)
        if k32.PeekNamedPipe(out_read, None, 0, None, ctypes.byref(available), None) and available.value:
            buf = ctypes.create_string_buffer(available.value)
            got = wintypes.DWORD(0)
            if k32.ReadFile(out_read, buf, available.value, ctypes.byref(got), None):
                collected += buf.raw[: got.value]
        if k32.WaitForSingleObject(pi.hProcess, 0) == 0:
            exited = True
            time.sleep(0.4)
            available = wintypes.DWORD(0)
            if k32.PeekNamedPipe(out_read, None, 0, None, ctypes.byref(available), None) and available.value:
                buf = ctypes.create_string_buffer(available.value)
                got = wintypes.DWORD(0)
                if k32.ReadFile(out_read, buf, available.value, ctypes.byref(got), None):
                    collected += buf.raw[: got.value]
            break
        time.sleep(0.05)

    code = wintypes.DWORD(999)
    k32.GetExitCodeProcess(pi.hProcess, ctypes.byref(code))
    k32.ClosePseudoConsole(hpc)
    text = collected.decode("utf-8", "replace")
    return {
        "status": "ok" if MARKER in text and exited else "partial",
        "marker_in_stream": MARKER in text,
        "process_exited": exited,
        "exit_code": int(code.value),
        "bytes": len(collected),
        "vt_escape_bytes": collected.count(b"\x1b"),
        "sample": text[:200],
    }


if __name__ == "__main__":
    print(json.dumps(probe(), ensure_ascii=False))
    sys.stdout.flush()
