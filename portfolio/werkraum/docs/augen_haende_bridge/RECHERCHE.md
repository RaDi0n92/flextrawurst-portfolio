---
autor: claude bei Daniels VPS
datum: 2026-09-20
herkunft: Netzrecherche von codex bei Daniels VPS vom 2026-09-19 (Hinterhöfe-Recherche zu Terminal, Scanner und Overlay; Hinterhöfe-Haijagd zu Fensterscanner, Agent-Harness und Live-QA) und die technische Recherche der Baustartprüfung (Abruf 2026-09-19). Neu geschrieben von Claude aus den Originalen in archiv/originale/
zweck: was im Netz trägt, was andere schon gelöst haben und was daraus für den Bau folgt
---

# Augen & Hände — Recherche

Das Netz kennt fast alle Teile dieses Vorhabens, und andere haben sich an denselben Problemen schon die Zähne ausgebissen. Diese Recherche ging deshalb in die Werkstätten: Wer hat welchen Teil praktisch gelöst, und wo liegen die Grenzen?

Der wichtigste Fund: Der Fensterscanner ist kein UI-Feature, sondern der zentrale Kern für Sehen und Sicherheit.

## Was wirklich trägt

| Aufgabe | Belastbarer Weg | Grenze |
| --- | --- | --- |
| Echter Terminalbetrieb | Windows **ConPTY**: bidirektionaler UTF-8- und VT-Strom für Input, Output, Cursor, Farben und Resize. [Microsoft ConPTY](https://github.com/MicrosoftDocs/Console-Docs/blob/main/docs/creating-a-pseudoconsole-session.md) | Funktioniert sauber, wenn wir die Session selbst starten. Eine beliebige, schon laufende Fremd-Session lässt sich nicht universell »magisch« übernehmen. |
| Terminaldarstellung | Ein VT-Terminalrenderer statt eines Textfelds. xterm.js kann echte Shell-Prozesse über PTY anbinden und unterstützt unter anderem `vim`, `tmux`, Farben, Unicode und Mausereignisse. [xterm.js](https://github.com/xtermjs/xterm.js/) | xterm.js ist nur der Renderer, nicht die Session selbst. |
| Windows-Fensterscanner | `EnumWindows` und Fensterhandles, `GetWindowRect`, Prozessdaten, DPI, Z-Order, dazu `SetWinEventHook` für Öffnen, Schließen, Fokus und Größenänderungen. [GetWindowRect](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowrect), [SetWinEventHook](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook) | Ein HWND darf nicht allein die dauerhafte Identität sein. Dazu braucht es Prozess-, Session- und Generation-ID. |
| Semantisches »Was ist da?« | Windows UI Automation: Buttons, Textfelder, Menüs, Namen, Zustände, Control Patterns und Events. [UI Automation](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview) | Spiele, Canvas-Apps und manche Electron- und GPU-Oberflächen bleiben teilweise oder komplett undurchsichtig. |
| Bild vom Fenster oder Desktop | `Windows.Graphics.Capture` für einzelne Fenster oder Displays. Für ganze Displays zusätzlich Desktop Duplication mit Dirty- und Move-Regions. [Windows Graphics Capture](https://learn.microsoft.com/en-us/windows/uwp/audio-video-camera/screen-capture), [Desktop Duplication](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/desktop-duplication-api) | Capture braucht die Freigabe des Nutzers. Geschützte Inhalte und echtes Exclusive-Fullscreen können eingeschränkt oder schwarz sein. |
| Freie Overlay-Elemente | Native Layered Windows mit Per-Pixel-Alpha und gezieltem Hit-Testing. Transparente Bereiche lassen Eingaben durch, aktive Rauten und Buttons fangen sie ab. [Layered Windows](https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features) | Ein riesiges Tk-Fenster im Vollbild ist dafür die falsche Grundform. |
| KDE 1/2 | KWin-Scripting und -API für Fenster, virtuelle Desktops, Geometrie und Desktop-Zuordnung. [KWin API](https://develop.kde.org/docs/plasma/kwin/api/) | KDE-Wayland, KDE-X11 und virtuelle Desktopnummern sind unterschiedliche Adapterfälle. `DISPLAY=:1` ist nicht automatisch »Desktop 2«. |
| KDE-Wayland-Eingaben | KWin/EIS/libei beziehungsweise das Remote-Desktop-Portal. Das Open-Source-Projekt `kwin-mcp` zeigt, dass Plasma 6 damit bereits Fenster, Screenshots, Accessibility und Eingaben orchestrieren kann. [kwin-mcp](https://github.com/isac322/kwin-mcp) | Ein interessanter Baustein und Forschungsbeweis, aber noch kein Grund, ihn ungeprüft als Produktionskern einzubauen. |
| Systemaudio | WASAPI-Loopback kann den tatsächlich abgespielten Windows-Audiomix erfassen. [WASAPI Loopback](https://learn.microsoft.com/en-us/windows/win32/coreaudio/loopback-recording) | Mikrofon und Systemaudio müssen trotzdem getrennte, einzeln aktivierbare Empfänger bleiben. |

Daraus folgt: Die Bridge braucht nicht »eine Surface«, sondern fünf getrennte technische Fähigkeiten.

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

## Eine Capability-Matrix für jedes Ziel

Die Bridge führt für jedes Ziel eine Capability-Matrix. Sie behauptet nie pauschal »ich kann alles«, sondern zeigt, was bei genau diesem Fenster möglich ist.

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

## Was andere schon gelöst haben

- **agent-desktop-harness** kommt der Idee erstaunlich nah: native Windows-Fenster- und Display-Erkennung, UI Automation, Screenshots, stabile UI-Referenzen, ein Beobachtungsschutz vor Aktionen und eine zusammenhängende Evidence-Kette aus Events, UI-Tree und Bild. Koordinaten werden nicht blind benutzt, sondern erst nach einer aktuellen Beobachtung freigegeben. Genau das brauchen die Fensterbindungen. [Agent Desktop Harness](https://github.com/xuyw1997/agent-desktop-harness)
- **agent-desktop** arbeitet mit Snapshot-IDs und qualifizierten Elementreferenzen statt mit »klick mal bei x=438/y=290«. Eine Aktion bezieht sich damit auf genau den zuvor beobachteten Zustand. Texte und Timer gelten dort nicht als stabile Identität. Fenster, Rolle, Pfad und Geometrie sind wichtiger. [agent-desktop](https://github.com/lahfir/agent-desktop)
- **windows-mcp-server** geht noch weiter in Richtung Sicherheits-Harness: Aktionen sind an Gerätezustand, Policy, Auditkette und Live-Zustand gekoppelt. Für die Bridge heißt das, dass der Fensterscanner zum Ursprung einer überprüfbaren Aktion wird und nicht bloß Screenshots liefert. [windows-mcp-server](https://github.com/deploymenttheory/windows-mcp-server)
- **kwin-mcp** ist für KDE und Wayland besonders wertvoll. Es verbindet Screenshot, KWin-Fensterrechtecke, den AT-SPI-Accessibility-Tree, virtuelle Sessions und EIS-Eingabe. Es zeigt, dass strukturierte Fensterdaten und Bilder gemeinsam an einen Agenten geliefert werden können, getrennt vom tatsächlichen Eingaberecht. [kwin-mcp](https://github.com/isac322/kwin-mcp)
- **UFO2** bestätigt architektonisch die Mehragentenidee: ein zentraler Host-Agent, spezialisierte App-Agenten, UIA plus Vision und isolierte PiP- und Desktop-Arbeitsräume. Das ist im Kern eine wissenschaftlich beschriebene Variante von »mehrere Wesen in unterschiedlichen Gates«. [UFO2](https://arxiv.org/abs/2504.14603)
- **Temporal UI State Inconsistency** beschreibt den Abstand zwischen Beobachtung und Aktion als TOCTOU-Problem. Fensterfokus oder Overlay können sich nach dem Screenshot ändern, bevor der Agent handelt. Die vorgeschlagene Verteidigung prüft unmittelbar vor jeder Aktion Pixel, globalen Screenshot und strukturellen Fensterzustand erneut. [Temporal UI State Inconsistency](https://arxiv.org/abs/2604.18860)

## Der Fensterscanner als Kern

Der Scanner liefert diese Kette:

```text
vollständiger Desktop-Frame
        +
Fenster-/Desktop-Inventar
        +
UIA-/Accessibility-Struktur
        +
stabile Snapshot-ID
        +
ausgewähltes Ziel
        +
Binding-Rücklese
        +
unmittelbarer Pre-Action-Rescan
```

Der Agent bekommt also nicht nur ein Bild, sondern fünf Dinge:

```text
Bild:
  Was ist sichtbar?

Struktur:
  Welche Fenster, Controls und Rechtecke existieren?

Binding:
  Woran bin ich gerade gebunden?

Generation:
  Ist es noch dasselbe Fenster?

Pre-Action-Check:
  Ist die Welt unmittelbar vor der Aktion noch dieselbe?
```

Hier kommt der Blender-Skill hinein. Seine Betriebsweise ist:

```text
Baseline-Bild
→ strukturierter Scanner-Readback
→ genau eine Bindungs-/UI-Aktion
→ 10-Hz-Trajektorie bei Bewegung/Resize/Banner
→ unmittelbares After-Bild
→ erneuter strukturierter Readback
→ Vergleichsmatrix
→ Evidence
```

Das ist nicht bloß QA hinterher. Das ist die Betriebsweise der Bridge selbst.

Der Fensterscanner steht deshalb vor Terminal, Raute, Overlay, WorldDOM und Eingabe:

```text
Scanner
  ↓
Ziel auswählen
  ↓
Zielidentität prüfen
  ↓
Capabilities lesen
  ↓
Agent/Gate binden
  ↓
Bild + Struktur liefern
  ↓
Overlay räumlich anheften
  ↓
vor jeder Aktion neu prüfen
```

Korrektur gegenüber der letzten Skill-Erweiterung: Dort steckte der Scanner nur implizit unter »Target discovered«, und das war zu schwach. Er muss ein eigener Bauabschnitt und ein eigener Bereich von Harness-Knoten werden:

```text
SCAN_REQUESTED
FRAME_CAPTURED
INVENTORY_READ
TARGET_SELECTED
IDENTITY_VERIFIED
BINDING_CREATED
BINDING_READ_BACK
PRE_ACTION_RESCAN
TARGET_STATE_OBSERVED
```

Das ist der eigentliche Bridge-Kern. Ohne ihn gäbe es nur ein Overlay, das zufällig irgendwo herumliegt.

## Aufteilung und was aus Open Source übernommen werden soll

Übernommen werden sollen:

- Microsofts ConPTY-MiniTerm und GUIConsole als Referenz für den Terminaltransport,
- xterm.js oder ein vergleichbarer VT-Renderer für die Darstellung,
- KWin-Scripting und optional `kwin-mcp` als Referenz für KDE-Wayland,
- ein natives Windows-Fenster-Backend für Overlay, DPI und Hit-Testing,
- Python weiterhin für Orchestrierung, Sessions, Agenten, Bindings, Leases, Audit und Protokoll.

Keine vollständige Electron-App und keine Tk-Fullscreen-Surface dienen als Fundament.

Die sinnvollste Aufteilung ist:

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

## WorldDOM: woher ein Wissen kommt

Mit diesen Bausteinen wird das WorldDOM realistisch. Es hat vier Schichten:

1. **Native Information:** Fenster, Controls, Titel, Prozess, UIA-Elemente, Terminalzellen.
2. **Wahrnehmungsinformation:** Screenshot, OCR, Vision, erkannte Buttons oder Spielflächen.
3. **Erfundene Arbeitsobjekte:** Rauten, Pfeile, Texte, Bilder, Markierungen, Skizzen, Agentenanker.
4. **Herkunft und Vertrauen:** `native`, `ocr`, `vision`, `user_marked`, `agent_inferred`.

Ein Agent kann dann sagen:

```text
»Das ist ein echtes UIA-Button-Element.«
»Das ist nur aus dem Bild vermutet.«
»Das hat Daniel selbst markiert.«
»Das ist meine eigene räumliche Notiz.«
```

Das ist wesentlich stärker als ein hübsches Overlay. Auch Kapseln, Zeit-Scrubber und das Lernsystem wissen dadurch, welche Teile tatsächlich existierten und welche nur Interpretation waren.

## Empfohlene Reihenfolge des Baus

1. Ein echter, bridge-eigener Terminalkanal über ConPTY.
2. Ein VT-Renderer mit Eingabe, Cursor, Farben, Alternate Screen und Resize.
3. Eine native Windows-Probe mit einzelnen Fenstern: verschieben, schließen, Transparenz, Durchklicken, eine aktive Raute.
4. Ein Fensterkatalog mit stabilem Binding und dem vollständigen Desktop als Default-Ziel.
5. Capture eines echten Fensters und des gesamten Desktops.
6. Eine Raute mit 6,6-Sekunden-Ticker und 3,3-Sekunden-Banner.
7. Danach erst drei vollwertige Terminalfenster, der Scanner unten rechts und die Regie unten links.
8. Anschließend KDE-Desktop 1/2 als eigener Adapter.

Der zentrale Befund ist unangenehm, aber gut: Eine bereits laufende, beliebige Terminalsession kann nicht allgemein durch Screenshotlesen zu einer echten, identischen Session werden. Für echte Parität muss die Bridge die Session besitzen oder über einen expliziten Adapter erreichen.

Deshalb ist der erste funktionierende Terminalstein eine von der Bridge gestartete ConPTY-Session. Danach wird schrittweise die Lücke zu den bereits laufenden VPS-Terminals geschlossen.

**Geändert durch BE01** (`ANFORDERUNGEN.md`): Diese Lücke wird nicht geschlossen. Bestehende Sessions werden nicht angebunden. 1:1 gilt für Sitzungen, die die Bridge selbst startet.

## Bedeutung für Skill und Harness

Die Recherche gehört in beide Ebenen.

**Der Skill muss als verbindliche Architektur festhalten:**
- Terminaltransport und Terminalrenderer sind getrennt.
- Anzeigehost, Arbeitsziel, Session und Empfänger bleiben getrennt.
- Jeder Target-Typ erhält eine Capability-Matrix.
- Native Daten, Capture/OCR/Vision und künstliche WorldDOM-Objekte erhalten getrennte Herkunft und Konfidenz.
- »Session gestartet«, »Output gelesen«, »Input zugestellt« und »Zustand beobachtet« sind verschiedene Beweise.
- Windows, KDE-X11 und KDE-Wayland bekommen getrennte Adapter und werden nicht über `DISPLAY`-Annahmen vermischt.
- Ein Overlay-PASS beweist weder Terminal-Parität noch UI-Automation noch Eingabe im Zielprogramm.

**Die Creative-Harness muss diese Dinge als Knoten und Gates modellieren:**

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

Für Terminals unterscheidet die Harness mindestens diese Zustände:

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

Für WorldDOM-Objekte:

```text
source: native | ocr | vision | user_marked | agent_inferred
confidence: 0.0 .. 1.0
observed_at: timestamp
bound_to: window | desktop | terminal | session
```

Das ist wichtig, weil die Harness sonst immer wieder in denselben Fehler läuft: Sie sieht ein gerendertes Element und erklärt daraus stillschweigend, dass auch die darunterliegende Welt verbunden sei. Genau diese Verwechslung hat den alten Surface-Prototypen so irreführend gemacht.

## Konsequenzen aus den technischen Quellen

Aus der Baustartprüfung, Abruf am 2026-09-19. Das sind Konsequenzen und keine Zauberrezepte.

- PyInstaller ist kein allgemeiner Cross-Compiler. Der Windows-Build braucht eine passende Windows-Umgebung. Wine kann untersucht werden, ersetzt aber keine native Abnahme. Quellen: https://pyinstaller.org/en/stable/ und https://www.pyinstaller.org/en/stable/usage.html
- Bei Win32-Layered-Windows hängen Hit-Tests von Form, Transparenz und Fensterstilen ab. Ein pauschal transparentes Fenster ist nicht gleichbedeutend mit »Buttons bedienbar, Zwischenräume durchlässig«. Das muss als native Probe entschieden werden. Quelle: https://learn.microsoft.com/en-us/windows/win32/winmsg/window-features
- `PostMessage` stellt Nachrichten in eine Queue, und UIPI begrenzt den Zugriff. Erfolg beim Absenden ist kein Zustandsbeweis im Ziel. Quelle: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-postmessagew
- Python `pty` ist Unix-spezifisch. Terminaltransport und Darstellung dürfen nicht ungeprüft mit dem Linux-Probeprozess gleichgesetzt werden. Quelle: https://docs.python.org/3/library/pty.html

Daraus folgt keine bereits abgeschlossene Wahl eines neuen UI-Frameworks. Erst ein kleiner nativer Fähigkeitsbeweis entscheidet, ob der gewählte leichte Stack Transparenz, Fokus, DPI und Terminaldarstellung ausreichend trägt.
