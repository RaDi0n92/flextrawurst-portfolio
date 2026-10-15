"""Der Windows-Dialog „Datei öffnen“ für Bilder (nur Auswahl, es wird nichts verändert)."""

from __future__ import annotations

import ctypes
import os
from ctypes import wintypes

FILTER = "Bilder (*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp)\0*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp\0Alle Dateien (*.*)\0*.*\0\0"
OFN_FILEMUSTEXIST, OFN_PATHMUSTEXIST, OFN_NOCHANGEDIR, OFN_EXPLORER = 0x1000, 0x800, 0x8, 0x80000


class OPENFILENAMEW(ctypes.Structure):
    _fields_ = [("lStructSize", wintypes.DWORD), ("hwndOwner", wintypes.HWND), ("hInstance", wintypes.HINSTANCE),
                ("lpstrFilter", wintypes.LPCWSTR), ("lpstrCustomFilter", wintypes.LPWSTR), ("nMaxCustFilter", wintypes.DWORD),
                ("nFilterIndex", wintypes.DWORD), ("lpstrFile", wintypes.LPWSTR), ("nMaxFile", wintypes.DWORD),
                ("lpstrFileTitle", wintypes.LPWSTR), ("nMaxFileTitle", wintypes.DWORD), ("lpstrInitialDir", wintypes.LPCWSTR),
                ("lpstrTitle", wintypes.LPCWSTR), ("Flags", wintypes.DWORD), ("nFileOffset", wintypes.WORD),
                ("nFileExtension", wintypes.WORD), ("lpstrDefExt", wintypes.LPCWSTR), ("lCustData", wintypes.LPARAM),
                ("lpfnHook", ctypes.c_void_p), ("lpTemplateName", wintypes.LPCWSTR), ("pvReserved", ctypes.c_void_p),
                ("dwReserved", wintypes.DWORD), ("FlagsEx", wintypes.DWORD)]


def datei_waehlen(hwnd: int, titel: str = "Bild für den Agenten wählen") -> str | None:
    """Pfad der gewählten Datei oder None (Abbruch). Läuft nur unter Windows."""
    if os.name != "nt":
        return None
    puffer = ctypes.create_unicode_buffer(1024)
    info = OPENFILENAMEW()
    info.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    info.hwndOwner = hwnd
    info.lpstrFilter = FILTER
    info.lpstrFile = ctypes.cast(puffer, wintypes.LPWSTR)
    info.nMaxFile = 1024
    info.lpstrTitle = titel
    info.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST | OFN_NOCHANGEDIR | OFN_EXPLORER
    return puffer.value if ctypes.WinDLL("comdlg32").GetOpenFileNameW(ctypes.byref(info)) else None
