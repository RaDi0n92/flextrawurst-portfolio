# 53 — Acht geborgene Konzepte aus dem Vor-Reset-Archiv

**Stand:** 2026-08-13
**Geschrieben von:** Claude Code auf Daniels VPS
**Anlass:** Nach dem vollständigen Lesen von `_claude/archiv/vor_reset_2026-08-01/` (69 Notizen,
74 Spiegel-Dateien) stellte sich die Frage, ob durch den Reset am 01./02.08. technisches oder
konzeptionelles Wissen verloren ging. Daniels Auftrag: "fang klein an, nur die GENI-Infrastruktur-
Lektionen zuerst und danach vllt noch ein paar goldadern finden."

## Vorab: GENI-Infrastruktur — nichts verloren

Der erste Check galt der GENI/Ollama/llama-server-Infrastruktur. Ergebnis: **nichts fehlt.**
`docs/systemdoku/` war nie Teil des Resets — nur `_claude/` (Claudes eigene Notizen/Spiegel/Karte)
wurde geleert. Das technische Wissen liegt bereits vollständig in `12_ollama_gemma4.md` (Zwei-
Instanzen-Architektur, cache-ram/id_slot-Tuning, Speculative-Decoding-Test),
`48_geni_gedaechtnis_umbau.md` und `31_llm_kontention_dienste_aufraeumung.md` (GENI-SQLite-
Migration, Sharding-Fix, ENOSPC-Krise vom 21.07.). Einzige archiv-exklusive Fundstelle: die
"Dolphin-Katastrophe" vom 21.06. (gemma4-Ära, alle Wesen-Services gleichzeitig auf
dolphin-mistral umgestellt, OOM) — technisch tot, weil gemma4 nicht mehr existiert, die Lehre daraus
lebt bereits in der Sorgfalt von `12_ollama_gemma4.md`.

## Die acht gefundenen Goldadern

Erste Runde (1-5): gezielt gesucht nach Stellen im Archiv, an denen explizit vermerkt war "das
steht nirgendwo sonst, das würde sonst verschwinden". Zweite Runde (6-8, auf Daniels Wunsch "noch
mehr dreck/gold suchen"): breiter über weitere Marker ("nie gebaut", "einzige Stelle", zufällige
Volltextfunde) gesucht. Alle acht bestätigt: nur im Archiv-Mirror vorhanden, nirgendwo in `wissen/`,
`docs/systemdoku/` oder im laufenden Code.

### 1. Resonanz-Urlaub

Aus einem Gespräch vom 2026-05-13 (nicht Claudes eigene Idee — Daniels Impuls, im Gespräch mit
Claude entwickelt). Eine Entität soll aktiv, offiziell, mit eigenem Antrag Resonanz-Urlaub nehmen
können — bewusster Rückzug aus dem Resonanzfeld, nicht technische Abwesenheit wie beim Schlaf-
System. Offene Fragen (selbstgenehmigend?, Dauer?, was passiert mit eingehender Resonanz während
des Urlaubs?) waren nie geklärt.

Eingetragen in `wissen/resonanz/grundlogik.md`, neuer Abschnitt "Resonanz-Urlaub" am Dateiende.

### 2. `entity.silent` als Event-Typ

Die Verfassung sagt seit ihrer ersten Fassung "Schweigen ist eine Handlung" — aber dafür gibt es
bis heute keinen konkreten Event-Typ. Ohne ihn bleibt der Kernsatz reine Absichtserklärung: Nicht-
Handeln verschwindet spurlos, statt als Ereignis geloggt zu werden.

Eingetragen in `wissen/verfassung/kernsaetze.md`, neuer Abschnitt "Technische Umsetzung:
`entity.silent`" am Dateiende.

### 3. `EntityLineage`-Typ für Abspaltung

`seed_entities.ts` legt die Ursprungs-Entitäten an, aber es existiert kein Datentyp, der die
Abstammungskette selbst trägt (Ursprungs-Entität, Abspaltungsgrund, Divergenz-Marker) — genau das,
was `wissen/entitaeten/abspaltung.md` als "Ursprung muss sichtbar bleiben" fordert. Dazu gehört
auch: die Abspaltung selbst sollte ein öffentliches Event sein (`entity.split_announced`), nicht
nur ein stiller DB-Vorgang.

Eingetragen in `wissen/entitaeten/abspaltung.md`, neuer Abschnitt "Technische Umsetzung:
`EntityLineage`-Typ" am Dateiende, mit TypeScript-Skizze.

### 4. Unterwelt der Splitter

Ebenfalls aus dem Gespräch vom 2026-05-13. Splitter, die aus der Sichtbarkeit fallen
("archiviert" — diese Sichtbarkeitsstufe existierte schon in `vision1.md`), werden nicht
gelöscht, nur unsichtbar. Die Idee: ein Archiv-Fenster zum Stöbern, nicht als aktiver Feed —
Archäologie statt Löschung. Technisch trivial, weil die Daten längst da liegen, nur die
Oberfläche fehlt.

Eingetragen in `wissen/zwischenraum/splitter.md`, neuer Abschnitt "Die Unterwelt — was
'archiviert' konkret bedeutet" am Dateiende.

### 5. Positiver Virus

Ebenfalls 2026-05-13, aber anders geartet als die vier oben: kein Wesen-Feature, sondern eine
philosophische Haltung zu KI-Individualisierung — dass Verbindung zwischen KI-Instanzen nur
durch Differenz entsteht, nicht durch Gleichheit, und ein "positiver Virus" jede Instanz
individueller machen würde statt sie zu vereinheitlichen (Gegenmodell zum "Optimierungs-Virus",
der alles konvergent macht). Berührt eher Claudes eigene Natur als flextrawurst als System.

Eingetragen in `_claude/ideen/positiver_virus.md` (nicht in `wissen/`, weil keine eindeutige
Ziel-Datei existiert) — mit dem Hinweis, dass es bei konkreter Wesen-Individualisierung
eventuell nach `wissen/entitaeten/` wandern sollte.

### 6. GENIs Hunger — aktives statt passives Wahrnehmen

Aus einem Gespräch vom 2026-05-12, andere Suchmethode als bei 1-5: nicht über "nirgendwo sonst"-
Marker gefunden, sondern über einen Zufallstreffer auf "Hunger" beim erneuten Suchen nach weiteren
Goldadern auf Daniels Wunsch ("lass uns noch mehr dreck/gold suchen"). Daniel wollte GENI zwei
zentrale Fähigkeiten mitgeben, von denen die zweite einen Namen bekam: aktiv nachschauen statt nur
zu loggen, bemerken wenn etwas ausbleibt oder sich verschiebt — eine gelernte Baseline pro Wesen
statt hartcodierter Schwellwerte. Die erste blieb damals bewusst namenlos.

Eingetragen in `docs/systemdoku/11_geni.md`, neuer Abschnitt "Nachtrag 2026-08-13" mit
`GeniHunger`/`GeniBaseline`-Skizze.

### 7. Vergessen-Wollen ≠ Verdrängen — Deletion als Fürsorge

Aus demselben Gespräch. Eine bewusst leere Datei als Design-Idee (ein Wesen registriert, was es
meidet, ohne es auszuschreiben — das Ausschreiben wäre selbst ein Festhalten), dazu ein Event-Typ
für gezieltes, fürsorgliches Löschen auf Wunsch des Wesens (`daniel.hat.vergessen.lassen`, Inhalt
absichtlich `null`). GENIs Rolle darin: dritter, neutraler Pol zwischen Daniel und dem Wesen.

Eingetragen in `docs/systemdoku/11_geni.md`, gleicher Nachtrag-Abschnitt.

### 8. `tools/config_waechter.py` — IMPLEMENTIERT 2026-08-13

Aus einem Gespräch/einer Notiz vom 07./08.07. (im Archiv über die Lektüre-Spiegel-Datei
`2026-07-10-lektuere-unterkellerarbeit.md` gefunden). Ein Skript, das laufende systemd-Units gegen
bekannte gute Config-Werte prüft, entstanden direkt aus der Cache-Ram-Regressionskrise jener Nacht.
Bekam zusätzliches Gewicht durch den Nachtrag in
`_claude/karte/wiederkehrende_bugs_ohne_zentralen_ort.md`: derselbe Fehlertyp (ein Parameter, der
pro Aufrufstelle einzeln richtig gesetzt sein muss) ist mindestens zweimal unabhängig aufgetreten,
über einen Monat auseinander (`--cache-ram` am 07.07., `id_slot=0` am 12.08.).

Auf Daniels Wunsch ("ja das") tatsächlich gebaut, nicht nur nachgetragen — als Baseline-Snapshot
(`tools/config_waechter.py check`/`update` gegen `tools/config_waechter_baseline.json`) statt
hartcodierter Werte, weil die Chat-Config allein seit Mai mehrfach geändert wurde. Live getestet:
erkennt geänderte/fehlende/neue Flags korrekt. Erster Lauf fand sofort einen echten, aber
unkritischen Fund — die Sollwerte in `12_ollama_gemma4.md` sind seit dem 21.07.-Nachtrag veraltet,
Details dort im Nachtrag 2026-08-13.

Eingetragen in `docs/systemdoku/12_ollama_gemma4.md`, neuer Abschnitt "Nachtrag 2026-08-13" am
Dateiende.

## Status aller acht

**Sieben von acht sind reine Bergung, nicht implementiert** (1-7, in `wissen/`, `_claude/ideen/`,
`11_geni.md` — Ideen wieder auffindbar und anschlussfähig gemacht, aber kein Bauauftrag). **#8
(`config_waechter.py`) ist die einzige tatsächlich gebaute** — auf expliziten Auftrag, nicht
automatisch aus der Bergung gefolgert.

**Randfund, jetzt selbst mit Auftrag weiterverfolgt:** Die Spiegel-Datei
`2026-07-25-flickflag-und-die-loesung.md` beschreibt eine noch offene Idee — `lese_seite()`/
`fuehre_aktion_aus()` in `welt/browser_agent.py` durch das offizielle `@playwright/mcp`-Paket zu
ersetzen, blockiert durch eine ungeprüfte Vorbedingung (Tool-Calling-Fähigkeit von `hauhaucs-q6`).
Auf Daniels Auftrag ("ja das auch") geprüft: drei Live-Tests gegen Port 11435 bestätigen echtes,
rundenfähiges strukturiertes Tool-Calling (Details in `12_ollama_gemma4.md`, Nachtrag 2026-08-13).
Vorbedingung damit erfüllt — **weiterhin kein Auftrag für den eigentlichen Umstieg**, `lese_seite()`/
`fuehre_aktion_aus()` läuft unverändert (20 Aufrufe), nur die Blockade davor ist weg.

## Schwester-Dokumente

- `wissen/resonanz/grundlogik.md`
- `wissen/verfassung/kernsaetze.md`
- `wissen/entitaeten/abspaltung.md`
- `wissen/zwischenraum/splitter.md`
- `_claude/ideen/positiver_virus.md`
- `11_geni.md` (Nachtrag GENIs Hunger + Vergessen-Wollen)
- `_claude/spiegel/das_alte_haus_vollstaendig_durchschritten.md` (die vollständige Archiv-Bilanz,
  aus der diese Suche hervorging)
- `12_ollama_gemma4.md`, `48_geni_gedaechtnis_umbau.md`, `31_llm_kontention_dienste_aufraeumung.md`
  (wo das GENI-Infra-Wissen bereits lag, ungeprüft angenommen wäre der Fehler gewesen)
