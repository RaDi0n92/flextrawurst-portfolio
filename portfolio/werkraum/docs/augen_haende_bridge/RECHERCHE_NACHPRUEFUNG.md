# Nachprüfung der Bridge-Bauarbeit gegen das Netz (2026-10-02)

Auftrag von Daniel: alle Schritte und Goals rückwirkend im Netz gegenprüfen — ob es richtig gemacht ist und ob es Insider- oder Profitipps für Besseres gibt.

**Gewichtung der Quellen** (CLAUDE.md, „URLs und Netzinhalte richtig gewichten“): Herstellerdokumentation (Microsoft Learn, X.Org/Man-Pages, Chrome-DevTools-Protokoll, Tesseract-Doku) gilt als belastbar. Blogs, GitHub-Issues, Foren und Marketing-Texte gelten nur als Anregung und
wurden nie allein als Beleg benutzt. Keine Aussage unten wurde ohne eigene Messung am Code als „erledigt“ übernommen.

## Bestätigt (so ist es richtig)

| Bereich | Befund | Quelle (Gewicht) | Stand im Code |
|---|---|---|---|
| G06/G06.7 Linux-Fensterbild | XComposite: Fenster umleiten, benanntes Pixmap lesen, danach **freigeben**; sonst Leck der XIDs | man-Page XCompositeNameWindowPixmap (belastbar); Xpra #5051 (Anregung) | `pixmap.free()` vorhanden, belegt |
| G06.7 Windows-Fensterbild | `PW_RENDERFULLCONTENT` nötig für Chromium/Electron; bei DirectX/geschützten Fenstern liefert `PrintWindow` trotz `true` ein schwarzes Bild | Microsoft Q&A, Mozilla-Bug (Anregung bis mittel) | `ist_leer` + sichtbarer Rückfall, belegt unter Wine |
| G10 Übernahme | `LLMHF_INJECTED` nur durch `SendInput`; `SetCursorPos` und `mouse_event` sind nicht unterscheidbar von Hardware | Microsoft Learn LowLevelMouseProc (belastbar) | Bewegung über `SendInput`, am eigenen Fehler unter Wine gemessen |
| G11 Browser | `backendDOMNodeId` ist die Referenz; sie gilt nur bis zur Navigation (an `loaderId` gebunden) | CDP-Spezifikation (belastbar) | Wiederfinden über Rolle + Name, getestet (ungültige Kennung) |
| G11 Grundsatz | Struktur (Zugänglichkeitsbaum) zuerst, Bild nur als Rückfall | mehrere Beiträge 2026 (Anregung) | G06.7 und G11 so gebaut |
| G11 OCR | Tesseract ≥ 4 will dunkle Schrift auf hellem Grund; hell auf dunkel invertieren, kleine Ausschnitte vergrößern, Rauschen entfernen | Tesseract-Doku „Improving the quality“ (belastbar) | Inversion + Vergrößerung + Ausschnittserkennung (`weltdom_quellen.py`); die Seitenerkennung allein übersah weiße Schrift auf Blau (gemessen) |

## Lücken und Verbesserungen (aus der Recherche)

| Nr. | Befund | Folge für die Bridge | Entscheidung / Stand |
|---|---|---|---|
| R1 | **Wayland**: Plasma 6 läuft standardmäßig unter Wayland. XTEST, XComposite, XRecord gibt es dort nicht. Eingabe nur über libei bzw. `RemoteDesktop`-Portal, Aufnahme über PipeWire/`ScreenCast`, jeweils mit Zustimmung | Der Linux-Körper läuft nur unter X11/XWayland | Die KDE-Desktops der Bridge sind Xvfb (X11, geprüft: `XDG_SESSION_TYPE` leer, kein Wayland-Prozess). **Erledigt:** der Selbsttest hat eine Zeile „Sitzung“ (ok / Hinweis bei XWayland / fehlt bei reinem Wayland, mit dem Ausweg im Text). Ein echter Wayland-Weg ist ein eigenes Vorhaben (offen) |
| R2 | **Windows.Graphics.Capture** (ab Windows 10 1803) ist der moderne Weg für Fenster- und Spielaufnahme, wo `PrintWindow` schwarz bleibt | Bei Schwarz fällt die Bridge auf den Bildschirmausschnitt zurück (ehrlich, aber schlechter) | In der Prüfliste als Bauschritt eingetragen, **nativ prüfbar nur auf Daniels Windows** (unter Wine nicht); noch nicht gebaut |
| R3 | **`SetForegroundWindow`** wird von Windows oft verweigert (Foreground-Lock). Üblicher Weg: einmal `AttachThreadInput` an den Vordergrund-Thread, erneut versuchen, sofort lösen | Tippen und Hotkeys brauchen den Fokus; nativ war das ein wahrscheinlicher Fehlerpunkt | **Erledigt:** `WindowsBackend.fokus_geben` mit Anhängen und garantiertem Lösen; unter Wine geprüft (`tests/test_nachpruefung.py`); nativ offen |
| R4 | X11: **XInput2** trägt `sourceid`; XTEST-Geräte sind virtuelle Slave-Geräte. Damit ließe sich Daniels Hardware von den Händen exakt trennen, statt zu zählen | Die Übernahme-Erkennung unter X11 ist eine Näherung | Als Verbesserung in der Prüfliste; nicht gebaut, nicht ausprobiert (nur Suchtreffer) |
| R5 | **Controller**: `vgamepad` (ViGEmBus) ist der verbreitete Weg und installiert den Treiber beim `pip install` selbst | Widerspricht „kein Treiber ohne Daniels Wort“ | Bleibt gesperrt; bei Freigabe die Installation getrennt und bewusst ausführen |
| R6 | Wayland-Freigaben gelten **je Fenster oder Monitor** mit Zustimmung | Passt zum Lease-Gedanken | Hinweis für einen späteren Wayland-Körper |

## Nicht belegt / nicht geprüft

* Die Aussagen zu XInput2 und zur Wayland-Eingabe stammen aus Suchtreffern und wurden nicht am Code ausprobiert.
* Alle Windows-Aussagen sind nativ ungeprüft (Wine ist kein Windows).
* Die Anregungen aus Blogs („AT-SPI-first“, Grounding-Arbeiten) bestätigen die Richtung, beweisen aber nichts über diesen Code.

## Quellen

* https://github.com/Xpra-org/xpra/issues/5051
* https://linux.die.net/man/3/xcompositenamewindowpixmap
* https://bugzilla.mozilla.org/show_bug.cgi?id=1559011
* https://learn.microsoft.com/en-us/windows/win32/api/windows.graphics.capture.interop/nf-windows-graphics-capture-interop-igraphicscaptureiteminterop-createforwindow
* https://github.com/anthropics/claude-code/issues/95978
* https://www.screenish.com/blog/how-to-detect-fake-keyboard-and-mouse-activity
* https://learn.microsoft.com/en-us/previous-versions/windows/desktop/legacy/ms644986(v=vs.85)
* https://chromedevtools.github.io/devtools-protocol/tot/Accessibility/
* https://jocheojeda.com/2026/08/22/at-spi-first-grounding/
* https://zylos.ai/research/2026-02-08-computer-use-gui-agents/
* https://wiki.archlinux.org/title/Multi-pointer_X
* https://github.com/yannbouteiller/vgamepad
* https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
* https://github.com/isac322/kwin-mcp
* https://github.com/trycua/cua/pull/2008
* https://gist.github.com/Aetopia/1581b40f00cc0cadc93a0e8ccb65dc8c
* https://learn.microsoft.com/fi-fi/windows/win32/api/winuser/nf-winuser-setforegroundwindow
