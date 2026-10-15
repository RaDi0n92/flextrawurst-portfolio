"""Die Win32-Schicht des Körpers: Typen, Konstanten und Funktionen über ctypes.

Nur hier stehen Aufrufe der Betriebssystem-DLLs. Unter Linux lässt sich das Modul importieren (Strukturen, Konstanten, reine Hilfen);
`WINDOWS` ist dann falsch und die Funktionstabellen `user32`, `gdi32`, `kernel32` sind `None`.
"""

from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes

WINDOWS = sys.platform == "win32"

LRESULT = ctypes.c_ssize_t
HCURSOR = HICON = HBRUSH = HMENU = HINSTANCE = HGDIOBJ = HBITMAP = HDC = HRGN = HFONT = wintypes.HANDLE
COLORREF = wintypes.DWORD

# ---- Nachrichten -------------------------------------------------------------------------------------------------------
WM_CREATE, WM_DESTROY, WM_MOVE, WM_SIZE, WM_ACTIVATE, WM_SETFOCUS, WM_KILLFOCUS = 0x0001, 0x0002, 0x0003, 0x0005, 0x0006, 0x0007, 0x0008
WM_CLOSE, WM_PAINT, WM_ERASEBKGND, WM_NCCALCSIZE, WM_NCHITTEST, WM_SETCURSOR = 0x0010, 0x000F, 0x0014, 0x0083, 0x0084, 0x0020
WM_MOUSEACTIVATE, WM_GETMINMAXINFO, WM_TIMER, WM_HOTKEY = 0x0021, 0x0024, 0x0113, 0x0312
WM_KEYDOWN, WM_KEYUP, WM_CHAR, WM_SYSKEYDOWN, WM_SYSKEYUP, WM_SYSCHAR = 0x0100, 0x0101, 0x0102, 0x0104, 0x0105, 0x0106
WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP, WM_LBUTTONDBLCLK = 0x0200, 0x0201, 0x0202, 0x0203
WM_RBUTTONDOWN, WM_RBUTTONUP, WM_MBUTTONDOWN, WM_MOUSEWHEEL, WM_MOUSELEAVE = 0x0204, 0x0205, 0x0207, 0x020A, 0x02A3
WM_EXITSIZEMOVE, WM_ENTERSIZEMOVE, WM_CAPTURECHANGED, WM_DPICHANGED = 0x0232, 0x0231, 0x0215, 0x02E0
WM_IME_CHAR = 0x0286
WM_APP = 0x8000
WM_QUIT = 0x0012

# ---- Fensterstile ------------------------------------------------------------------------------------------------------
WS_POPUP, WS_VISIBLE, WS_CLIPCHILDREN, WS_THICKFRAME = 0x80000000, 0x10000000, 0x02000000, 0x00040000
WS_EX_TOPMOST, WS_EX_TOOLWINDOW, WS_EX_NOACTIVATE = 0x00000008, 0x00000080, 0x08000000
WS_EX_LAYERED, WS_EX_TRANSPARENT = 0x00080000, 0x00000020
GWL_EXSTYLE, GWL_STYLE = -20, -16
CS_DBLCLKS, CS_HREDRAW, CS_VREDRAW = 0x0008, 0x0002, 0x0001

SW_HIDE, SW_SHOWNORMAL, SW_SHOWNOACTIVATE, SW_SHOWMINNOACTIVE, SW_MINIMIZE, SW_RESTORE, SW_SHOW = 0, 1, 4, 7, 6, 9, 5
HWND_TOPMOST, HWND_NOTOPMOST = -1, -2
SWP_NOSIZE, SWP_NOMOVE, SWP_NOZORDER, SWP_NOACTIVATE, SWP_SHOWWINDOW, SWP_FRAMECHANGED = 0x0001, 0x0002, 0x0004, 0x0010, 0x0040, 0x0020
LWA_ALPHA, LWA_COLORKEY = 0x2, 0x1
WDA_NONE, WDA_MONITOR, WDA_EXCLUDEFROMCAPTURE = 0x0, 0x1, 0x11

# ---- Trefferprüfung ----------------------------------------------------------------------------------------------------
HTCLIENT, HTCAPTION, HTTRANSPARENT, HTNOWHERE = 1, 2, -1, 0
HTLEFT, HTRIGHT, HTTOP, HTTOPLEFT, HTTOPRIGHT, HTBOTTOM, HTBOTTOMLEFT, HTBOTTOMRIGHT = 10, 11, 12, 13, 14, 15, 16, 17
MA_NOACTIVATE, MA_ACTIVATE = 3, 1

# ---- Tasten ------------------------------------------------------------------------------------------------------------
VK_BACK, VK_TAB, VK_RETURN, VK_SHIFT, VK_CONTROL, VK_MENU, VK_ESCAPE = 0x08, 0x09, 0x0D, 0x10, 0x11, 0x12, 0x1B
VK_PRIOR, VK_NEXT, VK_END, VK_HOME, VK_LEFT, VK_UP, VK_RIGHT, VK_DOWN = 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28
VK_INSERT, VK_DELETE, VK_F1, VK_F12, VK_F13, VK_F24 = 0x2D, 0x2E, 0x70, 0x7B, 0x7C, 0x87
MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_NOREPEAT = 0x1, 0x2, 0x4, 0x4000
MOD_WIN = 0x8
VK_LWIN, VK_RWIN = 0x5B, 0x5C

# ---- Menüs, Zwischenablage, sonstiges ----------------------------------------------------------------------------------
MF_STRING, MF_SEPARATOR, MF_CHECKED, MF_GRAYED, MF_POPUP = 0x0, 0x800, 0x8, 0x1, 0x10
TPM_RETURNCMD, TPM_NONOTIFY, TPM_LEFTALIGN, TPM_BOTTOMALIGN, TPM_RIGHTALIGN = 0x100, 0x80, 0x0, 0x20, 0x8
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x2
IDC_ARROW, IDC_IBEAM, IDC_HAND, IDC_SIZEALL = 32512, 32513, 32649, 32646
SM_CXSCREEN, SM_CYSCREEN, SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN = 0, 1, 76, 77, 78, 79
SPI_GETWORKAREA = 0x0030
PM_REMOVE = 0x0001
DPI_AWARENESS_PER_MONITOR_V2 = -4
LOGPIXELSX = 88
MONITOR_DEFAULTTONEAREST = 2

# ---- GDI ---------------------------------------------------------------------------------------------------------------
SRCCOPY = 0x00CC0020
HALFTONE = 4
TRANSPARENT, OPAQUE = 1, 2
DIB_RGB_COLORS, BI_RGB = 0, 0
FW_NORMAL, FW_BOLD = 400, 700
DEFAULT_CHARSET, OUT_TT_PRECIS, CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY = 1, 4, 0, 5
FIXED_PITCH, FF_MODERN, DEFAULT_PITCH, FF_DONTCARE = 1, 0x30, 0, 0
ETO_OPAQUE, ETO_CLIPPED = 0x2, 0x4
ALTERNATE, WINDING = 1, 2
RGN_OR, RGN_DIFF = 2, 4
PS_SOLID, NULL_BRUSH, NULL_PEN = 0, 5, 8
GGI_MARK_NONEXISTING_GLYPHS = 0x0001

# ---- Tastatur-Hook (Not-Aus) ---------------------------------------------------------------------------------------
WH_KEYBOARD_LL = 13
HC_ACTION = 0
LLKHF_INJECTED = 0x10


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class MSG(ctypes.Structure):
    _fields_ = [("hwnd", wintypes.HWND), ("message", wintypes.UINT), ("wParam", wintypes.WPARAM),
                ("lParam", wintypes.LPARAM), ("time", wintypes.DWORD), ("pt", POINT)]


WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM) if WINDOWS else ctypes.CFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM) if WINDOWS else ctypes.CFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)


class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("style", wintypes.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HANDLE),
                ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HANDLE), ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR), ("hIconSm", wintypes.HANDLE)]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [("hdc", wintypes.HANDLE), ("fErase", wintypes.BOOL), ("rcPaint", RECT), ("fRestore", wintypes.BOOL),
                ("fIncUpdate", wintypes.BOOL), ("rgbReserved", ctypes.c_byte * 32)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD), ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD)]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


class TEXTMETRICW(ctypes.Structure):
    _fields_ = [("tmHeight", wintypes.LONG), ("tmAscent", wintypes.LONG), ("tmDescent", wintypes.LONG),
                ("tmInternalLeading", wintypes.LONG), ("tmExternalLeading", wintypes.LONG), ("tmAveCharWidth", wintypes.LONG),
                ("tmMaxCharWidth", wintypes.LONG), ("tmWeight", wintypes.LONG), ("tmOverhang", wintypes.LONG),
                ("tmDigitizedAspectX", wintypes.LONG), ("tmDigitizedAspectY", wintypes.LONG), ("tmFirstChar", wintypes.WCHAR),
                ("tmLastChar", wintypes.WCHAR), ("tmDefaultChar", wintypes.WCHAR), ("tmBreakChar", wintypes.WCHAR),
                ("tmItalic", wintypes.BYTE), ("tmUnderlined", wintypes.BYTE), ("tmStruckOut", wintypes.BYTE),
                ("tmPitchAndFamily", wintypes.BYTE), ("tmCharSet", wintypes.BYTE)]


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD), ("scanCode", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


class SIZE(ctypes.Structure):
    _fields_ = [("cx", wintypes.LONG), ("cy", wintypes.LONG)]


class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [("BlendOp", ctypes.c_ubyte), ("BlendFlags", ctypes.c_ubyte), ("SourceConstantAlpha", ctypes.c_ubyte),
                ("AlphaFormat", ctypes.c_ubyte)]


ULW_ALPHA, AC_SRC_OVER, AC_SRC_ALPHA = 0x2, 0x0, 0x1


class MINMAXINFO(ctypes.Structure):
    _fields_ = [("ptReserved", POINT), ("ptMaxSize", POINT), ("ptMaxPosition", POINT), ("ptMinTrackSize", POINT),
                ("ptMaxTrackSize", POINT)]


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", RECT), ("rcWork", RECT), ("dwFlags", wintypes.DWORD)]


def rgb(r: int, g: int, b: int) -> int:
    """COLORREF (0x00BBGGRR) aus Rot, Grün, Blau."""
    return (r & 0xFF) | ((g & 0xFF) << 8) | ((b & 0xFF) << 16)


def rgb_hex(text: str) -> int:
    text = text.lstrip("#")
    return rgb(int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))


def loword(value: int) -> int:
    return value & 0xFFFF


def hiword(value: int) -> int:
    return (value >> 16) & 0xFFFF


def signed_loword(value: int) -> int:
    v = value & 0xFFFF
    return v - 0x10000 if v & 0x8000 else v


def signed_hiword(value: int) -> int:
    v = (value >> 16) & 0xFFFF
    return v - 0x10000 if v & 0x8000 else v


def make_lparam(x: int, y: int) -> int:
    return (x & 0xFFFF) | ((y & 0xFFFF) << 16)


def _bind(dll, name: str, restype, *argtypes):
    function = getattr(dll, name)
    function.restype = restype
    function.argtypes = list(argtypes)
    return function


class _Table:
    """Namensraum für die gebundenen Funktionen einer DLL; fehlende Funktionen (ältere Windows) ergeben None."""

    def __init__(self, dll):
        self._dll = dll

    def bind(self, name: str, restype, *argtypes):
        try:
            setattr(self, name, _bind(self._dll, name, restype, *argtypes))
        except AttributeError:
            setattr(self, name, None)


user32 = gdi32 = kernel32 = None

if WINDOWS:
    _u = ctypes.WinDLL("user32", use_last_error=True)
    _g = ctypes.WinDLL("gdi32", use_last_error=True)
    _k = ctypes.WinDLL("kernel32", use_last_error=True)
    user32, gdi32, kernel32 = _Table(_u), _Table(_g), _Table(_k)

    H, U, W, L, B, I, D, S = wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM, wintypes.BOOL, ctypes.c_int, wintypes.DWORD, wintypes.LPCWSTR
    HD, HO, HN = wintypes.HANDLE, wintypes.HANDLE, wintypes.HANDLE
    PR, PP = ctypes.POINTER(RECT), ctypes.POINTER(POINT)

    user32.bind("RegisterClassExW", wintypes.ATOM, ctypes.POINTER(WNDCLASSEXW))
    user32.bind("UnregisterClassW", B, S, wintypes.HINSTANCE)
    user32.bind("CreateWindowExW", H, D, S, S, D, I, I, I, I, H, HN, wintypes.HINSTANCE, ctypes.c_void_p)
    user32.bind("DestroyWindow", B, H)
    user32.bind("DefWindowProcW", LRESULT, H, U, W, L)
    user32.bind("ShowWindow", B, H, I)
    user32.bind("SetWindowPos", B, H, H, I, I, I, I, U)
    user32.bind("MoveWindow", B, H, I, I, I, I, B)
    user32.bind("GetWindowRect", B, H, PR)
    user32.bind("GetClientRect", B, H, PR)
    user32.bind("ClientToScreen", B, H, PP)
    user32.bind("ScreenToClient", B, H, PP)
    user32.bind("InvalidateRect", B, H, PR, B)
    user32.bind("BeginPaint", HD, H, ctypes.POINTER(PAINTSTRUCT))
    user32.bind("EndPaint", B, H, ctypes.POINTER(PAINTSTRUCT))
    user32.bind("GetDC", HD, H)
    user32.bind("ReleaseDC", I, H, HD)
    user32.bind("FillRect", I, HD, PR, HN)
    user32.bind("SetLayeredWindowAttributes", B, H, COLORREF, wintypes.BYTE, D)
    user32.bind("GetLayeredWindowAttributes", B, H, ctypes.POINTER(COLORREF), ctypes.POINTER(wintypes.BYTE), ctypes.POINTER(D))
    user32.bind("SetWindowRgn", I, H, HN, B)
    user32.bind("GetMessageW", I, ctypes.POINTER(MSG), H, U, U)
    user32.bind("PeekMessageW", B, ctypes.POINTER(MSG), H, U, U, U)
    user32.bind("TranslateMessage", B, ctypes.POINTER(MSG))
    user32.bind("DispatchMessageW", LRESULT, ctypes.POINTER(MSG))
    user32.bind("PostMessageW", B, H, U, W, L)
    user32.bind("PostQuitMessage", None, I)
    user32.bind("SetTimer", ctypes.c_size_t, H, ctypes.c_size_t, U, ctypes.c_void_p)
    user32.bind("KillTimer", B, H, ctypes.c_size_t)
    user32.bind("SetCapture", H, H)
    user32.bind("ReleaseCapture", B)
    user32.bind("GetCapture", H)
    user32.bind("GetCursorPos", B, PP)
    user32.bind("SetCursor", HN, HN)
    user32.bind("LoadCursorW", HN, wintypes.HINSTANCE, ctypes.c_void_p)
    user32.bind("GetSystemMetrics", I, I)
    user32.bind("SystemParametersInfoW", B, U, U, ctypes.c_void_p, U)
    user32.bind("GetForegroundWindow", H)
    user32.bind("SetForegroundWindow", B, H)
    user32.bind("SetFocus", H, H)
    user32.bind("BringWindowToTop", B, H)
    user32.bind("SwitchToThisWindow", None, H, B)
    user32.bind("GetWindowTextW", I, H, wintypes.LPWSTR, I)
    user32.bind("GetClassNameW", I, H, wintypes.LPWSTR, I)
    user32.bind("AttachThreadInput", B, D, D, B)
    user32.bind("AllowSetForegroundWindow", B, D)
    user32.bind("GetWindowThreadProcessId", D, H, ctypes.POINTER(D))
    user32.bind("GetFocus", H)
    user32.bind("GetKeyState", ctypes.c_short, I)
    user32.bind("GetAsyncKeyState", ctypes.c_short, I)
    user32.bind("RegisterHotKey", B, H, I, U, U)
    user32.bind("UnregisterHotKey", B, H, I)
    user32.bind("WindowFromPoint", H, POINT)
    user32.bind("IsWindow", B, H)
    user32.bind("IsWindowVisible", B, H)
    user32.bind("IsIconic", B, H)
    user32.bind("GetWindowLongPtrW", ctypes.c_ssize_t, H, I)
    user32.bind("SetWindowLongPtrW", ctypes.c_ssize_t, H, I, ctypes.c_ssize_t)
    user32.bind("CreatePopupMenu", HN)
    user32.bind("AppendMenuW", B, HN, U, ctypes.c_size_t, S)
    user32.bind("TrackPopupMenuEx", I, HN, U, I, I, H, ctypes.c_void_p)
    user32.bind("DestroyMenu", B, HN)
    user32.bind("OpenClipboard", B, H)
    user32.bind("CloseClipboard", B)
    user32.bind("EmptyClipboard", B)
    user32.bind("GetClipboardData", HN, U)
    user32.bind("SetClipboardData", HN, U, HN)
    user32.bind("SetProcessDpiAwarenessContext", B, HN)
    user32.bind("GetDpiForWindow", U, H)
    user32.bind("GetDpiForSystem", U)
    user32.bind("UpdateLayeredWindow", B, H, HD, PP, ctypes.POINTER(SIZE), HD, PP, wintypes.DWORD, ctypes.POINTER(BLENDFUNCTION), D)
    user32.bind("SetWindowDisplayAffinity", B, H, D)
    user32.bind("GetWindowDisplayAffinity", B, H, ctypes.POINTER(D))
    user32.bind("MonitorFromPoint", HN, POINT, D)
    user32.bind("MonitorFromWindow", HN, H, D)
    user32.bind("GetMonitorInfoW", B, HN, ctypes.POINTER(MONITORINFO))
    user32.bind("TrackMouseEvent", B, ctypes.c_void_p)
    user32.bind("SetWindowTextW", B, H, S)
    user32.bind("FlashWindow", B, H, B)
    user32.bind("SetWindowsHookExW", HN, I, HOOKPROC, wintypes.HINSTANCE, D)
    user32.bind("CallNextHookEx", LRESULT, HN, I, W, L)
    user32.bind("UnhookWindowsHookEx", B, HN)
    user32.bind("PostThreadMessageW", B, D, U, W, L)
    user32.bind("keybd_event", None, ctypes.c_ubyte, ctypes.c_ubyte, D, ctypes.c_size_t)

    gdi32.bind("CreateCompatibleDC", HD, HD)
    gdi32.bind("DeleteDC", B, HD)
    gdi32.bind("CreateDIBSection", HN, HD, ctypes.POINTER(BITMAPINFO), U, ctypes.POINTER(ctypes.c_void_p), HN, D)
    gdi32.bind("CreateCompatibleBitmap", HN, HD, I, I)
    gdi32.bind("SelectObject", HN, HD, HN)
    gdi32.bind("DeleteObject", B, HN)
    gdi32.bind("GetStockObject", HN, I)
    gdi32.bind("BitBlt", B, HD, I, I, I, I, HD, I, I, D)
    gdi32.bind("StretchDIBits", I, HD, I, I, I, I, I, I, I, I, ctypes.c_void_p, ctypes.POINTER(BITMAPINFO), U, D)
    gdi32.bind("SetStretchBltMode", I, HD, I)
    gdi32.bind("CreateSolidBrush", HN, COLORREF)
    gdi32.bind("CreatePen", HN, I, I, COLORREF)
    gdi32.bind("SetTextColor", COLORREF, HD, COLORREF)
    gdi32.bind("SetBkColor", COLORREF, HD, COLORREF)
    gdi32.bind("SetBkMode", I, HD, I)
    gdi32.bind("ExtTextOutW", B, HD, I, I, U, PR, S, U, ctypes.POINTER(I))
    gdi32.bind("TextOutW", B, HD, I, I, S, I)
    gdi32.bind("CreateFontW", HN, I, I, I, I, I, D, D, D, D, D, D, D, D, S)
    gdi32.bind("GetTextMetricsW", B, HD, ctypes.POINTER(TEXTMETRICW))
    gdi32.bind("GetTextExtentPoint32W", B, HD, S, I, ctypes.POINTER(SIZE))
    gdi32.bind("CreatePolygonRgn", HN, PP, I, I)
    gdi32.bind("CreateRectRgn", HN, I, I, I, I)
    gdi32.bind("CreateRoundRectRgn", HN, I, I, I, I, I, I)
    gdi32.bind("CombineRgn", I, HN, HN, HN, I)
    gdi32.bind("Polygon", B, HD, PP, I)
    gdi32.bind("Rectangle", B, HD, I, I, I, I)
    gdi32.bind("MoveToEx", B, HD, I, I, PP)
    gdi32.bind("LineTo", B, HD, I, I)
    gdi32.bind("GetDeviceCaps", I, HD, I)
    gdi32.bind("GetTextFaceW", I, HD, I, ctypes.c_wchar_p)
    gdi32.bind("GetGlyphIndicesW", D, HD, S, I, ctypes.POINTER(wintypes.WORD), D)
    gdi32.bind("GdiFlush", B)

    kernel32.bind("GetModuleHandleW", wintypes.HINSTANCE, S)
    kernel32.bind("GlobalAlloc", HN, U, ctypes.c_size_t)
    kernel32.bind("GlobalLock", ctypes.c_void_p, HN)
    kernel32.bind("GlobalUnlock", B, HN)
    kernel32.bind("GlobalSize", ctypes.c_size_t, HN)
    kernel32.bind("GetCurrentThreadId", D)
    kernel32.bind("GetTickCount64", ctypes.c_ulonglong)


def require_windows() -> None:
    from .plattform import ist_linux

    if not WINDOWS and not ist_linux():  # die Linux-Fassung (BRIDGE_BACKEND=linux) ersetzt die Windows-Aufrufe durch win32_linux
        raise RuntimeError("win32_required")


def last_error() -> int:
    return ctypes.get_last_error() if WINDOWS else 0


def _linux_einhaengen() -> None:
    """Mit BRIDGE_BACKEND=linux stehen unter `user32`, `gdi32`, `kernel32` die Linux-Fassungen (win32_linux.py)."""
    global user32, gdi32, kernel32
    from .plattform import ist_linux

    if ist_linux():
        from . import win32_linux

        user32, gdi32, kernel32 = win32_linux.user32, win32_linux.gdi32, win32_linux.kernel32


_linux_einhaengen()
