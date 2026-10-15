"""Welche Fensterschicht der Körper benutzt: Windows (Win32/GDI, Standard) oder Linux (GTK 3 mit Pillow-Leinwand und X11).

Gewählt wird einmal beim Import über die Umgebungsvariable `BRIDGE_BACKEND` (`windows` oder `linux`). Ohne sie bleibt es Windows, auch wenn der
Code unter Linux läuft: so prüfen die bisherigen Tests weiter das Windows-Verhalten, und nichts wechselt ungewollt. Die Linux-Fassung trägt
dieselben Namen und Aufrufe wie die Windows-Fassung (`Fenster`, `Leinwand`, `Schrift`, `Anwendung`, Menüs, Zwischenablage), damit die Fenster
des Körpers (Raute, Terminal, Chat, Regie, Zeichnen …) für beide dieselbe Zeichen- und Bedienlogik benutzen.
"""

from __future__ import annotations

import os

BACKEND = "linux" if os.environ.get("BRIDGE_BACKEND", "windows").strip().lower() == "linux" else "windows"


def ist_linux() -> bool:
    return BACKEND == "linux"
