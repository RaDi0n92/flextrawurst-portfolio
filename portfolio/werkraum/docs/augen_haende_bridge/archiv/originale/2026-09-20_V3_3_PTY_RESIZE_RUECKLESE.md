---
datum: 2026-09-20
autor: codex bei Daniels VPS
herkunft: V3.1-Terminalkanal und V3.2-VT-Rücklese
status: V3.3 Linux-PTY-Resize mit Kernel-Rücklese belegt; ConPTY offen
---

# V3.3 — PTY-Resize-Roundtrip

## Ergebnis

Das besessene Probe-Terminal kann jetzt kontrolliert auf eine neue Größe
gesetzt werden. Der Resize-Weg läuft über einen separaten Control-Socket und
vermischt seine JSON-Bestätigung nicht mit dem rohen VT-Ausgabestrom.

```text
Resize-Anforderung
  → PTY TIOCSWINSZ
  → Kernel TIOCGWINSZ
  → Control-Ack mit beobachteten rows/cols
  → VTScreenState.resize()
  → sichtbarer Proof-Zustand
```

Implementierung:

- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py`
- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py`
- `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_renderer.py`

Der Live-Proof setzt 40×120 und liest 40×120 aus dem PTY-Kernelzustand zurück.
Die browserbedienbare Proof-Surface zeigt diesen Rücklauf zusätzlich sichtbar
unter `data-testid="terminal-resize"`.

## Sicherheitsgrenze

Der Control-Socket akzeptiert ausschließlich den strukturierten Vorgang
`resize` und begrenzt rows/cols auf 1…1000. Er ist kein allgemeiner Shell-
oder Terminal-Command-Kanal. Der bereits geprüfte sichere `printf`-Marker
bleibt der einzige aktive Eingabeprobe.

## Noch nicht behauptet

Dieser Roundtrip beweist Linux-PTY-Größenänderung, nicht Windows-ConPTY,
KDE-Fenster-Resize, pixelgenaue Font-/DPI-Darstellung oder eine vollständige
SIGWINCH-/Alternate-Screen-Trajektorie. Diese Belege gehören zu späteren
Adaptertests.
