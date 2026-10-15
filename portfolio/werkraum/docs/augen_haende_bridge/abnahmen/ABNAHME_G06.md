---
autor: claude bei Daniels VPS
datum: 2026-10-02
status: Entwurf zur Abnahme durch Daniel; alles nur auf dem VPS (Xvfb, Wine, echter Relay-Prozess) belegt, nativ bei Daniel offen
herkunft: `PLAN.md` G06, `ANFORDERUNGEN.md` R011–R014, R022, R115, R120; unlazy-Ledger `augen_haende_bridge/.unlazy/g06-g14/` (Teilstücke 1.1.1 bis 1.1.4 und Integration 1.1)
---

# Abnahmeprotokoll G06 — Windows und KDE 1/2 unabhängig anzeigen und benutzen

Zeichen: **belegt** (Test oder Probe, Befehl im Ledger), **nativ offen** (steht in der Prüfliste), **Lücke**, **Entscheidung**.

## Was gebaut wurde

1. **Linux-Fensterschicht** (`koerper/fenster_linux.py`, `win32_linux.py`, `menue_linux.py`, `plattform.py`): GTK 3 als Fensterschicht, Pillow als Zeichenfläche, dieselben Namen und Aufrufe wie die Windows-Fassung. Gewählt über `BRIDGE_BACKEND=linux`; ohne die Variable bleibt es Windows. Alle elf Fenster des Körpers laufen dadurch mit **unverändertem** Zeichen- und Bedien-Code.
2. **X11-Adapter** (`koerper/linux_adapter.py`, `x11_helfer.py`, `tasten_x11.py`): Fensterliste für den Scanner, Aufnahme des Desktops und einzelner Fenster über XComposite (auch verdeckte Fenster vollständig; die Fenster der Bridge lassen sich aus der Aufnahme auslassen), Tasteneingabe per XTEST (Umlaute, Emoji, jede Taste), lokaler F12-Not-Aus über XRecord, Sichtquelle, Dateiwahl.
3. **Relay mit mehreren Desktops** (`client_vps/anzeigeorte.py`, `desktops.json`, `terminal_launcher.py`, `transport.py`): je Desktop (Windows, KDE 1, KDE 2) ein eigenes Zugangspaar; Windows behält seine Kennungen. Ein Terminal hat einen **Anzeigeort** (wo Raute, Terminal, Chat stehen) und einen davon unabhängigen **Zielort** (was der Agent sieht).
4. **Linux-Körper** (`koerper/haupt_linux.py`, `haupt.py` über eine Plattformbeschreibung, `selbsttest_linux.py`, `client_vps/koerper_linux_starten.sh`).

## Anforderungen und Belege

| Forderung | Stand | Beleg |
|---|---|---|
| Das Overlay erscheint auf KDE 1 und KDE 2 (R011, G06) | belegt (Xvfb), nativ offen | `tests/test_g06_integration.py::ZweiKoerperTests`: zwei echte Linux-Körper auf zwei Bildschirmen und ein echter Relay; `tests/test_koerper_haupt_linux.py::KoerperEndeZuEndeTests` |
| Anzeigeort und Arbeitsziel unabhängig wählbar (R012) | belegt | Anzeigeort wechselt ohne Sitzungsverlust (gleiche ID, gleicher Prozess, Verlauf wird wieder eingespielt); das Ziel liegt auf einem anderen Desktop (Ziel-Gast sendet seinen ganzen Bildschirm); Bilder gelten nur vom Zielort, andere Desktops werden abgewiesen und gezählt: `test_anzeigeort.py`, `test_bridge_server_anzeigeort.py` |
| Windows und Linux sehen gleich aus und verhalten sich gleich („1:1“) | belegt für Aussehen und Größen, Grenze: Schrift | `ParitaetTests`: dieselben acht Fenster einmal mit GDI (Wine) und einmal mit GTK: Größen bis auf die Schriftmaße gleich (Chat, Regie, Kamera, Bild-Element exakt), Pixelübereinstimmung 84 bis 99 %, im Mittel 95 %. Windows nutzt Segoe UI und Consolas, Linux Noto Sans und DejaVu Sans Mono: die Buchstaben sehen nicht identisch aus. |
| Ganze Desktops und einzelne Fenster stimmen mit den Originalen überein (R013) | belegt (Aufnahme) | Aufnahme der richtigen Pixel, ein Ausschnitt mit Rand, ein verdecktes Fenster vollständig ohne fremde Pixel; Zielbild eines Ziel-Gasts hat die Größe des Bildschirms |
| Gemeinsame und getrennte Bindung | belegt | Zielort folgt dem Anzeigeort, bis er ausdrücklich gewählt wird; danach nicht mehr |
| Schließen oder Ersetzen eines Fensters bindet nicht still ein anderes Ziel (R014) | belegt | `ZielTests`: nach „weg“ nimmt der Starter keine Bilder mehr an, auch nicht von einem Ersatzfenster, bis ein neues Ziel ausdrücklich gemeldet wird |
| Host, Arbeitsplatz, Session und Ziel getrennt (R115) | belegt | `terminal_ort` trägt Laufort, Anzeigeort, Zielort, PID/Startzeit und das Ziel getrennt; das Raute-Menü „Anzeigeort und Ziel“ zeigt vier Zeilen |
| Inaktive, minimierte, verdeckte Ziele mit sichtbarer Fähigkeit | belegt (Meldung), nativ offen | `ziel_zustand` mit `zustand` (ok, verdeckt, minimiert, inaktiv, weg) und `faehigkeit` (frisch, fremde_pixel, letztes_bild, keine_aufnahme); Windows meldet bei „verdeckt“ ehrlich `fremde_pixel` (Bildschirmausschnitt), Linux `frisch` (XComposite) |
| X11-DISPLAY ersetzt keine Desktop-Kennung | belegt | Arbeitsplätze heißen `kde1`, `kde2` aus `desktops.json`, nicht nach Display-Nummern |
| Kein Rückschritt für Windows | belegt (Wine) | `tests/regression_alle.py` (1253 Tests, nur die drei bekannten Fehlschläge), Wine-Proben, der Windows-Start über die Plattformbeschreibung läuft unter Wine sauber an und beendet sich |

## Entscheidungen und Grenzen (bitte lesen)

- **Compositor:** Daniels KDE-Desktops laufen nach meinem Wissen ohne Compositor. Dann sind Fenster **undurchsichtig** (Deckkraft ohne Wirkung); die Bildschirmobjekte der Zeichenfläche nutzen eine Formmaske und Rasterung statt echter Durchsichtigkeit. Mit Compositor gibt es echtes Alpha, aber dann ist XComposite für die Aufnahme nicht verfügbar (siehe Selbsttest „Aufnahme“); das wird gemeldet, nicht verschwiegen.
- **Ziel auf einem anderen Desktop:** Das Ziel ist dort **der ganze Desktop**. Ein einzelnes Fenster eines anderen Desktops als Ziel zu wählen (Scanner-Liste über Desktops hinweg) ist **nicht gebaut** — Lücke, falls gewünscht.
- **Aufnahme eines verdeckten Fensters** liefert unter Linux das ganze Fenster; die Bilderfolge der Agenten schneidet bisher noch den Bildschirmausschnitt — der Wechsel auf die Fensteraufnahme ist G06.7.
- **Windows-Körper:** Die ausgelieferte exe 0.9.1 kennt Anzeigeorte noch nicht; sie funktioniert mit dem neuen Relay wie bisher, ein Wechsel von oder nach Windows geht erst mit dem neuen Paket.
- **Zugangsdaten:** Windows behält `BRIDGE_DESKTOP_TOKEN`/`BRIDGE_AGENT_TOKEN`. KDE 1 und KDE 2 haben private Token-Dateien (Rechte 0600) in `runtime/tokens/`, die der Relay beim ersten Start mit dem neuen Code anlegt. Der Relay muss dafür neu gestartet werden.
- **Zwischenfall (offen gelegt):** Beim Bau lief die Testsuite einmal nicht auf einem eigenen Xvfb, sondern auf dem sichtbaren vd1-Desktop (`DISPLAY=:1.0`) und tippte dort per XTEST Testtext und Enter an das gerade fokussierte Fenster. Seitdem laufen alle X11-Tests und Proben nur, wenn `BRIDGE_TEST_XVFB=1` ausdrücklich bestätigt, dass `DISPLAY` ein privater Xvfb ist.

## Entscheidung (Daniel)

- G06: ☐ abgenommen mit den Grenzen oben ☐ erst nach der Prüfliste (Prüfliste folgt mit dem Paket)
