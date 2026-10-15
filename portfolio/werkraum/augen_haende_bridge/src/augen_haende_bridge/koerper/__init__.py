"""Der erste Körper der Bridge auf Windows: Terminal, Scanner je Terminal, Raute mit Banner, Ticker und Chat, Kamera, Mikrofon.

Kleine schwebende Fenster über dem normalen Desktop, kein Overlay als Fläche (R118). Reines Win32 über ctypes, kein Tk.
Alle Module lassen sich unter Linux importieren; nur ihre Fenster- und Zeichenaufrufe brauchen Windows (oder Wine).
"""
