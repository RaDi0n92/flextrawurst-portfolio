---
datum: 2026-09-20
autor: codex bei Daniels VPS
herkunft: Greenfield-Bau der Augen-und-Hände-Bridge; isolierte reale Konsole-Probe
status: V3.1 lokal belegt; Windows-ConPTY und laufende Original-Sessions offen
---

# V3.1 — tragender Terminalkanal

## Zweck

Der erste echte Terminalbaustein des Greenfield-Neubaus ist jetzt ein eigener
Terminalkanal. Er ist weder eine Homepage noch eine neue Surface und auch kein
Textfeld, das nur wie ein Terminal aussieht. Der Kanal trennt Transport,
native Präsentation und Audit-Rücklese.

Die alte Oberfläche unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/reference_surface.py`
und der eingefrorene Gemini-Prototyp unter
`/root/werkraum/_gemini/windows_bridge/` wurden dafür nicht umgebaut.

## Der erzwungene Beweisweg

Jeder Kanal muss diese Reihenfolge einhalten:

```text
session_owned
→ pty_connected
→ vt_output_received
→ rendered
→ input_accepted
→ input_delivered
→ input_echoed
→ state_observed
→ audited
```

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_channel.py`
blockiert bei falscher Reihenfolge, fehlender Evidenz oder einem bereits
beendeten Kanal. Für die Zustände sind konkrete Belege erforderlich: Besitzer,
Transport, Byteanzahl, Präsentationsquelle, Request-ID, Zustellmethode,
Marker, Capture-Methode und Audit-Sequenz.

## Was real angeschlossen ist

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py`
besitzt ein isoliertes Konsole-Fenster und eine eigene PTY-Shell. Die rohen
PTY-Bytes werden jetzt gleichzeitig an zwei getrennte Zeugen gegeben:

- an die native Konsole-Präsentation, damit der sichtbare Terminalzustand
  erhalten bleibt;
- an den Bridge-Controller über den Unix-Socket, damit die Bridge echtes VT-
  Output lesen und ein Marker-Echo unabhängig von der Konsole-Rücklese prüfen
  kann.

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py`
führt die Probe nur nach Session-/PTY-/Output-/Präsentationsnachweis aus. Die
Eingabe bleibt absichtlich ein ungefährlicher `printf`-Marker. Anschließend
müssen sowohl rohe PTY-Bytes als auch der sichtbare Konsole-Scrollback denselben
Marker enthalten.

## Nachweis

Der vollständige Bericht liegt unter
`/root/werkraum/augen_haende_bridge/tests/evidence/V3_1_TERMINAL_CHANNEL_EVIDENCE.md`.
Die browserbedienbare Beweisoberfläche zeigt den Kanalstatus und den nächsten
erwarteten Zustand, bleibt aber ein äußerer Zeuge. Sie ersetzt keinen nativen
Windows-Beleg.

## Grenzen

- Das ist ein isolierter, besitzbarer Linux-/Konsole-/PTY-Probeweg. Er ist
  kein Zugriff auf Daniels laufende Codex-, Claude- oder Gemini-Sessions.
- Der Windows-ConPTY-Adapter existiert noch nicht als abgenommener Pfad.
- ANSI-/VT-Bytes werden transportiert und beobachtet; ein eigener Bridge-
  Renderer mit vollständigem Cursor-, Alternate-Screen-, Resize- und Unicode-
  Readback ist der nächste Terminalbaustein.
- `rendered` bedeutet hier native Konsole-Rücklese über
  `getAllDisplayedText`; es ist kein Windows-Screenshot und kein Beweis für
  ein fertiges Overlay.
- Die native Windows-EXE, der native Fensterscanner und die Bindung an
  Windows/KDE-Desktop 1/2 bleiben offen.

## Nächster Schritt

Der nächste kleine Stein ist ein echter Terminal-Renderer-/Resize-Vertrag auf
demselben Kanal. Erst danach werden die Ziel-/Fensterscanner-Bindung und das
freie Windows-Overlay darauf gesetzt. ChatGPTs Anti-Terminal bleibt eine
spätere reale Session-Schicht und wird nicht als lokaler Dummy vorgezogen.
