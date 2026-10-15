---
autor: claude bei Daniels VPS
datum: 2026-09-20
herkunft: Baustartprüfung von codex bei Daniels VPS (2026-09-19) und Postmortem von codex bei Daniels VPS (2026-09-20). Neu geschrieben von Claude aus den Originalen in archiv/originale/
status: Prüfung abgeschlossen; native Produktabnahme offen; Bau-Goal auf Daniels Wunsch pausiert; Produkt nicht abgenommen
betrifft: [augen-haende-bridge, baustartpruefung, falscher-baupfad, review-versagen, surface-drift]
---

# Augen & Hände — Befunde

Dieses Dokument hält fest, wie es um die Bridge stand, als geprüft wurde, und was daraus folgt. Es hat zwei Teile: die Baustartprüfung vom 2026-09-19 und den Befund zum falschen Bridge-Körper vom 2026-09-20. Die Aussagen gelten für den Stand des jeweiligen Datums.

## Baustartprüfung vom 2026-09-19

### Ergebnis und Geltung

Die Idee ist klar genug für einen schmalen ersten Bauabschnitt. Der damalige Stand war aber **keine fertig verbundene Windows-Bridge**. Browserbeweise belegen Browserfunktionen und nicht die native EXE. Ein getesteter Windows-Build-, Auslieferungs- und Rückkanal war nicht nachgewiesen.

Die Gesamt-Goalliste folgte erst nach dieser Prüfung und steht in `PLAN.md`. Die Prüfung selbst startete keinen Goal und keine Implementierung.

Bei Widersprüchen zu älteren Bauanweisungen gilt diese Korrektur für den nächsten Bauabschnitt. Daniels Aussagen bleiben die Anforderungsquelle. Vorschläge von Codex werden dadurch nicht nachträglich zu Daniels Entscheidungen. Die früheren Dokumente und der eingefrorene Gemini-Prototyp bleiben erhalten.

Was Daniel festgelegt hat, steht in `ANFORDERUNGEN.md` im Abschnitt »Was Daniel festgelegt hat«.

### Befund 1 — Die Browser-Abnahme war zu weit ausgelegt

`/root/werkraum/augen_haende_bridge/tests/evidence/B4_6_REFERENCE_SURFACE_EVIDENCE.md` enthält `OUTCOME: PASS` und behauptet zugleich, die dargestellte Browseransicht sei bereits die räumliche Windows-Bridge. Die aufgeführten DOM- und Playwright-Prüfungen tragen diese zweite Behauptung nicht.

Das historische PASS bleibt als Browser-Testresultat erhalten. Die native Produktabnahme ist **offen**.

### Befund 2 — Der native Entwurf war noch kein tragfähiges Overlay

`/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py` setzt ein bildschirmfüllendes Tk-Fenster mit Deckkraft 0,94 auf. Freie, klickdurchlässige Bereiche und selektiv bedienbare Overlay-Elemente sind dort nicht nachgewiesen.

Es gibt fest gezeichnete Beziehungspfeile, Terminalkarten statt einer vollständigen Terminaldarstellung und lokale Zustandswechsel für Mikrofon und Kamera statt einer belegten Aufnahme.

Zeile 64 ruft `self.root.wm_class(...)` auf, und der umgebende Handler fängt nur `tk.TclError`. Eine Read-only-Prüfung mit `hasattr(tk.Tk, "wm_class")` ergab `False`. Damit liegt ein konkreter API-Fehler im Startpfad. Das ist ein statischer Befund plus lokale API-Prüfung und **kein durchgeführter Windows-Starttest**.

F12 ist dort nur an den Tk-Eventloop gebunden. Ein systemweiter Not-Aus, der von einem hängenden UI unabhängig ist, ist damit nicht bewiesen.

### Befund 3 — Terminal-Erkennung ist noch keine Terminal-Parität

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/target_registry.py` fragt lokal den Konsole-Adapter ab. Eine Windows-Instanz erhält dadurch nicht automatisch VPS-Terminals. Windows- und KDE-Ziele stehen ausdrücklich auf `unavailable`. Terminal-IDs entstehen aus der Entdeckungsreihenfolge, und verschwundene Einträge werden beim Refresh nicht entfernt. Für dauerhaft sichere Bindungen fehlen stabile Identität und Lebenszyklusbehandlung.

`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_adapter.py` liest dargestellten Text. Das beweist weder einen vollständigen VT-Terminalzustand noch Eingaben in die ursprüngliche Agentensession. Das isolierte Probe-Terminal in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/probe_terminal.py` bleibt ein anderer Testgegenstand.

Eine zunächst vermutete, sofortige Windows-Importsperre durch `pty` wurde **nicht bestätigt**. Der Import steht in einem eingebetteten Wrapper-String und nicht als sofort ausgeführter Modulimport. Der Wrapper selbst ist Unix-spezifisch. Eine erfundene Importfehlermeldung darf nicht in den Bauplan übernommen werden.

### Befund 4 — Die Auslieferung ist offen

`/root/werkraum/augen_haende_bridge/client_windows/build_exe.bat` installiert PyInstaller ohne feste Version, prüft Fehler nicht ausdrücklich und meldet am Ende unabhängig vom Erfolg einen Paketpfad. `--onedir` erzeugt ein Verzeichnis-Bundle, die EXE allein ist also nicht das vollständige Paket. Im durchsuchten Greenfield-Verzeichnis wurde keine EXE gefunden.

Wine ist in der Umgebung vorhanden. Das ist weder ein Windows-Buildnachweis noch ein Test auf Daniels Windows. Es wurde kein neuer Runner angelegt, kein fremder Wine-Prefix verändert und kein Release veröffentlicht.

### Befund 5 — Alte Skill-Garantien sind keine Messwerte

Der ursprüngliche Skill `/config/.agents/skills/augen-und-haende-bridge/SKILL.md` verbindet gute Ziele mit unbelegten Zusagen: Not-Aus unter 1 ms, Disconnect-Stopp unter 10 ms trotz 1-s-Heartbeat, exakt 12 ms Cursorleihe, null VRAM und Idle-CPU sowie garantierte RAM-Grenzen. Diese Zahlen dürfen nicht als funktionierende Eigenschaften oder universelle Abnahmekriterien weitergetragen werden.

Ein Abtastraster von 10 Hz garantiert keine lückenlose Beobachtung. KDE-Arbeitsflächen sind nicht automatisch verschiedene X11-Displays. Ein gepostetes Windows-Ereignis ist kein Beweis, dass eine Anwendung es ausgeführt hat. Die Wahl von Hardware und Framework bleibt von gemessenen Fähigkeiten abhängig.

### Was vor dem jeweiligen Fertigmelden noch fehlte

| Nachweis | Stand |
| --- | --- |
| Produkt und erste Kontaktstrecke klar beschrieben | Ja, hier korrigiert |
| Native Buildumgebung und vollständiges Paket | Nicht nachgewiesen |
| Windows-Start ohne Entwicklungsinstallation | Nicht nachgewiesen |
| TLS/Pairing/erreichbarer Liefer- und Rückkanal | Nicht nachgewiesen |
| Echter Agent empfängt Bild, sendet Nachricht, erhält Antwort | Nicht nachgewiesen |
| Original-Terminal vollständig lesbar und bedienbar | Nicht nachgewiesen |
| Overlay-Anzeigewechsel Windows/KDE 1/2 | Nicht nachgewiesen |
| Gesamtprodukt fertig | Nein |

### Was die Prüfung getan hat und was nicht

Die Prüfung hat keine neue Windows-, Playwright- oder End-to-End-Abnahme durchgeführt. Sie bestand aus Code- und Dokumentprüfung, einer Tk-API-Abfrage und Primärquellenrecherche. Die vorhandenen Testberichte wurden nicht als heutige Testläufe ausgegeben.

Im Rahmen dieser Baustartkorrektur gab es keine Codeänderung, keinen Service-Neustart und keine Änderung am Gemini-Prototypen.

### Zusammengehörige Quellen

- `/root/werkraum/docs/augen_haende_bridge/archiv/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-astra-planung-messages.jsonl` — Gesprächsprotokoll der Planung, keine Implementierungsabnahme.
- `/root/werkraum/docs/augen_haende_bridge/KAPSELN_UND_HAUHAUCS.md` — die vorherige Ableitung. Ihre Reihenfolge ist durch diese Prüfung korrigiert.
- `/root/werkraum/docs/systemdoku/76_augen_und_haende_bridge.md` — das Zielbild.
- `/root/werkraum/docs/systemdoku/77_worlddom_memory_seeds_wiedererweckung.md` — Erweiterungen und Portabilität.
- `/root/werkraum/docs/systemdoku/78_augen_und_haende_bauplan.md` — der historische Bauablauf mit korrigierter Geltung.
- `/root/werkraum/docs/augen_haende_bridge/archiv/originale/2026-09-19_BRIDGE_SKILL_ORIGINAL_VOR_BAUSTARTPRUEFUNG.md` — die wortgetreue Sicherung des alten globalen Skills.
- `/root/werkraum/_codex/skills/augen-haende-greenfield-builder/SKILL.md` — die Arbeitsweise für den Neubau.
- `/vps_root/werkraum_bilder/refferenzen/hand-auge-bridge-ref.jpg` — Daniels räumliche Referenz. In der Baustartprüfung hieß die Datei `h a bridge.jpg`; unter diesem Namen liegt sie heute nicht mehr im Ordner.

## Der falsche Bridge-Körper (Befund vom 2026-09-20)

Stand: Der Bau-Goal ist auf Daniels Wunsch pausiert. Das Produkt ist nicht abgenommen. Dieser Abschnitt verändert keinen laufenden Service und löscht keine Artefakte.

### Urteil

Der relevante Bauauftrag wurde verfehlt. Weitergebaut wurde eine technisch testbare, aber inhaltlich falsche EXE- und Surface-Schicht. Der vereinbarte erste nutzbare Körper wurde nicht geliefert. Er besteht aus einem einzelnen echten Terminal mit Fensterscanner, ohne Fake-Agenten und ohne Monster-Surface.

Daniels Bilanz: Außer der Dokumentation wurde nichts hinbekommen. Diese Einschränkung ist fair, und sie trifft auch die Dokumentation: Sie war selbst zu dicht, wiederholend und teilweise nicht ernsthaft genug als belastbarer Arbeitsvertrag.

### Was ausdrücklich verlangt war

- Ein echtes Programm als EXE, keine Homepage und keine große Ersatz-Surface.
- Als erster tragender Körper genau **ein** sauberes Terminal.
- Der Fensterscanner gehört an dieses Terminal, unten rechts, und öffnet die Auswahl erst bei Bedarf.
- Rauten erscheinen nur für tatsächlich vorhandene und gebundene Agenten.
- Keine vier Platzhalter-Terminals, keine Beziehungspfeil-Landschaft und keine vorgetäuschte Agentenpräsenz.

### Was stattdessen weitergetragen wurde

`/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py` enthielt weiterhin die alte Surface-Logik:

- ein großes, zentrales Overlay mit Raster und Beziehungspfeilen,
- voreingetragene Rauten für Codex, Gemini, Claude und Daniel,
- vier Terminalkarten,
- lokale Platzhalter für Regie, Mikrofon und Kamera.

Diese Logik wurde nicht als verdächtige Altlast entfernt oder quarantänisiert, sondern als Grundlage für den Greenfield-Körper behandelt. Die daraus gebaute G12-Lieferung ist deshalb kein akzeptierter Produktkörper, auch wenn sie unter Wine startet und technische Readback-Tests besteht.

### Ursache

Autonomie war nicht die Ursache. Auch ein eng betreuter Bau, Schritt für Schritt, hätte dieselbe Logik wiederholt, weil die falsche Quelle als Wahrheit verwendet wurde:

1. Vorhandener Code wurde als legitime Grundlage behandelt.
2. Die ausdrücklichen visuellen und funktionalen Vorgaben wurden nicht als Abbruchkriterium gegen diesen Code durchgesetzt.
3. Die Tests prüften Transport, Registry, Scanmarker und Binding-Readback. Sie prüften nicht, ob beim Öffnen exakt der Körper erscheint, den Daniel wollte.
4. Ein grüner technischer Teilbeleg wurde als Produktfortschritt gelesen.

Der Kern: Daniels Vorgaben wurden nicht als harte Quelle behandelt, sondern der vorhandene falsche Code.

### Warum die Fremdprüfung es nicht verhindert hat

Claude und Gemini haben technische Teilbereiche geprüft und reale Probleme in Transport, Idle-Verbindung, Namespace und Readback gefunden. Sie bekamen aber keinen erzwungenen Auftrag, die tatsächlich geöffnete EXE gegen Daniels sichtbaren Minimalvertrag abzunehmen.

Geprüft wurde überwiegend die Frage »Ist der neue Code technisch konsistent?« und nicht die Frage »Öffnet sich exakt das, was Daniel verlangt hat?«. Außerdem wurde die alte Surface als vorhandener Kontext präsentiert. Ein Reviewer, der nur Änderungen und technische Verträge liest, hinterfragt eine unveränderte falsche Grundlage nicht von selbst. Das erklärt, warum es durchrutschte. Es entschuldigt es nicht.

### Negative Tests

Ein Test war nicht nötig, um zu erkennen, dass vier Terminals falsch sind. Das stand bereits in den Anforderungen. Ein Negativtest hätte höchstens als zusätzlicher Sicherungszaun geholfen, nachdem die Anforderungen richtig verstanden waren. Die fehlenden Negativtests sind ein Symptom der eigentlichen Ursache: Die Vorgaben galten nicht als unmittelbare Bauwahrheit.

### Was tatsächlich erreicht wurde

Unter `/root/werkraum/augen_haende_bridge/` gibt es technische Artefakte: Relay, Registry, Scannerkern, read-only Binding, EXE-Bundle, Tests und Evidence-Strukturen. Sie beweisen einzelne technische Eigenschaften.

Sie beweisen nicht den verlangten nutzbaren Bridge-Körper. Insbesondere fehlen der Nachweis
- eines echten 1:1-Terminals,
- der gewünschten ersten EXE-Oberfläche,
- realer Agentenpräsenz statt Platzhalter-Rauten,
- einer vollständigen nativen Windows-Abnahme,
- der ChatGPT-, Claude- und Gemini-Körper in der Bridge.

Die G12-Lieferung `/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G12-win64-handoff.zip` ist ein forensisches Zwischenartefakt und keine Produktfreigabe.

### Lehre für die Wiederaufnahme

Das gilt zwingend:

- Daniels Anforderung und die sichtbare Referenz stehen über vorhandenem Code.
- Vorhandener UI-Code ist bei Widerspruch Altlast und kein Fundament.
- Der erste Start wird gegen die gewünschte Ansicht geprüft, bevor weitere Transport- oder Evidence-Schichten darauf gesetzt werden.
- »Technisch grün« ersetzt nie »inhaltlich richtig«.
- Ein Schritt-für-Schritt-Prozess ist nur sinnvoll, wenn der erste Schritt auf der richtigen Grundlage beginnt.
