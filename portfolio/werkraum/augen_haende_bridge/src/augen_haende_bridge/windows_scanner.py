"""Read-only Win32 target inventory for the first native scanner slice.

The scanner inventories the complete Windows desktop and visible top-level
windows.  It does not capture pixels, bind agents, inject input, or claim UI
automation.  A caller must provide the paired visual frame reference/hash.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import os
import time
from typing import Protocol

from .contracts import TargetKind, TargetScanItem, TargetScanSnapshot


Rect = tuple[int, int, int, int]


@dataclass(frozen=True)
class WindowInfo:
    hwnd: int
    title: str
    class_name: str
    rect: Rect
    process_id: int | None
    process_path: str | None
    visible: bool = True


class WindowApi(Protocol):
    def virtual_screen_rect(self) -> Rect: ...

    def enumerate_windows(self) -> list[WindowInfo]: ...


class Win32WindowApi:
    """Small ctypes-only read path; construction is Windows-only."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise RuntimeError("win32_scanner_requires_windows")
        from ctypes import wintypes

        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._enum_proc_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        self.user32.GetSystemMetrics.argtypes = [ctypes.c_int]
        self.user32.GetSystemMetrics.restype = ctypes.c_int
        self.user32.EnumWindows.argtypes = [self._enum_proc_type, wintypes.LPARAM]
        self.user32.EnumWindows.restype = wintypes.BOOL
        self.user32.IsWindowVisible.argtypes = [wintypes.HWND]
        self.user32.IsWindowVisible.restype = wintypes.BOOL
        self.user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        self.user32.GetWindowRect.restype = wintypes.BOOL
        self.user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        self.user32.GetWindowTextLengthW.restype = ctypes.c_int
        self.user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.user32.GetWindowTextW.restype = ctypes.c_int
        self.user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
        self.user32.GetClassNameW.restype = ctypes.c_int
        self.user32.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.DWORD),
        ]
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD

        self.kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.kernel32.OpenProcess.restype = wintypes.HANDLE
        self.kernel32.QueryFullProcessImageNameW.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPWSTR,
            ctypes.POINTER(wintypes.DWORD),
        ]
        self.kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL

    def virtual_screen_rect(self) -> Rect:
        metrics = self.user32.GetSystemMetrics
        return (
            int(metrics(76)),  # SM_XVIRTUALSCREEN
            int(metrics(77)),  # SM_YVIRTUALSCREEN
            int(metrics(76)) + int(metrics(78)),  # SM_CXVIRTUALSCREEN
            int(metrics(77)) + int(metrics(79)),  # SM_CYVIRTUALSCREEN
        )

    def enumerate_windows(self) -> list[WindowInfo]:
        from ctypes import wintypes

        windows: list[WindowInfo] = []
        def callback(hwnd: int, _lparam: int) -> bool:
            if not self.user32.IsWindowVisible(hwnd):
                return True
            rect = wintypes.RECT()
            if not self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return True
            title = self._window_text(hwnd)
            class_name = self._class_name(hwnd)
            process_id = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            pid = int(process_id.value) or None
            windows.append(
                WindowInfo(
                    hwnd=int(hwnd),
                    title=title or class_name or f"HWND {int(hwnd)}",
                    class_name=class_name,
                    rect=(int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)),
                    process_id=pid,
                    process_path=self._process_path(pid),
                )
            )
            return True

        if not self.user32.EnumWindows(self._enum_proc_type(callback), 0):
            raise ctypes.WinError(ctypes.get_last_error())
        return windows

    def _window_text(self, hwnd: int) -> str:
        length = int(self.user32.GetWindowTextLengthW(hwnd))
        if length <= 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value

    def _class_name(self, hwnd: int) -> str:
        buffer = ctypes.create_unicode_buffer(256)
        length = int(self.user32.GetClassNameW(hwnd, buffer, len(buffer)))
        return buffer.value[:length]

    def _process_path(self, pid: int | None) -> str | None:
        if not pid:
            return None
        process_query_limited_information = 0x1000
        handle = self.kernel32.OpenProcess(process_query_limited_information, False, pid)
        if not handle:
            return None
        try:
            from ctypes import wintypes

            size = wintypes.DWORD(32768)
            buffer = ctypes.create_unicode_buffer(size.value)
            if self.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                return buffer.value[: size.value]
            return None
        finally:
            self.kernel32.CloseHandle(handle)


class WindowsWindowScanner:
    """Produce a paired desktop/frame inventory without binding or input."""

    def __init__(self, api: WindowApi | None = None, *, host: str = "thinkpad", ort: str = "windows",
                 desktop_label: str = "Windows kompletter Desktop", quelle: str = "win32") -> None:
        """`ort` ist die Kennung dieses Arbeitsplatzes in den Ziel-Ids (`windows:window:123`, auf Linux z. B. `kde1:window:123`); die Vorgaben sind Windows."""
        self.api = api if api is not None else (Win32WindowApi() if os.name == "nt" else None)
        self.host = host
        self.ort = ort
        self.desktop_label = desktop_label
        self.quelle = quelle
        self._linux = ort != "windows"
        self._identity_by_hwnd: dict[int, tuple[int | None, str]] = {}
        self._generation_by_hwnd: dict[int, int] = {}

    @property
    def available(self) -> bool:
        return self.api is not None

    def _generation(self, info: WindowInfo) -> str:
        identity = (info.process_id, info.class_name)
        previous = self._identity_by_hwnd.get(info.hwnd)
        if previous != identity:
            self._generation_by_hwnd[info.hwnd] = self._generation_by_hwnd.get(info.hwnd, 0) + 1
            self._identity_by_hwnd[info.hwnd] = identity
        return f"hwnd:{info.hwnd}:generation:{self._generation_by_hwnd[info.hwnd]}"

    def scan(
        self,
        *,
        frame_ref: str,
        frame_hash: str,
        captured_at_ms: int | None = None,
    ) -> TargetScanSnapshot:
        if not frame_ref or not frame_hash:
            raise ValueError("paired_frame_reference_and_hash_required")
        captured_at_ms = captured_at_ms if captured_at_ms is not None else int(time.time() * 1000)
        if self.api is None:
            desktop = TargetScanItem(
                target_id=f"{self.ort}:desktop",
                generation="desktop:unavailable",
                kind=TargetKind.LINUX_KDE_DESKTOP if self._linux else TargetKind.WINDOWS_DESKTOP,
                label=self.desktop_label,
                host=self.host,
                rect=None,
                visible=True,
                source=f"{self.quelle}.unavailable",
                availability="unavailable",
                capabilities=frozenset(),
            )
            return TargetScanSnapshot(
                scan_id=self._scan_id(captured_at_ms, frame_hash),
                captured_at_ms=captured_at_ms,
                source=f"{self.quelle}.unavailable",
                frame_ref=frame_ref,
                frame_hash=frame_hash,
                default_target_id=desktop.target_id,
                items=(desktop,),
            )

        desktop_rect = self.api.virtual_screen_rect()
        items = [
            TargetScanItem(
                target_id=f"{self.ort}:desktop",
                generation="desktop:virtual-screen",
                kind=TargetKind.LINUX_KDE_DESKTOP if self._linux else TargetKind.WINDOWS_DESKTOP,
                label=self.desktop_label,
                host=self.host,
                rect=desktop_rect,
                visible=True,
                z_order=0,
                virtual_desktop="all-visible",
                source=f"{self.quelle}.window-enum",
                availability="available",
                capabilities=frozenset({"inventory"}),
            )
        ]
        for z_order, info in enumerate(self.api.enumerate_windows(), start=1):
            if not info.visible:
                continue
            title = info.title or info.class_name or f"HWND {info.hwnd}"
            items.append(
                TargetScanItem(
                    target_id=f"{self.ort}:window:{info.hwnd}",
                    generation=self._generation(info),
                    kind=TargetKind.LINUX_WINDOW if self._linux else TargetKind.WINDOWS_WINDOW,
                    label=title,
                    host=self.host,
                    rect=info.rect,
                    visible=True,
                    z_order=z_order,
                    virtual_desktop="unknown",
                    process_id=info.process_id,
                    process_path=info.process_path,
                    source=f"{self.quelle}.window-enum",
                    availability="available",
                    capabilities=frozenset({"inventory"}),
                )
            )
        return TargetScanSnapshot(
            scan_id=self._scan_id(captured_at_ms, frame_hash),
            captured_at_ms=captured_at_ms,
            source=f"{self.quelle}.window-enum",
            frame_ref=frame_ref,
            frame_hash=frame_hash,
            default_target_id=f"{self.ort}:desktop",
            items=tuple(items),
        )

    @staticmethod
    def _scan_id(captured_at_ms: int, frame_hash: str) -> str:
        digest = hashlib.sha256(f"{captured_at_ms}:{frame_hash}".encode("utf-8")).hexdigest()[:16]
        return f"windows-scan:{digest}"
