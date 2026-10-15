# PLAN-G01 — Fundament: die Voraussetzungen, die sonst den Plan kippen

Datum: 2026-09-20 · Autor: claude bei Daniels VPS · Ort: vd1 (`/config`), Repo `/root/werkraum`

Dieses Goal ist G01 aus `docs/augen_haende_bridge/PLAN.md`. Es liefert Proben und Verträge, keine Oberfläche. Codex' frühere Nummerierung
(G01–G12 im Bauprotokoll) ist eine andere; hier ist immer der Plan gemeint.

## Fokusvertrag dieses Zyklus

- Ziel: G01 des Plans. Nächster einzelner Stein: die acht Punkte der »Konkreten Arbeit« mit realem Ergebnis belegen.
- Erhaltungsanker: Der Körper besteht aus Terminal, Scanner je Terminal, Raute, Kamera und Mikrofon (BE03). Kein Overlay als Fläche (R118).
  1:1 nur für Sitzungen, die die Bridge selbst startet (BE01). Harness und beide Skills bleiben unverändert (BE04).
  Die exe geht erst mit dem kompletten ersten Körper an Daniel (BE03).
- Verbotene Drift: kein Tk-Fenster als Grundlage, keine Attrappen, keine Terminal-Anbindung bestehender Sessions, kein Browsernachbau.

## 1. Bauumgebung — PASS (Wine), native Abnahme UNKNOWN

| Was | Ergebnis |
| --- | --- |
| Wine | 10.0 (Ubuntu), isolierter Prefix `/config/wine-bridge-build/prefix`, Win64 |
| Windows-Python | 3.13.5, Installer `python-3.13.5-amd64.exe`, SHA256 `c1cb40978b28f696b111c36034a1bdeda17d25e35c74a08ef5e5ff405a63fc20` |
| Pakete | PyInstaller 6.14.2, websockets 16.1.1 (dieselben festen Versionen wie im bisherigen Bau) |
| Rust-Weg | nicht möglich ohne Systemänderung: `/usr/lib/rust-1.93` hat nur das Ziel `x86_64-unknown-linux-gnu`, kein Windows-Std, kein mingw-w64 |
| Netz | Installer-Download und `pip` funktionierten |

Die frühere Wine-Umgebung von Codex war ein temporärer Prefix und existierte nicht mehr. Der neue Prefix liegt außerhalb des Repos und ist reproduzierbar
aus den obigen Angaben.

## 2. Native Probe: Fenstereigenschaften — PASS auf API-Ebene unter Wine, native Wirkung UNKNOWN

Probe: `augen_haende_bridge/probes/window_probe.py` (reines Win32 über ctypes, kein Tk). Vier Fenster liegen sich im Weg.

| Eigenschaft | Ergebnis unter Wine |
| --- | --- |
| Durchsichtigkeit je Fenster | `SetLayeredWindowAttributes(87)` gesetzt, `GetLayeredWindowAttributes` liest `87` zurück (34 % Deckkraft = 66 % durchsichtig) |
| Rautenform | `SetWindowRgn` gesetzt, Regionsbox `[0,1,99,99]`, Regionstyp komplex |
| Durchklicken | Windows-eigene Trefferlogik `WindowFromPoint`: Punkt im `WS_EX_TRANSPARENT`-Fenster trifft das Fenster darunter; Punkt an der Rautenecke trifft das Fenster darunter; Punkt in der Rautenmitte trifft die Raute; Punkt im Fenster mit Deckkraft trifft dieses Fenster |
| Textfokus | getippte Zeichen kamen als `WM_CHAR` an |
| Schließen | Esc beendet alle Fenster, Prozess endet mit Exit-Code 0 |
| DPI | `SetProcessDpiAwarenessContext(PER_MONITOR_AWARE_V2)` akzeptiert |
| Fensterrechtecke | alle vier Win32-Rechtecke wie angefordert |

**Grenze:** Unter Wine ohne Compositor legt der X11-Treiber Fenster mit Deckkraft als bildschirmgroße X-Fenster an. Deshalb liefern Klicks über `xdotool`
dort kein aussagekräftiges Bild. Das ist ein Wine-Effekt und keine Aussage über Windows. Ob die Fenster auf einem echten Windows sichtbar durchsichtig
sind, sich bewegen lassen und Klicks dort durchlassen, bleibt **UNKNOWN**, bis das gepackte Programm auf Daniels Windows läuft. Dafür bekommt das Programm
einen Selbsttest (`--selbsttest`), der dieselben Prüfungen dort ausführt und eine JSON-Datei schreibt.

## 3. Terminal, das die Bridge hält — Entscheidung nach Probe

Probe: `probes/conpty_probe.py`. Ergebnis unter Wine: `CreatePseudoConsole` existiert und der Kindprozess läuft, aber seine Ausgabe landet nicht in der
Pipe der Pseudokonsole (0 Bytes, der Marker erscheint auf dem echten stdout). ConPTY ist hier also **nicht testbar**. Auf einem echten Windows wäre es
verfügbar, ich könnte das Ergebnis dort aber nicht vor der Übergabe belegen.

Entscheidung: Das Terminal des ersten Körpers besteht aus einer **Linux-PTY-Sitzung, die die Bridge auf dem VPS selbst startet und hält** (BE01, BE02).
Der rohe Strom läuft über das Relay zum Windows-Fenster, das ihn mit einer Terminal-Emulationsbibliothek darstellt. Eingaben und Größenänderungen laufen zurück.
Das ist derselbe Weg wie V3.1 bis V3.3 (besessene PTY-Sitzung, rohe Bytes an den Bridge-Controller, Resize per Kernel-Roundtrip) und lässt sich vollständig auf
Linux und unter Wine prüfen. Bestehende Sessions werden nicht angebunden.

## 4. KDE-Sitzung — belegt

Preflight `python3 -m augen_haende_bridge.preflight`: KDE live (`qdbus6`, `DISPLAY=:1`), WebSocket verfügbar, Windows-Runner und native Fensterbeweise
`NOT_PROVEN`. Zusätzlich: `XDG_SESSION_TYPE=wayland` mit XWayland als `:1`. Aus `DISPLAY` folgt keine KDE-Arbeitsflächennummer.

## 5. Basisaufnahme und private Empfängerkomposition — Weg festgelegt, native Wirkung UNKNOWN

`SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)` nimmt eigene Fenster aus der Bildschirmaufnahme. Unter Wine schlägt der Aufruf fehl (Fehler 8, Readback 0).
Das ist der Leakage-Fall der physischen Rückaufnahme: Ohne Ausschluss stünden die Fenster der Bridge im Basisbild.

Festlegung: Das Programm versucht den Ausschluss für jedes eigene Fenster und meldet das Ergebnis als Fähigkeit `capture_excludes_own_windows`.
Ist sie `false`, sind private Objekte gesperrt, und die Fenster der Bridge werden für die Aufnahme kurz ausgeblendet. Die Komposition je Empfänger
(Banner und Ticker in das Bild, das ein Agent sieht) geschieht im Bild und nicht auf dem physischen Bildschirm. Auf Windows 10 vor Version 2004 gibt es den
Ausschluss nicht.

## 6. Gemeinsame IDs, Ereignisse, Zustände — festgelegt

Getrennte Kennungen: `agent_id` (was läuft), `terminal_id` (die von der Bridge gehaltene Sitzung), `start_id` (Eintrag der Startliste auf dem VPS),
`target_id` mit `generation` (Fenster oder Desktop), `binding_id`, `gate_id`, Empfänger und Relay-`session_id`. Labels sind änderbar, Kennungen nicht.
Nachrichten tragen `v`, `id`, `epoch` und eine Sequenz. Ergebniszustände bleiben getrennt: `accepted`, `forwarded`, `received`, `observed`, `audited`.
Die Umsetzung im Relay ist der erste Stein von G02.

## 7. Grenzen und Messziele — festgelegt (Ziele, keine Messwerte)

- Ruhe-Arbeitsspeicher des Programms: Ziel unter 150 MB, gemessen auf Daniels Gerät. Die frühere Zusage »unter 60 MB« gilt nicht als erwiesen.
- Tastendruck bis Echo im Terminal über den Tunnel: Ziel unter 150 ms, gemessen mit Zeitstempeln.
- Banner 3,3 s und Ticker 6,6 s: Toleranz 100 ms, gemessen im Selbsttest.
- Bilder nur auf Anforderung oder im 10-Hz-Fenster während einer Handlung, nie als Dauerstrom.
- Abweichungen werden berichtet und nicht als PASS verborgen.

Update und Persistenz: Einstellungen in `%APPDATA%\AugenUndHaende\settings.json`, Paket als Ordner mit Versionsdatei; die vorige Version bleibt für den
Rückweg liegen.

## 8. Stackwahl

Python-Programm mit ctypes-Fenstern (Win32), einer Terminal-Emulationsbibliothek und Pillow, gepackt mit PyInstaller als `--onedir`. Kamera und Mikrofon
kommen als spät geladene Module. Gründe: Der Windows-Teil braucht keine Systemänderung, der vorhandene, geprüfte Code für Scanner, Aufnahme und Transport bleibt
in Gebrauch, und die Fenstereigenschaften sind mit Standard-Win32-Aufrufen belegt. Rust scheidet hier aus (siehe Abschnitt 1). Das bisherige Tk-Fenster
(`client_windows/overlay_app.py`) widerspricht R118 und wird ersetzt.

## Ergebnis

**PASS** für Bauumgebung, Fenster-API-Verhalten unter Wine, KDE-Fakten und alle Festlegungen. **UNKNOWN** für alles, was nur auf Daniels Windows sichtbar
wird: echte Durchsichtigkeit, Durchklicken mit der Hand, DPI, Ausschluss aus der Aufnahme. Diese Punkte gehen als Übergabe in G02.
