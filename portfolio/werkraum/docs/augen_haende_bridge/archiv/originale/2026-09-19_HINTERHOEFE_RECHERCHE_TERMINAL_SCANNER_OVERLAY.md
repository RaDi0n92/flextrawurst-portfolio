# Augen & Hände — Recherche aus den Hinterhöfen des Netzes

## Was wirklich trägt

| Aufgabe | Belastbarer Weg | Grenze |
|---|---|---|
| Echter Terminalbetrieb | Windows **ConPTY**: bidirektionaler UTF‑8-/VT-Strom für Input, Output, Cursor, Farben und Resize | Funktioniert sauber, wenn die Session von uns gestartet wird; eine beliebige bereits laufende Fremd-Session lässt sich nicht universell „magisch“ übernehmen. [Microsoft ConPTY](https://github.com/MicrosoftDocs/Console-Docs/blob/main/docs/creating-a-pseudoconsole-session.md) |
| Terminaldarstellung | VT-Terminalrenderer statt Textfeld; xterm.js kann echte Shell-Prozesse über PTY anbinden und unterstützt u. a. `vim`, `tmux`, Farben, Unicode und Mausereignisse. [xterm.js](https://github.com/xtermjs/xterm.js/) | xterm.js ist nur der Renderer, nicht die Session selbst. |
| Windows-Fensterscanner | `EnumWindows`/Fensterhandles, `GetWindowRect`, Prozessdaten, DPI, Z‑Order plus `SetWinEventHook` für Öffnen, Schließen, Fokus und Größenänderungen. [GetWindowRect](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect), [SetWinEventHook](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook) | Ein HWND darf nicht allein die dauerhafte Identität sein; wir brauchen zusätzlich Prozess-, Session- und Generation-ID. |
| Semantisches „Was ist da?“ | Windows UI Automation: Buttons, Textfelder, Menüs, Namen, Zustände, Control Patterns und Events. [UI Automation](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview) | Spiele, Canvas-Apps und manche Electron-/GPU-Oberflächen bleiben teilweise oder komplett undurchsichtig. |
| Bild vom Fenster/Desktop | `Windows.Graphics.Capture` für einzelne Fenster oder Displays; für ganze Displays zusätzlich Desktop Duplication mit Dirty-/Move-Regions. [Windows Graphics Capture](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture), [Desktop Duplication](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/desktop-duplication-api) | Capture braucht Nutzerfreigabe; geschützte Inhalte und echtes Exclusive-Fullscreen können eingeschränkt oder schwarz sein. |
| Freie Overlay-Elemente | Native Layered Windows mit per-Pixel-Alpha und gezieltem Hit-Testing. Transparente Bereiche lassen Eingaben durch, aktive Rauten/Buttons fangen sie ab. [Layered Windows](https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features) | Ein riesiges fullscreen-Tk-Fenster ist dafür die falsche Grundform. |
| KDE 1/2 | KWin-Scripting/API für Fenster, virtuelle Desktops, Geometrie und Desktop-Zuordnung. [KWin API](https://develop.kde.org/docs/plasma/kwin/api/) | KDE-Wayland, KDE-X11 und virtuelle Desktopnummern sind unterschiedliche Adapterfälle. `DISPLAY=:1` ist nicht automatisch „Desktop 2“. |
| KDE-Wayland-Eingaben | KWin/EIS/libei beziehungsweise Remote-Desktop-Portal. Das Open-Source-Projekt `kwin-mcp` zeigt, dass Plasma 6 damit bereits Fenster, Screenshots, Accessibility und Eingaben orchestrieren kann. [kwin-mcp](https://github.com/isac322/kwin-mcp) | Das ist ein interessanter Baustein und Forschungsbeweis, aber noch kein Grund, ihn ungeprüft als Produktionskern einzubauen. |
| Systemaudio | WASAPI-Loopback kann den tatsächlich abgespielten Windows-Audiomix erfassen. [WASAPI Loopback](https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording) | Mikrofon und Systemaudio müssen trotzdem getrennte, individuell aktivierbare Empfänger bleiben. |

Der wichtigste Fund ist also: Wir brauchen nicht „eine Surface“, sondern fünf getrennte technische Fähigkeiten:

```text
Terminal-Session
      ↓
VT-Terminalrenderer

Fenster-/Desktop-Katalog ── UI Automation ── Capture
      ↓                         ↓             ↓
        Binding- und Gate-Modell

Native Overlay-Fenster
      ↓
Raute / Banner / Text / Bild / Zeichnung / Regie
```

## Der eigentliche Hinterhof-Fund

Die Bridge sollte für jedes Ziel eine Capability-Matrix führen:

```text
Ziel: Chrome-Fenster
capture:             ja
ui_automation:       teilweise
overlay:             ja
terminal_read:       nein
terminal_write:      nein
mouse_input:         möglich, aber gesondert prüfen
text_injection:      UIA oder Clipboard/Keyboard
```

```text
Ziel: Bridge-eigene ConPTY-Session
capture:             ja
terminal_read:       ja
terminal_write:      ja
cursor/colors/resize: ja
overlay:             ja
```

```text
Ziel: Spiel/GPU-Canvas
capture:             wahrscheinlich
ui_automation:       meistens nein
overlay:             abhängig von Fenster-/Fullscreenmodus
input:               gesonderter Beweis
```

Damit behauptet die Bridge nie pauschal „ich kann alles“, sondern zeigt konkret, was bei genau diesem Fenster möglich ist.

## Was wir aus den Open-Source-Projekten übernehmen sollten

- Microsofts ConPTY-MiniTerm und GUIConsole als Referenz für den Terminaltransport.
- xterm.js oder ein vergleichbarer VT-Renderer für die Darstellung.
- KWin-Scripting und optional `kwin-mcp` als Referenz für KDE-Wayland.
- Ein natives Windows-Fenster-Backend für Overlay, DPI und Hit-Testing.
- Python weiterhin für Orchestrierung, Sessions, Agenten, Bindings, Leases, Audit und Protokoll.
- Keine vollständige Electron-App und keine Tk-Fullscreen-Surface als Fundament.

Die sinnvollste Aufteilung wäre daher:

```text
Windows-Helfer: C#/.NET oder Rust/Win32
                Capture, Fenster, Overlay, UIA, globale Hotkeys

Bridge-Core:    Python
                Sessions, Agenten, Bindings, Leases, Audit, Protokoll

Terminal:       ConPTY/PTY + VT-Renderer
                keine Fake-Terminalkarten

KDE-Adapter:    Python/D-Bus/KWin/EIS
                Desktop 1, Desktop 2, Wayland/X11 getrennt
```

## Die kreative Schicht, die daraus möglich wird

Dein „WorldDOM“ wird dadurch tatsächlich realistisch:

1. Native Information  
   Fenster, Controls, Titel, Prozess, UIA-Elemente, Terminalzellen.

2. Wahrnehmungsinformation  
   Screenshot, OCR, Vision, erkannte Buttons oder Spielflächen.

3. Erfundene Arbeitsobjekte  
   Rauten, Pfeile, Texte, Bilder, Markierungen, Skizzen, Agentenanker.

4. Herkunft und Vertrauen  
   `native`, `ocr`, `vision`, `user_marked`, `agent_inferred`.

Ein Agent könnte dann sagen:

```text
„Das ist ein echtes UIA-Button-Element.“
„Das ist nur aus dem Bild vermutet.“
„Das hat Daniel selbst markiert.“
„Das ist meine eigene räumliche Notiz.“
```

Das ist wesentlich stärker als ein hübsches Overlay, weil später auch Kapseln, Zeit-Scrubber und Lernsystem wissen, welche Teile tatsächlich existierten und welche nur Interpretation waren.

## Meine harte Empfehlung für den Bau

Die Reihenfolge sollte jetzt sein:

1. Ein echter Bridge-eigener Terminalkanal über ConPTY.
2. Ein VT-Renderer mit Eingabe, Cursor, Farben, Alternate Screen und Resize.
3. Native Windows-Probe mit einzelnen Fenstern: verschieben, schließen, Transparenz, Durchklicken, eine aktive Raute.
4. Fensterkatalog mit stabilem Binding und vollständigem Desktop als Default-Ziel.
5. Capture eines echten Fensters und des gesamten Desktops.
6. Eine Raute mit 6,6‑Sekunden-Ticker und 3,3‑Sekunden-Banner.
7. Danach erst drei vollwertige Terminalfenster, Scanner unten rechts und Regie unten links.
8. Anschließend KDE-Desktop 1/2 als eigener Adapter.

Der zentrale Befund ist unangenehm, aber gut: Eine bereits laufende beliebige Terminalsession kann nicht allgemein durch Screenshotlesen zu einer echten identischen Session werden. Für echte Parität müssen wir die Session besitzen oder über einen expliziten Adapter erreichen. Genau deshalb sollte der erste funktionierende Terminalstein eine von der Bridge gestartete ConPTY-Session sein — danach schließen wir schrittweise die Lücke zu deinen bereits laufenden VPS-Terminals.

## Bedeutung für Skill und Harness

Diese Recherche gehört in beide Ebenen.

Der Skill muss als verbindliche Architektur festhalten:

- Terminaltransport und Terminalrenderer sind getrennt.
- Anzeigehost, Arbeitsziel, Session und Empfänger bleiben getrennt.
- Jeder Target-Typ erhält eine Capability-Matrix.
- Native Daten, Capture/OCR/Vision und künstliche WorldDOM-Objekte erhalten getrennte Herkunft und Konfidenz.
- „Session gestartet“, „Output gelesen“, „Input zugestellt“ und „Zustand beobachtet“ sind verschiedene Beweise.
- Windows, KDE-X11 und KDE-Wayland bekommen getrennte Adapter und dürfen nicht über `DISPLAY`-Annahmen vermischt werden.
- Ein Overlay-PASS beweist weder Terminal-Parität noch UI-Automation noch Eingabe im Zielprogramm.

Die Creative-Harness muss diese Dinge als Knoten und Gates modellieren:

```text
Target entdeckt
      ↓
Capabilities gelesen
      ↓
Binding gewählt
      ↓
Lease/Policy geprüft
      ↓
Aktion angenommen
      ↓
Aktion zugestellt
      ↓
Zielzustand zurückgelesen
      ↓
Audit- und Plattformbeweis vorhanden
```

Für Terminale muss die Harness mindestens diese Zustände unterscheiden:

```text
session_owned
pty_connected
vt_output_received
rendered
input_accepted
input_delivered
input_echoed
state_observed
audited
```

Für ein Fenster oder einen Desktop:

```text
target_discovered
target_identity_stable
capture_available
ui_automation_available
overlay_attached
hit_test_verified
input_path_verified
target_state_observed
```

Und für WorldDOM-Objekte:

```text
source: native | ocr | vision | user_marked | agent_inferred
confidence: 0.0 .. 1.0
observed_at: timestamp
bound_to: window | desktop | terminal | session
```

Das ist wichtig, weil die Harness sonst immer wieder in denselben Fehler laufen würde: Sie sieht ein gerendertes Element und erklärt daraus stillschweigend, dass die darunterliegende Welt ebenfalls verbunden sei. Genau diese Verwechslung hat den alten Surface-Prototypen so irreführend gemacht.
