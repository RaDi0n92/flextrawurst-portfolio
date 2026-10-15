"""Read-only Windows virtual-screen capture for paired scanner witnesses.

The capture is deliberately separate from the Win32 window inventory. A
scanner result is only valid when the caller supplies the frame reference and
hash produced here. No input, window binding, OCR, or network publishing is
performed by this module.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
import hashlib
import os
import time
from typing import Protocol

from .windows_scanner import Rect


MAX_CAPTURE_PIXELS = 16_000_000
SRCCOPY = 0x00CC0020
CAPTUREBLT = 0x40000000  # ohne dieses Bit fehlen Layered Windows (Raute, Banner, Ticker, Chat) im Bild
DIB_RGB_COLORS = 0
BI_RGB = 0


@dataclass(frozen=True)
class CapturedFrame:
    frame_ref: str
    frame_hash: str
    captured_at_ms: int
    width: int
    height: int
    bgra_bytes: bytes


class CaptureApi(Protocol):
    def virtual_screen_rect(self) -> Rect: ...

    def capture_bgra(self, rect: Rect) -> bytes: ...


class _BitmapInfoHeader(ctypes.Structure):
    _fields_ = [
        ("biSize", ctypes.c_uint32),
        ("biWidth", ctypes.c_int32),
        ("biHeight", ctypes.c_int32),
        ("biPlanes", ctypes.c_uint16),
        ("biBitCount", ctypes.c_uint16),
        ("biCompression", ctypes.c_uint32),
        ("biSizeImage", ctypes.c_uint32),
        ("biXPelsPerMeter", ctypes.c_int32),
        ("biYPelsPerMeter", ctypes.c_int32),
        ("biClrUsed", ctypes.c_uint32),
        ("biClrImportant", ctypes.c_uint32),
    ]


class _RgbQuad(ctypes.Structure):
    _fields_ = [
        ("rgbBlue", ctypes.c_ubyte),
        ("rgbGreen", ctypes.c_ubyte),
        ("rgbRed", ctypes.c_ubyte),
        ("rgbReserved", ctypes.c_ubyte),
    ]


class _BitmapInfo(ctypes.Structure):
    _fields_ = [("bmiHeader", _BitmapInfoHeader), ("bmiColors", _RgbQuad)]


class Win32CaptureApi:
    """Minimal GDI capture of the complete virtual screen."""

    def __init__(self) -> None:
        if os.name != "nt":
            raise RuntimeError("windows_capture_requires_windows")
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
        handle = ctypes.c_void_p
        self.user32.GetDC.argtypes = [handle]
        self.user32.GetDC.restype = handle
        self.user32.ReleaseDC.argtypes = [handle, handle]
        self.user32.ReleaseDC.restype = ctypes.c_int
        self.user32.GetSystemMetrics.argtypes = [ctypes.c_int]
        self.user32.GetSystemMetrics.restype = ctypes.c_int
        self.gdi32.CreateCompatibleDC.argtypes = [handle]
        self.gdi32.CreateCompatibleDC.restype = handle
        self.gdi32.CreateCompatibleBitmap.argtypes = [handle, ctypes.c_int, ctypes.c_int]
        self.gdi32.CreateCompatibleBitmap.restype = handle
        self.gdi32.SelectObject.argtypes = [handle, handle]
        self.gdi32.SelectObject.restype = handle
        self.gdi32.BitBlt.argtypes = [
            handle,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            handle,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint32,
        ]
        self.gdi32.BitBlt.restype = ctypes.c_int
        self.gdi32.GetDIBits.argtypes = [
            handle,
            handle,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.POINTER(_BitmapInfo),
            ctypes.c_uint,
        ]
        self.gdi32.GetDIBits.restype = ctypes.c_int
        self.gdi32.DeleteObject.argtypes = [handle]
        self.gdi32.DeleteObject.restype = ctypes.c_int
        self.gdi32.DeleteDC.argtypes = [handle]
        self.gdi32.DeleteDC.restype = ctypes.c_int

    def virtual_screen_rect(self) -> Rect:
        x = int(self.user32.GetSystemMetrics(76))
        y = int(self.user32.GetSystemMetrics(77))
        width = int(self.user32.GetSystemMetrics(78))
        height = int(self.user32.GetSystemMetrics(79))
        return (x, y, x + width, y + height)

    def capture_bgra(self, rect: Rect) -> bytes:
        left, top, right, bottom = rect
        width, height = right - left, bottom - top
        if width <= 0 or height <= 0 or width * height > MAX_CAPTURE_PIXELS:
            raise ValueError("invalid_or_oversized_virtual_screen")
        screen = self.user32.GetDC(ctypes.c_void_p())
        if not screen:
            raise ctypes.WinError(ctypes.get_last_error())
        memory = ctypes.c_void_p()
        bitmap = ctypes.c_void_p()
        previous = ctypes.c_void_p()
        try:
            memory = self.gdi32.CreateCompatibleDC(screen)
            bitmap = self.gdi32.CreateCompatibleBitmap(screen, width, height)
            if not memory or not bitmap:
                raise ctypes.WinError(ctypes.get_last_error())
            previous = self.gdi32.SelectObject(memory, bitmap)
            if not previous:
                raise ctypes.WinError(ctypes.get_last_error())
            if not self.gdi32.BitBlt(memory, 0, 0, width, height, screen, left, top, SRCCOPY | CAPTUREBLT):
                raise ctypes.WinError(ctypes.get_last_error())
            info = _BitmapInfo()
            info.bmiHeader.biSize = ctypes.sizeof(_BitmapInfoHeader)
            info.bmiHeader.biWidth = width
            info.bmiHeader.biHeight = -height  # top-down, no post-flip ambiguity
            info.bmiHeader.biPlanes = 1
            info.bmiHeader.biBitCount = 32
            info.bmiHeader.biCompression = BI_RGB
            buffer = (ctypes.c_ubyte * (width * height * 4))()
            rows = self.gdi32.GetDIBits(
                memory,
                bitmap,
                0,
                height,
                ctypes.cast(buffer, ctypes.c_void_p),
                ctypes.byref(info),
                DIB_RGB_COLORS,
            )
            if rows != height:
                raise ctypes.WinError(ctypes.get_last_error())
            return bytes(buffer)
        finally:
            if memory and previous:
                self.gdi32.SelectObject(memory, previous)
            if bitmap:
                self.gdi32.DeleteObject(bitmap)
            if memory:
                self.gdi32.DeleteDC(memory)
            self.user32.ReleaseDC(ctypes.c_void_p(), screen)


class WindowsScreenCapture:
    """Create one bounded frame witness for the Windows scanner."""

    def __init__(self, api: CaptureApi | None = None, *, ort: str = "windows") -> None:
        self.api = api if api is not None else (Win32CaptureApi() if os.name == "nt" else None)
        self.ort = ort  # Kennung des Arbeitsplatzes im Frame-Verweis (Vorgabe Windows; Linux z. B. kde1)

    @property
    def available(self) -> bool:
        return self.api is not None

    def capture(self, *, captured_at_ms: int | None = None) -> CapturedFrame:
        if self.api is None:
            raise RuntimeError("windows_capture_unavailable")
        rect = self.api.virtual_screen_rect()
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        if width <= 0 or height <= 0:
            raise ValueError("invalid_virtual_screen_rect")
        if width * height > MAX_CAPTURE_PIXELS:
            raise ValueError("virtual_screen_too_large")
        raw = self.api.capture_bgra(rect)
        expected = width * height * 4
        if len(raw) != expected:
            raise ValueError("capture_byte_length_mismatch")
        captured_at_ms = captured_at_ms if captured_at_ms is not None else int(time.time() * 1000)
        digest = hashlib.sha256(raw).hexdigest()
        return CapturedFrame(
            frame_ref=f"{self.ort}://desktop/{captured_at_ms}-{digest[:16]}",
            frame_hash=f"sha256:{digest}",
            captured_at_ms=captured_at_ms,
            width=width,
            height=height,
            bgra_bytes=raw,
        )
