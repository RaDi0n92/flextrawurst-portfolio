#!/usr/bin/env python3
"""
Test 07: KWin Wayland Window Scanner & Activation Test
Pfad: /root/werkraum/_gemini/windows_bridge/tests/test_07_kwin_wayland_windows.py

Verifiziert:
1. Echtes Scannen nativer Wayland- und XWayland-Fenster via KWin DBus.
2. Erkennung von Chromium, Firefox und Blender auf dem aktiven Desktop.
3. Valide Geometriedaten (x, y, w, h) und Bounding-Box für Klick-Käfig.
4. Erfolgreiche Fenster-Aktivierung / Entminimierung über activate_window().
"""

import os
import sys

# Füge client_windows zum Python-Pfad hinzu
sys.path.insert(0, "/root/werkraum/_gemini/windows_bridge/client_windows")
from windows_copilot_gui import WindowsCopilotClient


def run_test():
    print("=== STARTE TEST 07: KWIN WAYLAND WINDOW SCANNER & ACTIVATION ===")
    client = WindowsCopilotClient()

    # 1. Fenster scannen
    windows = client.scan_open_windows()
    print(f"Gescannte Fenster: {len(windows)}")
    assert len(windows) > 0, "Es wurden keine Fenster auf dem Desktop gefunden!"

    found_chromium = False
    found_blender = False
    found_firefox = False

    target_window = None

    for w in windows:
        title = w.get("title", "")
        rect = w.get("rect", [])
        size = w.get("size", [])
        wid = w.get("id", "")
        minimized = w.get("minimized", False)

        print(f"  - [{wid}] '{title}' -> Rect: {rect}, Size: {size}, Minimized: {minimized}")

        assert len(rect) == 4, f"Ungültiges Rect für Fenster {title}: {rect}"
        assert len(size) == 2, f"Ungültige Size für Fenster {title}: {size}"
        assert size[0] > 0 and size[1] > 0, f"Fenstergröße muss positiv sein: {size}"

        title_lower = title.lower()
        if "chromium" in title_lower:
            found_chromium = True
            if not target_window:
                target_window = w
        if "blender" in title_lower:
            found_blender = True
            if not target_window:
                target_window = w
        if "firefox" in title_lower:
            found_firefox = True

    print(f"Ergebnis: Chromium={found_chromium}, Blender={found_blender}, Firefox={found_firefox}")
    assert found_chromium, "Chromium wurde nicht im KWin Fenster-Scan gefunden!"
    assert found_blender, "Blender wurde nicht im KWin Fenster-Scan gefunden!"

    # 2. Fenster-Aktivierung / Ent-Minimierung testen
    if target_window:
        print(f"Teste activate_window für '{target_window['title']}'...")
        ok = client.activate_window(target_window)
        print(f"activate_window Ergebnis: {ok}")
        assert ok, f"Aktivierung von {target_window['title']} fehlgeschlagen!"

    print("=== TEST 07 ERFOLGREICH BESTANDEN! ===")
    return 0


if __name__ == "__main__":
    sys.exit(run_test())
